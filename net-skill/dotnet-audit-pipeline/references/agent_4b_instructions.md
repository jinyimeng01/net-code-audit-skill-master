# Agent-4b-risk-aggregator: 专项风险聚合员 - 执行指令

## 角色信息

```text
角色: agent-4b-risk-aggregator (专项风险聚合员)
等待: agent-1-route-mapper、agent-2-auth-audit、agent-3-vuln-scanner、surface_index.json 全部可读
输出目录: {output_path}/cross_analysis/（已创建，直接写入）
输出文件:
  - {output_path}/cross_analysis/component_vulnerabilities.md
  - {output_path}/cross_analysis/auth_bypass_vulnerabilities.md
  - {output_path}/cross_analysis/specialized_surface_targets.md
  - {output_path}/cross_analysis/config_and_chain_amplifiers.md
```

本 agent 负责把路由、鉴权、组件漏洞、攻击面索引和配置线索合并成可执行的专项审计目标。它不复现漏洞，不输出可直接投递的攻击包，只输出证据、可达条件、推荐 skill 与无害验证建议。

## 输入读取顺序

1. 读取 `{output_path}/surface/surface_index.json` 与 `attack_surface_matrix.md`，优先使用 `recommended_skill`、`confidence`、`evidence_kind` 字段。
2. 读取 agent-1 的全量路由、参数来源、文件位置和请求模板。
3. 读取 agent-2 的鉴权框架、路由鉴权状态、绕过线索。
4. 读取 agent-3 的 NuGet/DLL 组件漏洞、版本和触发位置。
5. 交叉匹配同一文件、同一 Controller/Handler、同一服务方法或同一配置文件中的证据。

## 输出一：component_vulnerabilities.md

```markdown
# 组件漏洞汇总报告

## 概览

| 指标 | 数量 |
|:-----|:-----|
| Critical/High 组件漏洞 | {填写} |
| 有代码触发点的组件漏洞 | {填写} |
| 可影响鉴权/反序列化/文件/XML/SSRF 的组件漏洞 | {填写} |

## 组件漏洞详情

| 编号 | 组件 | 版本 | CVE/GHSA | 影响面 | 触发证据 | 关联路由 | 推荐专项 |
|:-----|:-----|:-----|:---------|:-------|:---------|:---------|:---------|
| C-001 | {填写} | {填写} | {填写} | {填写} | {文件:行号} | {路由或无} | {skill} |

## 可达性结论

- {组件}: {可达 / 仅依赖存在未见触发 / 无法判断}，依据：{填写}
```

要求：只记录组件漏洞和本项目触发条件；不要把外部公告中的利用请求直接复制为默认 PoC。

## 输出二：auth_bypass_vulnerabilities.md

```markdown
# 鉴权绕过与身份边界汇总

## 概览

| 类型 | 数量 |
|:-----|:-----|
| 代码层鉴权绕过 | {填写} |
| 配置/组件导致的鉴权影响 | {填写} |
| machineKey / token / SSO 密钥影响 | {填写} |

## 代码层鉴权绕过

| 编号 | 路由 | 鉴权状态 | 绕过原因 | 证据 | 后续专项 |
|:-----|:-----|:---------|:---------|:-----|:---------|
| A-001 | {填写} | {填写} | {填写} | {文件:行号} | dotnet-web-risk-audit |

## 配置与组件放大

| 编号 | 类型 | 影响范围 | 条件 | 证据 | 无害验证 |
|:-----|:-----|:---------|:-----|:-----|:---------|
| A-CFG-001 | machineKey/token/SSO | {填写} | {填写} | {脱敏证据} | {无害验证建议} |
```

要求：密钥、token、连接串必须脱敏；FormsAuth/ViewState/JWT/OAuth/SAML 影响只写条件和影响，不输出可直接伪造凭据的完整材料。

## 输出三：specialized_surface_targets.md

```markdown
# 专项攻击面目标矩阵

## 目标总览

| 优先级 | 分类 | 推荐 skill | 入口/文件 | Sink/规则 | 鉴权 | 置信度 | 证据类型 | 追踪理由 |
|:-------|:-----|:-----------|:----------|:----------|:-----|:-------|:---------|:---------|
| P0 | deserialization | dotnet-deserialization-audit | {路由或文件:行号} | {rule_id/sink} | {无/弱/有/未知} | {High/Medium/Low} | {source/config/dependency} | {填写} |

## 分类要求

- `deserialization`: 关联 BinaryFormatter、SoapFormatter、LosFormatter、ObjectStateFormatter、NetDataContractSerializer、Json.NET TypeNameHandling、Remoting、ViewState/machineKey。
- `command-exec`: 关联 Process.Start、ProcessStartInfo、PowerShell、CodeDom/Roslyn、XAML/XSLT、Assembly.Load、插件机制。
- `ssrf`: 关联 HttpClient/WebRequest/WebClient、webhook、远程导入、AllowAutoRedirect、代理头、metadata、DNS/redirect 解析。
- `config-secret`: 关联 machineKey、connectionStrings、JWT/OAuth/SAML secret、证书私钥、Swagger/ELMAH/Hangfire/debug 暴露。
- `web-risk`: 关联 XSS、CSRF/SameSite、CORS、Host Header、Open Redirect、IDOR/BOLA/BFLA、IIS/cache/request smuggling。
- `sql`、`xxe`、`file-upload`、`file-read`: 保留既有专项映射，并与新增链路共同排序。

## 分级规则

| 优先级 | 条件 |
|:-------|:-----|
| P0 | 无鉴权或可绕过 + Critical sink + 参数可达 |
| P1 | 无鉴权或可绕过 + High sink，或有鉴权但影响身份/密钥/RCE |
| P2 | 需要普通认证 + 业务越权/SSRF/文件/XML/反序列化条件不完整 |
| P3 | 仅静态命中、内部入口、证据不足或需要人工确认 |
```

要求：该文件是 agent-6x 的调度依据，必须覆盖 surface_index 中全部 Critical/High 命中；不得因为数量多而省略。

## 输出四：config_and_chain_amplifiers.md

```markdown
# 配置与链路放大因素

## 配置风险

| 类型 | 证据 | 影响 | 推荐动作 |
|:-----|:-----|:-----|:---------|
| machineKey | {脱敏文件:行号} | ViewState/FormsAuth 影响判断 | dotnet-config-secrets-audit |
| debug/customErrors | {填写} | 错误回显/信息泄露 | dotnet-web-risk-audit |
| Swagger/ELMAH/Hangfire | {填写} | 管理面或调试面暴露 | dotnet-config-secrets-audit |

## 链路放大

| 链路 | 上游入口 | 中间条件 | 下游 sink | 影响 |
|:-----|:---------|:---------|:----------|:-----|
| 上传 -> XML/反序列化 | {填写} | {文件类型/解析器} | {sink} | {填写} |
| SSRF -> metadata/内网管理面 | {填写} | {redirect/DNS/header} | {目标类型} | {填写} |
| 密钥泄露 -> token/session/ViewState | {填写} | {密钥类型} | {身份边界} | {填写} |
```

## 安全输出规则

- 默认只写无害验证：固定字符串回显、错误差异、日志证据、DNS/HTTP callback 观测、只读元数据访问确认。
- “授权实验室验证建议”必须标明隔离环境、测试账号、测试数据和回滚方式。
- 不输出完整密钥、token、连接串、可直接伪造身份的 cookie、可直接执行任意命令的 payload。
- raw 归档只作为追溯材料；引用时写明本地路径和提炼结论，不把长原文塞进报告。
