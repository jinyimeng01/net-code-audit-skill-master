# 静师傅 .NET 攻防代码审计 Skill

`net-skill` 是一套面向 .NET Web / IIS / WCF / 反编译项目的综合安全审计 skill 集合。它以 [dotnet-offsec-audit](net-skill/dotnet-offsec-audit/SKILL.md) 为总控入口，以 [dotnet-audit-pipeline](net-skill/dotnet-audit-pipeline/SKILL.md) 为流水线编排，覆盖路由、鉴权、组件漏洞、调用链追踪和 9 类专项漏洞审计，最终输出唯一、可复核、默认无害验证的 `quality_report.md`。

适用范围：

- ASP.NET WebForms、MVC、Web API、ASP.NET Core、WCF、IIS 发布包。
- 源码项目、只有 `bin/` 或 DLL/EXE 的项目、dnSpy 反编译结果。
- 授权源码审计、防守加固复核、红队实验室验证。

安全边界：

- 默认报告只输出无害验证证据和修复建议。
- 涉及命令执行、反序列化、SSRF、凭据伪造、ViewState/machineKey 的内容必须遵守 [REDTEAM_LAB_BOUNDARY.md](net-skill/shared/REDTEAM_LAB_BOUNDARY.md)。
- 不默认生成可直接用于未授权目标的武器化 payload、完整密钥、token、连接串或可伪造身份的材料。

## 核心能力

| 能力 | 覆盖内容 | 入口 skill |
|:-----|:---------|:----------|
| 总控编排 | 授权边界、反编译、攻击面索引、专项调度、最终报告 | [dotnet-offsec-audit](net-skill/dotnet-offsec-audit/SKILL.md) |
| 全链路流水线 | agent 分阶段执行、质量门、唯一 `quality_report.md` | [dotnet-audit-pipeline](net-skill/dotnet-audit-pipeline/SKILL.md) |
| 路由与参数 | MVC/Web API/Core/WebForms/WCF 路由、参数来源、请求模板 | [dotnet-route-mapper](net-skill/dotnet-route-mapper/SKILL.md) |
| 鉴权与越权 | FormsAuth、Identity、JWT、OAuth/OIDC、Windows Auth、Membership、IDOR | [dotnet-auth-audit](net-skill/dotnet-auth-audit/SKILL.md) |
| 调用链追踪 | 从 Controller/Page/Handler/WCF 到 SQL、文件、XML、命令等 sink | [dotnet-route-tracer](net-skill/dotnet-route-tracer/SKILL.md) |
| 组件漏洞 | NuGet、DLL、配置中的依赖与 CVE/GHSA 触发条件 | [dotnet-vuln-scanner](net-skill/dotnet-vuln-scanner/SKILL.md) |
| SQL 注入 | ADO.NET、Entity Framework、Dapper、NHibernate、动态 SQL | [dotnet-sql-audit](net-skill/dotnet-sql-audit/SKILL.md) |
| XXE/XML | XmlDocument、XmlReader、XDocument、XmlSerializer、XSLT、SOAP/OOXML/SVG | [dotnet-xxe-audit](net-skill/dotnet-xxe-audit/SKILL.md) |
| 文件上传 | HttpPostedFile、IFormFile、SaveAs、CopyToAsync、路径与类型校验 | [dotnet-file-upload-audit](net-skill/dotnet-file-upload-audit/SKILL.md) |
| 文件读取 | File.ReadAllText、FileStream、StreamReader、Response.WriteFile、路径穿越 | [dotnet-file-read-audit](net-skill/dotnet-file-read-audit/SKILL.md) |
| 反序列化 | 11 类 formatter、Json.NET TypeNameHandling、ViewState/machineKey、Remoting、类型控制点 | [dotnet-deserialization-audit](net-skill/dotnet-deserialization-audit/SKILL.md) |
| 命令/动态代码执行 | Process.Start、ProcessStartInfo、PowerShell、CodeDom、Roslyn、XAML/XSLT、Assembly.Load、插件机制 | [dotnet-command-exec-audit](net-skill/dotnet-command-exec-audit/SKILL.md) |
| SSRF | HttpClient、WebRequest、URL parser、redirect、DNS rebinding、metadata、代理头、远程导入链 | [dotnet-ssrf-audit](net-skill/dotnet-ssrf-audit/SKILL.md) |
| 配置密钥 | machineKey、连接串、JWT/OAuth/SAML secret、证书私钥、IIS/Swagger/ELMAH/Hangfire 暴露 | [dotnet-config-secrets-audit](net-skill/dotnet-config-secrets-audit/SKILL.md) |
| Web 综合风险 | Razor/WebForms XSS、CSRF/SameSite、CORS、Host Header、Open Redirect、IDOR/BOLA/BFLA、cache/request smuggling | [dotnet-web-risk-audit](net-skill/dotnet-web-risk-audit/SKILL.md) |
| Minimal API | MapGet/MapPost、EndpointFilter、Source Generator、OpenAPI | [dotnet-minimal-api-audit](net-skill/dotnet-minimal-api-audit/SKILL.md) |
| Blazor | IJSRuntime、MarkupString、Circuit、AuthenticationStateProvider | [dotnet-blazor-audit](net-skill/dotnet-blazor-audit/SKILL.md) |
| SignalR | Hub、HubContext、Group、Message broadcast、WebSocket | [dotnet-signalr-audit](net-skill/dotnet-signalr-audit/SKILL.md) |

完整 skill 索引见 [net-skill/README.md](net-skill/README.md)。

> 📖 [English README](README_EN.md)

## 推荐执行流

```text
阶段0: 授权边界 + 源码/发布包识别 + dnSpy 反编译
阶段1: collect_dotnet_surface.py 生成 surface_index.json 和 attack_surface_matrix.md
阶段2: route-mapper + auth-audit + vuln-scanner
阶段3: 高危路由分级 + 专项攻击面聚合
阶段4: route-tracer 调用链追踪
阶段5: SQL / XXE / 文件 / 反序列化 / 命令执行 / SSRF / 配置密钥 / Web 风险 / Minimal API / Blazor / SignalR 专项审计
阶段6: 质量校验 + 唯一最终报告 quality_report.md
```

推荐提示词：

```text
使用当前目录下 net-skill 的 dotnet-offsec-audit 和 dotnet-audit-pipeline，
在授权范围内审计当前 .NET 项目。若源码不完整先反编译，输出目录为 ./audit-output。
最终只生成一个 quality_report.md，默认使用无害验证，密钥和 token 必须脱敏。
```

## 攻击面索引脚本

总控 skill 内置脚本：

```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py <source_path> -o <output_path>\surface
```

输出：

- `surface_index.json`: 机器可读攻击面索引。
- `attack_surface_matrix.md`: 人工复核矩阵。

`surface_index.json` 每条 finding 兼容旧字段，并新增调度字段：

| 字段 | 说明 |
|:-----|:-----|
| `category` | route/auth/sql/xxe/file-read/file-upload/deserialization/command-exec/ssrf/config-secret/web-risk/minimal-api/blazor/signalr |
| `rule_id` | 命中的具体规则 |
| `severity_hint` | 静态风险提示，不等同最终评级 |
| `recommended_skill` | 后续推荐专项 skill |
| `confidence` | High / Medium / Low |
| `evidence_kind` | sink、config、type-control、proxy-header、route-declaration 等 |
| `file` / `line` / `snippet` | 证据位置和最小代码片段 |

重点覆盖 sink 包括 `BinaryFormatter`、`TypeNameHandling`、`UnsafeDeserializeMethodResponse`、`PSObject`、`MulticastDelegate`、`WindowsIdentity`、`ClaimsIdentity`、`Process.Start`、`ProcessStartInfo`、`HttpClient`、`AllowAutoRedirect`、`ForwardedHeaders`、`X-Original-URL`、`X-Rewrite-URL`、`machineKey`、`File.ReadAllText`、`IsLocalUrl`、`SameSite`、`MapGet`、`IJSRuntime`、`MarkupString`、`Hub` 等。

## 原文归档与结构化提炼

本项目采用“原文归档 + 结构化 reference”模式：

- 11 课 .NET 反序列化原文归档在 [raw/deserialization](net-skill/dotnet-deserialization-audit/references/raw/deserialization)，索引见 [RAW_REFERENCE_INDEX.md](net-skill/dotnet-deserialization-audit/references/RAW_REFERENCE_INDEX.md)。
- `hack-skills` 原文归档在 [raw/hack-skills](net-skill/dotnet-offsec-audit/references/raw/hack-skills)，索引见 [RAW_REFERENCE_INDEX.md](net-skill/dotnet-offsec-audit/references/RAW_REFERENCE_INDEX.md)。
- raw 文件只作追溯材料；默认审计优先读取结构化 references，不把 raw 中的攻击样例原样塞进最终报告。

当前归档规模：

| 来源 | 数量 | 用途 |
|:-----|----:|:-----|
| .NET 反序列化 11 课 | 11 个 lesson | formatter、触发条件、审计关键点、修复建议追溯 |
| hack-skills | 18 类 skill family / 29 个 md | Web 攻防方法、绕过条件、链式风险追溯 |

## dnSpy 反编译配置

当源码不完整或只有 `.dll/.exe` 时，使用 dnSpy.Console.exe 反编译。

**下载 dnSpy（不再直接包含在仓库中）：**

```powershell
# 运行脚本自动下载
.\tools\setup-dnspy.ps1
```

或手动下载：https://github.com/dnSpy/dnSpy/releases

推荐目录：

```text
目标项目/
├── dnSpy/
│   ├── dnSpy.Console.exe
│   └── 依赖文件
├── bin/
└── net-skill/
```

示例命令：

```powershell
dnSpy\dnSpy.Console.exe -o audit-output\decompiled -r bin\
```

约束：

- 成功时必须验证 `decompiled/` 中存在 `.cs` 文件。
- 部分失败时记录失败 DLL，继续审计已反编译部分。
- 工具缺失时报告阻塞项，不伪造反编译结论。

## 安装与使用

方式一：复制整个 `net-skill/` 到支持本地 skill 的 Agent 工作目录，然后显式要求使用该目录。

方式二：把 `net-skill/` 放入待审计项目根目录，在提示词中指定：

```text
使用当前目录下的 net-skill，对当前 .NET 源码执行授权代码审计。
先运行 dotnet-offsec-audit 的攻击面索引，再按 dotnet-audit-pipeline 输出 quality_report.md。
```

## 最终报告要求

最终交付文件为 `{output_path}/quality_report.md`。结构参考 [REPORT_TEMPLATE.md](net-skill/dotnet-offsec-audit/references/REPORT_TEMPLATE.md)。

必须包含：

- 审计概况、授权边界、框架识别、反编译范围。
- 攻击面总览、路由与鉴权状态、P0/P1 高危目标。
- 每个漏洞的入口、调用链、sink、代码证据、证据标签、风险等级、影响和修复建议。
- 每个高危问题的无害验证，或说明为何无法安全验证。
- 反序列化 11 类 formatter 覆盖情况。
- 配置密钥脱敏展示和轮换建议。
- 质量覆盖率、raw 来源头完整性、安全输出检查。

禁止：

- 未替换的 `TODO`、`...`、`【填写】`。
- 省略式输出，例如“同上”“略”“参考前文”。
- 完整密钥、token、连接串。
- 默认输出可直接用于未授权目标的武器化 payload。

## 质量校验

维护或发布前建议运行：

```powershell
$validator = "C:\Users\user\.codex\skills\.system\skill-creator\scripts\quick_validate.py"
Get-ChildItem .\net-skill -Directory |
  Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } |
  ForEach-Object { python $validator $_.FullName }

python -m py_compile .\net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py
```

还应检查：

- 结构化 Markdown 链接无断链，raw 归档只校验文件存在和来源头。
- `surface_index.json` 字段完整：`recommended_skill`、`confidence`、`evidence_kind`。
- 关键术语覆盖：11 类 formatter、命令执行 sink、SSRF 绕过、Web 风险、配置密钥、Minimal API、Blazor、SignalR。
- `quality_report.md` 模板唯一、完整、默认无害验证、密钥脱敏。

## 维护同步规则

新增或修改专项时，必须同步以下位置：

1. 对应 `net-skill/<skill-name>/SKILL.md`。
2. 对应 `references/` 结构化文档。
3. [DOTNET_ATTACK_SURFACE_TAXONOMY.md](net-skill/shared/DOTNET_ATTACK_SURFACE_TAXONOMY.md)。
4. [collect_dotnet_surface.py](net-skill/dotnet-offsec-audit/scripts/collect_dotnet_surface.py) 的规则与推荐 skill 字段。
5. [dotnet-audit-pipeline/SKILL.md](net-skill/dotnet-audit-pipeline/SKILL.md) 和质量模板。
6. 本 README 与 [net-skill/README.md](net-skill/README.md)。

## Support Matrix

| 框架 | 状态 |
|-----------|--------|
| ASP.NET WebForms | ✅ 完整支持 |
| ASP.NET MVC 5 | ✅ 完整支持 |
| ASP.NET Web API 2 | ✅ 完整支持 |
| ASP.NET Core (2.x–9.x) | ✅ 完整支持 |
| WCF | ✅ 完整支持 |
| IIS 发布包 | ✅ 完整支持 |
| Blazor Server / WASM | ✅ v2.0 |
| SignalR | ✅ v2.0 |
| Minimal API | ✅ v2.0 |
| gRPC (.NET) | 🚧 部分支持 |

## 效果截图

![效果截图 1](docs/assets/screenshot-audit-effect-1.png)
![效果截图 2](docs/assets/screenshot-audit-effect-2.png)
![效果截图 3](docs/assets/screenshot-audit-effect-3.png)
![效果截图 4](docs/assets/screenshot-audit-effect-4.png)
