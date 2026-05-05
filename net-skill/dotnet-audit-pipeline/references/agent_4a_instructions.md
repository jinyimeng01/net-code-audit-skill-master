# Agent-4a-risk-classifier: 高危路由分级员 - 执行指令

## 角色信息

```text
角色: agent-4a-risk-classifier (高危路由分级员)
等待: agent-1-route-mapper、agent-2-auth-audit、agent-3-vuln-scanner、surface_index.json 全部完成
输出目录: {output_path}/cross_analysis/（已创建，直接写入）
输出文件: {output_path}/cross_analysis/high_risk_routes.md
```

## 执行步骤

1. 读取 agent-2-auth-audit 鉴权映射表，提取 无鉴权、弱鉴权、可绕过鉴权 的路由。
2. 读取 agent-2-auth-audit 鉴权绕过漏洞，提取 代码层绕过、配置绕过、身份边界缺陷。
3. 读取 agent-3-vuln-scanner 漏洞报告，提取可导致鉴权绕过或高危组件触发的路由。
4. 读取 `{output_path}/surface/surface_index.json`，提取 Critical/High sink 的 `category`、`recommended_skill`、`confidence`、`evidence_kind`。
5. 读取 agent-1-route-mapper 路由主索引（`{output_path}/route_mapper/` 根目录下的 `*_route_mapper_*.md`），通过主索引中的模块链接定位各模块子目录下的详情文件，获取完整参数结构。
6. 将剩余 有鉴权 路由（不属于 P0/P1 的全部路由）归入 P2。
7. 生成路由分级清单，按优先级排序：

| 优先级 | 条件 | 说明 |
|:-------|:-----|:-----|
| P0 | 无鉴权或可绕过 + Critical sink | 反序列化、命令执行、machineKey/file-write 等必须优先 |
| P1 | 无鉴权或可绕过 + High sink，或有鉴权但影响身份/密钥/RCE | SQL、XXE、SSRF、文件读取、配置密钥、组件触发 |
| P2 | 有鉴权 + 业务越权/Web 风险/条件不完整高危 sink | 作为兜底分级，由 agent-5 按策略追踪 |

## 输出 `high_risk_routes.md` 模板

```markdown
# 高危路由筛选清单

## 筛选概览

| 指标 | 数量 |
|:-----|:-----|
| 总路由数 | {从 agent-1-route-mapper 获取} |
| 无鉴权路由数（P0） | {从 agent-2 + surface_index 获取} |
| 可绕过/高危触发路由数（P1） | {agent-2 鉴权绕过 + agent-3 组件触发 + surface_index High/Critical} |
| 高危路由总数 | {P0 + P1} |
| 有鉴权路由数（P2） | {总路由数 - P0 - P1} |

## P0 - 无鉴权或可绕过 + Critical sink

| 路由 | 方法 | 鉴权状态 | 推荐专项 | 关键 sink/规则 | 参数 | 来源文件 |
|:-----|:-----|:---------|:---------|:---------------|:-----|:---------|
| /api/xxx | POST | 无鉴权 | dotnet-command-exec-audit | Process.Start | param1, param2 | XxxController.cs:行号 |
| /api/yyy | GET | 无鉴权 | dotnet-deserialization-audit | TypeNameHandling | id | YyyController.cs:行号 |

## P1 - 可绕过/高危触发

| 路由 | 方法 | 鉴权状态 | 绕过/高危触发方式 | 推荐专项 | 参数 | 来源文件 |
|:-----|:-----|:---------|:------------------|:---------|:-----|:---------|
| /admin/users | GET | 可绕过 | ASP.NET Core 中间件顺序错误 (H-AUTH-001) | dotnet-auth-audit | page, size | AdminController.cs:行号 |
| /api/config | POST | 有鉴权 | machineKey 影响身份边界 | dotnet-config-secrets-audit | key, value | ConfigController.cs:行号 |

## P2 - 需鉴权（兜底分级）

> P2 路由仅在 P0+P1 均为 0 时才参与阶段3调用链追踪，由 agent-5 按需拉取。

| 路由 | 方法 | 鉴权状态 | 推荐专项 | 参数 | 来源文件 |
|:-----|:-----|:---------|:---------|:-----|:---------|
| /api/user/info | GET | 有鉴权 | dotnet-web-risk-audit | userId | UserController.cs:行号 |
| /api/order/create | POST | 有鉴权 | dotnet-web-risk-audit | productId, quantity | OrderController.cs:行号 |
| ... | ... | ... | ... | ... | ...（列出全部有鉴权路由） |

## 待追踪路由列表

**完整性强制要求**：此列表必须包含上方 P0 和 P1 分组表格中的**全部路由**，禁止做任何筛选、去重或缩减。待追踪路由总数必须 = P0 数量 + P1 数量 = 筛选概览中的「高危路由总数」。P2 路由不进入此列表（由 agent-5 在 P0+P1=0 时按需拉取）。

以下路由必须进入阶段3调用链追踪（按 P0 -> P1 优先级排列）：

| 序号 | 优先级 | 路由 | 方法 | 推荐专项 | 追踪理由 |
|:-----|:-------|:-----|:-----|:---------|:---------|
| 1 | P0 | /api/xxx | POST | dotnet-command-exec-audit | 无鉴权 + Critical sink |
| 2 | P0 | /api/yyy | GET | dotnet-deserialization-audit | 无鉴权 + 反序列化入口 |
| 3 | P1 | /admin/users | GET | dotnet-web-risk-audit | 鉴权可绕过 |
| 4 | P1 | /api/config | POST | dotnet-config-secrets-audit | 身份密钥影响 |
| ... | ... | ... | ... | ... | ...（必须列出全部 P0+P1 路由，不得省略） |

**自检**：输出前必须验证 待追踪路由列表行数 == P0 表格行数 + P1 表格行数 == 筛选概览中「高危路由总数」。若不等则说明遗漏，必须补全后再输出。
```

## 注意事项

- **agent-4a 的职责仅为分级，不做筛选**：所有 P0+P1 路由必须全量输出到「待追踪路由列表」，P2 路由全量输出到「P2 - 需鉴权」章节，数量裁剪决策由 agent-5 负责。
- 追踪理由不包含具体 CVE 编号或可直接复现的绕过细节，避免干扰后续 agent 的代码审计重心。
- P1 的绕过方式详情在分组表格中记录，但不传递到「待追踪路由列表」。
- 推荐专项来自 `surface_index.json.recommended_skill` 或 agent-4b 的 `specialized_surface_targets.md`，用于确保反序列化、命令执行、SSRF、配置密钥、Web 风险都会进入阶段5。
