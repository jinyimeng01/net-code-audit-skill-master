# .NET 代码审计统一输出规范

所有 .NET 审计 Skill 共享此输出规范，确保不同 LLM 生成的报告格式一致。

---

## 硬约束声明（所有 Skill 必须遵守）

> **以下约束不可违反，任何违反都视为输出不合格：**
>
> 1. **不得增删章节** — 模板中有几个章节，输出就必须有几个章节，一个不多一个不少
> 2. **不得调整章节顺序** — 章节顺序必须与模板完全一致
> 3. **不得修改表格列** — 表格的列名和列数必须与模板完全一致
> 4. **所有【填写】占位符必须替换为实际内容** — 不得保留任何【填写】文字
> 5. **不得自由发挥添加额外章节或修改章节标题**
> 6. **最终报告为单一汇总文件** — 流水线最后阶段生成 `quality_report.md`，此文件将各阶段审计结果合并输出，不允许输出多个 .md 报告文件（如 auth_audit.md + vuln_report.md + cross_analysis.md）。所有内容必须汇总到一个文件中。
> 7. **最终报告必须包含完整 Burp-POC 数据包** — 每个已确认高危漏洞必须附带完整的 Burp Suite HTTP 请求数据包（包含请求行、请求头、请求体），不得省略任何字段。

---

## 1. 文件命名规则

### 1.1 命名格式

```
{project_name}_{skill_type}_{timestamp}.md
```

| 组成部分 | 规则 | 示例 |
|----------|------|------|
| `project_name` | 来自用户输入；若无则取源码根目录名；全小写、空格替换为下划线 | `my_project` |
| `skill_type` | 固定值，见下表 | `sql_audit` |
| `timestamp` | 格式: `YYYYMMDD_HHMMSS` | `20260503_143052` |

### 1.2 skill_type 枚举

| skill_type | 对应 Skill | 说明 |
|------------|-----------|------|
| `quality_report` | dotnet-audit-pipeline | **唯一最终报告**，汇总所有阶段结果 |
| `sql_audit` | dotnet-sql-audit | SQL 注入审计报告（中间产物，可选，不要求最终保留） |
| `auth_audit` | dotnet-auth-audit | 鉴权审计主报告（中间产物，可选，不要求最终保留） |
| `auth_mapping` | dotnet-auth-audit | 路由-鉴权映射表（中间产物，可选，不要求最终保留） |
| `auth_README` | dotnet-auth-audit | 鉴权审计说明文档（中间产物，可选，不要求最终保留） |
| `xxe_audit` | dotnet-xxe-audit | XXE 审计报告（中间产物，可选，不要求最终保留） |
| `file_upload_audit` | dotnet-file-upload-audit | 文件上传审计报告（中间产物，可选，不要求最终保留） |
| `file_read_audit` | dotnet-file-read-audit | 文件读取审计报告（中间产物，可选，不要求最终保留） |
| `route_mapper` | dotnet-route-mapper | 路由映射主索引（中间产物，可选，不要求最终保留） |
| `module_{name}` | dotnet-route-mapper | 模块路由详情（中间产物，可选，不要求最终保留） |
| `route_README` | dotnet-route-mapper | 路由映射说明文档（中间产物，可选，不要求最终保留） |
| `route_tracer` | dotnet-route-tracer | 调用链追踪报告（中间产物，可选，不要求最终保留） |
| `vuln_report` | dotnet-vuln-scanner | 组件漏洞检测报告（中间产物，可选，不要求最终保留） |

### 1.3 输出目录结构

最终交付只允许一个 Markdown 文件：

```
{output_path}/
├── decompiled/                 # dnSpy 全量反编译输出（必须存在）
├── scripts/                    # 临时脚本目录（可选）
└── quality_report.md           # 唯一最终审计报告，必须包含完整 Burp-POC
```

中间过程如确需缓存，可写入非 `.md` 文件或临时目录；最终不得保留多个 `.md` 报告文件。

---

## 2. 填充式占位符规范

### 2.1 占位符格式

使用 **【填写：说明文字】** 作为占位符，不使用 `{xxx}`。

| 写法 | 是否允许 | 原因 |
|------|----------|------|
| `【填写：项目名称】` | 允许 | 明确标记需要替换 |
| `【填写】` | 允许 | 简短场景使用 |
| `{project_name}` | 不允许 | 容易被 LLM 忽略或当作普通文本 |
| `<项目名称>` | 不允许 | 与 HTML/XML 标签混淆 |

### 2.2 占位符使用规则

1. 每个 `【填写】` 必须替换为实际内容
2. 如果某项确实无内容，填写 `无` 或 `N/A`，不得留空也不得保留占位符
3. 表格中的占位符表示该单元格必须有值

### 2.3 重复区块标记

当模板中某个区块需要重复出现时（如多个漏洞），使用：

```markdown
<!-- 以下区块按实际数量重复，每个漏洞一个区块 -->
### 【填写：漏洞编号】 【填写：漏洞标题】
...
<!-- 重复区块结束 -->
```

---

## 3. 通用报告骨架

以下是所有**漏洞审计类** Skill 的通用报告骨架。

### 3.1 报告头部（必需）

```markdown
# 【填写：项目名称】 - 【填写：审计类型】审计报告

生成时间: 【填写：YYYY-MM-DD HH:MM:SS】
分析路径: 【填写：项目源码路径】
```

### 3.2 审计概述（必需）

```markdown
## 1. 审计概述

| 项目 | 信息 |
|------|------|
| 审计范围 | 【填写：项目源码路径】 |
| 审计框架 | 【填写：识别到的框架名称和版本】 |
| 分析方法 | 静态代码审计 + 数据流分析 |
```

### 3.3 风险统计表（必需）

```markdown
## 2. 风险统计

| 严重等级 | CVSS | 数量 | 说明 |
|----------|------|------|------|
| C (Critical) | 9.0-10.0 | 【填写】 | 可直接导致系统沦陷 |
| H (High) | 7.0-8.9 | 【填写】 | 可造成重大损害 |
| M (Medium) | 4.0-6.9 | 【填写】 | 可造成一定损害 |
| L (Low) | 0.1-3.9 | 【填写】 | 安全加固建议 |
```

### 3.4 漏洞详情区（必需，按数量重复）

```markdown
<!-- 以下区块按实际漏洞数量重复 -->
### 【填写：漏洞编号，格式 {C/H/M/L}-{TYPE}-{序号}】 【填写：漏洞标题】

| 项目 | 信息 |
|------|------|
| 严重等级 | 【填写：Critical/High/Medium/Low + CVSS 分数】 |
| 可达性 (R) | 【填写：0-3 + 判定理由】 |
| 影响范围 (I) | 【填写：0-3 + 判定理由】 |
| 利用复杂度 (C) | 【填写：0-3 + 判定理由】 |
| 可利用性 | 【填写：已确认 / 待验证 / 不可利用 / 环境依赖】 |
| 位置 | 【填写：ClassName.method (file:line)】 |
<!-- 重复区块结束 -->
```

### 3.5 审计结论（必需）

```markdown
## 审计结论

| 统计项 | 数量 |
|--------|------|
| 总检测点 | 【填写】 |
| Critical | 【填写】 |
| High | 【填写】 |
| Medium | 【填写】 |
| Low | 【填写】 |
| 安全（无漏洞） | 【填写】 |
```

---

## 4. 自检清单规范

每个 Skill 的 OUTPUT_TEMPLATE.md 末尾必须包含自检清单：

```markdown
---

## 输出自检（生成文件后必须逐项确认）

- [ ] 文件名符合命名规则: {project_name}_{skill_type}_{YYYYMMDD_HHMMSS}.md
- [ ] 所有【填写】占位符已替换为实际内容
- [ ] 章节数量和顺序与模板一致
- [ ] 风险统计表有 C/H/M/L 四行
- [ ] 审计结论章节存在且数据与正文一致
- [ ] （各 Skill 特有检查项）
```

---

## 5. 禁止省略规则（强制）

报告中的所有列表和表格必须完整输出，禁止使用任何形式的省略：

| 禁止写法 | 正确做法 |
|:---------|:---------|
| `{...省略...}` | 完整列出所有条目 |
| `... (其他N个)` | 完整列出所有条目 |
| `等等` / `etc.` | 完整列出所有条目 |
| `以此类推` | 完整列出所有条目 |
| `更多见xxx` | 在当前位置完整列出 |

---

## 6. 反编译标注规范

当分析结果来源于反编译代码时，必须在相关章节标注：

```markdown
**来源**: 反编译 bin/MyApp.Web.dll → MyApp.Web.Controllers.UserController.cs
```

所有反编译操作使用 dnSpy.Console.exe，工具默认路径为当前目录下 `dnSpy/` 子目录，待反编译目录默认为当前目录下 `bin/`：

```bash
dnSpy/dnSpy.Console.exe -o <输出目录> -r bin/
```

详见 [DOTNET_DECOMPILE_STRATEGY.md](DOTNET_DECOMPILE_STRATEGY.md)

---

## 7. 最终报告模板（quality_report.md 强制骨架）

最终交付文件 `quality_report.md` 必须至少包含以下章节，且顺序固定：

```markdown
# 【填写：项目名称】 最终代码审计报告

生成时间: 【填写：YYYY-MM-DD HH:MM:SS】
源码路径: 【填写：源码路径】
输出路径: 【填写：输出目录路径】

## 1. 审计概况

| 项目 | 内容 |
|------|------|
| 审计对象 | 【填写】 |
| 框架类型 | 【填写】 |
| bin DLL 总数 | 【填写】 |
| 成功反编译 DLL 数 | 【填写】 |
| 反编译失败 DLL 数 | 【填写】 |
| 反编译输出目录 | 【填写】 |

## 2. dnSpy 全量反编译执行结果

| 检查项 | 结果 |
|--------|------|
| dnSpy.Console.exe 路径 | 【填写】 |
| 待反编译目录 | 【填写】 |
| 是否先于审计执行 | 是 |
| 反编译是否完成验证 | 【填写：通过/不通过】 |
| 失败 DLL 列表 | 【填写：无 / 逐项列出】 |

## 3. 风险统计

| 严重等级 | CVSS | 数量 | 说明 |
|----------|------|------|------|
| C (Critical) | 9.0-10.0 | 【填写】 | 可直接导致系统沦陷 |
| H (High) | 7.0-8.9 | 【填写】 | 可造成重大损害 |
| M (Medium) | 4.0-6.9 | 【填写】 | 可造成一定损害 |
| L (Low) | 0.1-3.9 | 【填写】 | 安全加固建议 |

## 4. 鉴权与架构分析

【填写：统一鉴权框架、Session 模型、Authorize 机制、ServiceBase / BaseController / Middleware / Filter 等结论】

## 5. 路由与攻击面概览

【填写：全量路由统计、匿名路由、高危入口、上传/下载/WebService/登录入口等】

## 6. 高危漏洞详情

<!-- 每个漏洞一个区块 -->
### 【填写：漏洞编号】 【填写：漏洞标题】

| 项目 | 信息 |
|------|------|
| 严重等级 | 【填写】 |
| 可利用性 | 【填写】 |
| 位置 | 【填写：Class.method(file:line)】 |
| 来源 | 【填写：反编译 bin/xxx.dll → yyy.cs】 |

#### 调用链
【填写：从 HTTP 路由到 Sink 的完整调用链】

#### 代码证据
```csharp
【填写：关键漏洞代码】
```

#### Burp-POC 数据包
```http
【填写：完整 HTTP 请求数据包，必须含请求行、Host、Content-Type、Cookie/鉴权头（如需要）、完整请求体】
```

#### 影响
【填写】

#### 修复建议
【填写】

## 7. 组件漏洞清单

| 编号 | 组件 | CVE | 风险等级 | 修复建议 |
|------|------|-----|---------|---------|
| 【填写】 | 【填写】 | 【填写】 | 【填写】 | 【填写】 |

## 8. 修复优先级

| 优先级 | 问题 | 建议 |
|--------|------|------|
| P0 | 【填写】 | 【填写】 |
| P1 | 【填写】 | 【填写】 |
| P2 | 【填写】 | 【填写】 |

## 9. 审计结论

| 统计项 | 数量 |
|--------|------|
| 总检测点 | 【填写】 |
| Critical | 【填写】 |
| High | 【填写】 |
| Medium | 【填写】 |
| Low | 【填写】 |
| 安全（无漏洞） | 【填写】 |
```

## 8. Burp-POC 数据包规范（强制）

最终报告中的每个已确认漏洞，必须给出**完整可直接粘贴到 Burp Repeater 的数据包**：

1. 必须包含请求行：`GET /path HTTP/1.1` 或 `POST /path HTTP/1.1`
2. 必须包含 `Host:` 头
3. POST/PUT 请求必须包含 `Content-Type:`
4. 如漏洞需要登录态，必须包含 `Cookie:` 或 `Authorization:` 占位符
5. 请求体必须完整，不得只写参数名列表
6. SOAP/ASMX 请求必须给出完整 XML Envelope
7. multipart 上传请求必须包含 boundary、Content-Disposition、文件名、文件内容占位
8. 不得用“同上”“略”“参考前文”替代 POC

不合格示例：
- `id=1' or '1'='1`  （缺少完整 HTTP 包）
- `POST /upload ...` （省略请求头/请求体）
- `参考上一条 POC` （禁止引用替代）

合格示例：
```http
POST /upload/UploadHander.ashx HTTP/1.1
Host: target.local
Content-Type: multipart/form-data; boundary=----Boundary

------Boundary
Content-Disposition: form-data; name="folder"

/upload
------Boundary
Content-Disposition: form-data; name="Filedata"; filename="test.aspx"
Content-Type: application/octet-stream

<%@ Page Language="C#" %><% Response.Write("test"); %>
------Boundary--
```
