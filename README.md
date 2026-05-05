# .NET Offensive Security & Code Audit Skill Suite

[![License](https://img.shields.io/badge/license-Mulan%20PSL%20v2-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-18-green.svg)](#核心能力)
[![Coverage](https://img.shields.io/badge/coverage-.NET%20Full%20Stack-orange.svg)](#support-matrix)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success.svg)](.github/workflows/validate.yml)
[![English](https://img.shields.io/badge/README-English-blue.svg)](README_EN.md)

> 面向 .NET 全生态的 AI Agent 安全审计 Skill 集合，覆盖传统 ASP.NET WebForms 到 ASP.NET Core 9.x、Blazor、SignalR、Minimal API 的完整攻击面审计。

## 目录

- [适用范围](#适用范围)
- [安全边界](#安全边界)
- [核心能力](#核心能力)
- [快速开始](#快速开始)
  - [环境准备](#环境准备)
  - [场景一：完整源码审计](#场景一完整源码审计)
  - [场景二：仅有二进制审计](#场景二仅有二进制审计)
  - [场景三：单一漏洞专项审计](#场景三单一漏洞专项审计)
- [攻击面索引脚本](#攻击面索引脚本)
- [架构概览](#架构概览)
- [详细执行流程](#详细执行流程)
- [输出规范](#输出规范)
- [Support Matrix](#support-matrix)
- [故障排查](#故障排查)
- [相关文档](#相关文档)
- [许可证](#许可证)

## 适用范围

| 场景 | 说明 |
|------|------|
| **ASP.NET 全系** | WebForms、MVC 5、Web API 2、ASP.NET Core (2.x–9.x)、WCF、IIS 部署包 |
| **源码审计** | 完整的 `.csproj` / `.sln` 项目、发布后的站点目录 |
| **二进制审计** | 仅有 `bin/` 目录、`.dll` / `.exe` 文件，需先通过 dnSpy 反编译 |
| **现代 .NET** | Minimal API、Blazor Server / WASM、SignalR、Source Generator |
| **审计模式** | 授权源码审计、防守加固复核、红队实验室验证 |

## 安全边界

- **默认无害验证**：报告只输出无害验证证据（DNS callback、错误回显、文件名回显、 harmless command output）与修复建议。
- **红队实验室边界**：涉及命令执行、反序列化、SSRF、凭据伪造、ViewState / machineKey 的内容必须遵守 [REDTEAM_LAB_BOUNDARY.md](net-skill/shared/REDTEAM_LAB_BOUNDARY.md)。
- **禁止默认武器化**：不默认生成可直接用于未授权目标的完整 payload、密钥、token、连接串或身份伪造材料。

## 核心能力

| 能力 | 覆盖内容 | 入口 Skill |
|:-----|:---------|:----------|
| 总控编排 | 授权边界、反编译、攻击面索引、专项调度、最终报告 | [dotnet-offsec-audit](net-skill/dotnet-offsec-audit/SKILL.md) |
| 全链路流水线 | Agent 分阶段执行、质量门、唯一 `quality_report.md` | [dotnet-audit-pipeline](net-skill/dotnet-audit-pipeline/SKILL.md) |
| 路由与参数 | MVC / Web API / Core / WebForms / WCF / Minimal API 路由、参数来源、请求模板 | [dotnet-route-mapper](net-skill/dotnet-route-mapper/SKILL.md) |
| 鉴权与越权 | FormsAuth、Identity、JWT、OAuth/OIDC、Windows Auth、Membership、IDOR | [dotnet-auth-audit](net-skill/dotnet-auth-audit/SKILL.md) |
| 调用链追踪 | 从 Controller / Page / Handler / WCF 到 SQL、文件、XML、命令等 Sink | [dotnet-route-tracer](net-skill/dotnet-route-tracer/SKILL.md) |
| 组件漏洞 | NuGet、DLL、配置依赖与 CVE/GHSA 触发条件 | [dotnet-vuln-scanner](net-skill/dotnet-vuln-scanner/SKILL.md) |
| SQL 注入 | ADO.NET、EF、Dapper、NHibernate、动态 SQL | [dotnet-sql-audit](net-skill/dotnet-sql-audit/SKILL.md) |
| XXE / XML | XmlDocument、XmlReader、XDocument、XmlSerializer、XSLT、SOAP / OOXML / SVG | [dotnet-xxe-audit](net-skill/dotnet-xxe-audit/SKILL.md) |
| 文件上传 | HttpPostedFile、IFormFile、SaveAs、CopyToAsync、路径与类型校验 | [dotnet-file-upload-audit](net-skill/dotnet-file-upload-audit/SKILL.md) |
| 文件读取 | File.ReadAllText、FileStream、StreamReader、Response.WriteFile、路径穿越 | [dotnet-file-read-audit](net-skill/dotnet-file-read-audit/SKILL.md) |
| 反序列化 | 11 类 Formatter、Json.NET TypeNameHandling、ViewState / machineKey、Remoting | [dotnet-deserialization-audit](net-skill/dotnet-deserialization-audit/SKILL.md) |
| 命令执行 | Process.Start、PowerShell、CodeDom、Roslyn、XAML / XSLT、Assembly.Load | [dotnet-command-exec-audit](net-skill/dotnet-command-exec-audit/SKILL.md) |
| SSRF | HttpClient、WebRequest、URL Parser、Redirect、DNS Rebinding、Metadata | [dotnet-ssrf-audit](net-skill/dotnet-ssrf-audit/SKILL.md) |
| 配置密钥 | machineKey、连接串、JWT / OAuth / SAML Secret、证书私钥、IIS / Swagger / ELMAH | [dotnet-config-secrets-audit](net-skill/dotnet-config-secrets-audit/SKILL.md) |
| Web 综合风险 | XSS、CSRF / SameSite、CORS、Host Header、Open Redirect、IDOR / BOLA / BFLA | [dotnet-web-risk-audit](net-skill/dotnet-web-risk-audit/SKILL.md) |
| Minimal API | MapGet / MapPost、EndpointFilter、Source Generator、OpenAPI | [dotnet-minimal-api-audit](net-skill/dotnet-minimal-api-audit/SKILL.md) |
| Blazor | IJSRuntime、MarkupString、Circuit、AuthenticationStateProvider | [dotnet-blazor-audit](net-skill/dotnet-blazor-audit/SKILL.md) |
| SignalR | Hub、HubContext、Group、Message Broadcast、WebSocket | [dotnet-signalr-audit](net-skill/dotnet-signalr-audit/SKILL.md) |

完整索引见 [net-skill/README.md](net-skill/README.md)。

> [English README](README_EN.md)

---

## 快速开始

### 环境准备

1. **Python 3.10+**
   ```powershell
   python --version
   ```

2. **dnSpy（二进制审计时需要）**
   ```powershell
   # 自动下载
   .\tools\setup-dnspy.ps1

   # 或手动下载：https://github.com/dnSpy/dnSpy/releases
   ```

3. **将 `net-skill/` 复制到审计项目根目录，或 Agent 工作目录**

### 场景一：完整源码审计

适用于拥有完整 `.cs` / `.csproj` / `.sln` 源码的项目。

**步骤 1：运行攻击面索引**
```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py `
  .\target-project `
  -o .\audit-output\surface
```

输出：
- `audit-output/surface/surface_index.json` — 机器可读攻击面
- `audit-output/surface/attack_surface_matrix.md` — 人工复核矩阵

**步骤 2：使用总控 Skill 执行完整审计**

```text
使用当前目录下 net-skill 的 dotnet-offsec-audit 和 dotnet-audit-pipeline，
在授权范围内审计当前 .NET 项目。输出目录为 ./audit-output。
最终只生成一个 quality_report.md，默认使用无害验证，密钥和 token 必须脱敏。
```

**步骤 3：检查最终报告**
```text
audit-output/quality_report.md
```

### 场景二：仅有二进制审计

适用于仅有 `bin/` 目录或 `.dll` / `.exe` 文件的项目。

**步骤 1：反编译**
```powershell
# 使用 setup 脚本下载的 dnSpy
dnSpy\dnSpy.Console.exe -o audit-output\decompiled -r target-project\bin\

# 验证反编译结果
Test-Path audit-output\decompiled\*.cs  # 应为 True
```

**步骤 2：对反编译结果运行攻击面索引**
```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py `
  .\audit-output\decompiled `
  -o .\audit-output\surface
```

**步骤 3：执行审计并标注反编译来源**

```text
使用当前目录下 net-skill 的 dotnet-offsec-audit 和 dotnet-audit-pipeline，
审计反编译后的代码（来源：target-project/bin/ 下的 DLL）。
输出目录 ./audit-output，最终报告 quality_report.md。
所有来自反编译代码的证据必须标注原始 DLL 名称和反编译路径。
```

### 场景三：单一漏洞专项审计

适用于已经明确漏洞类型的场景（如只审 SQL 注入或反序列化）。

```text
使用当前目录下 net-skill 的 dotnet-sql-audit，
审计当前项目中所有 ADO.NET / Entity Framework / Dapper 的 SQL 注入风险。
输出到 ./audit-output/sql-specialized/。
```

---

## 攻击面索引脚本

```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py <source_path> -o <output_path>\surface
```

**输出文件说明：**

| 文件 | 用途 |
|------|------|
| `surface_index.json` | 机器可读攻击面索引，每条 finding 包含 category、rule_id、severity_hint、recommended_skill、confidence、evidence_kind、file、line、snippet |
| `attack_surface_matrix.md` | 人工复核矩阵，按高危程度排序 |

**索引覆盖范围：**

- **路由**：Controller、Page、Handler、WCF Operation、Minimal API MapGet/MapPost
- **鉴权**：Authorize、AllowAnonymous、FormsAuth、JWT、OAuth
- **Sink**：BinaryFormatter、TypeNameHandling、Process.Start、HttpClient、machineKey、File.ReadAllText、IJSRuntime、MarkupString、Hub 等
- **配置**：debug=true、customErrors=Off、Swagger 暴露、ELMAH、Hangfire

---

## 架构概览

```text
net-skill/
├── dotnet-offsec-audit/              # 总控编排：授权确认 → 反编译 → 索引 → 调度 → 报告
│   └── scripts/collect_dotnet_surface.py
├── dotnet-audit-pipeline/            # 流水线：6 阶段执行 + 质量门
├── dotnet-route-mapper/              # 路由枚举：HTTP / WCF / WebForms / Minimal API
├── dotnet-auth-audit/                # 鉴权审计：FormsAuth / Identity / JWT / OAuth / IDOR
├── dotnet-route-tracer/              # 调用链追踪：入口 → Sink 可达性
├── dotnet-vuln-scanner/              # 组件漏洞：NuGet / DLL / CVE / GHSA
├── dotnet-sql-audit/                 # SQL 注入：ADO.NET / EF / Dapper / NHibernate
├── dotnet-xxe-audit/                 # XXE / XML：XmlDocument / XmlReader / XDocument / XSLT
├── dotnet-file-upload-audit/         # 文件上传：IFormFile / SaveAs / 校验绕过
├── dotnet-file-read-audit/           # 文件读取：FileStream / Path.Combine / 路径穿越
├── dotnet-deserialization-audit/     # 反序列化：11 类 Formatter / ViewState / Remoting
├── dotnet-command-exec-audit/        # 命令执行：Process.Start / PowerShell / CodeDom / Roslyn
├── dotnet-ssrf-audit/                # SSRF：HttpClient / WebRequest / DNS Rebinding / Metadata
├── dotnet-config-secrets-audit/      # 配置密钥：machineKey / JWT Secret / IIS 暴露面
├── dotnet-web-risk-audit/            # Web 风险：XSS / CSRF / CORS / Host Header / Open Redirect
├── dotnet-minimal-api-audit/         # Minimal API：EndpointFilter / Source Generator / OpenAPI
├── dotnet-blazor-audit/              # Blazor：JS Interop / MarkupString / Circuit / XSS
├── dotnet-signalr-audit/             # SignalR：Hub / Group / Message Broadcast / WebSocket
└── shared/                           # 共享标准
    ├── DOTNET_ATTACK_SURFACE_TAXONOMY.md
    ├── DOTNET_DECOMPILE_STRATEGY.md
    ├── DOTNET_OUTPUT_STANDARD.md
    ├── REDTEAM_LAB_BOUNDARY.md
    └── SEVERITY_RATING.md
```

---

## 详细执行流程

```text
阶段0: 授权边界确认
  ├── 确认审计授权范围与目标系统归属
  ├── 识别项目类型（WebForms / MVC / Core / WCF / Minimal API / Blazor）
  └── 若源码不完整 → dnSpy 反编译 → 验证 decompiled/ 存在 .cs 文件

阶段1: 攻击面索引
  ├── collect_dotnet_surface.py 扫描源码/反编译代码
  ├── 生成 surface_index.json（机器可读）
  └── 生成 attack_surface_matrix.md（人工复核）

阶段2: 基础审计并行
  ├── dotnet-route-mapper: 全量路由、参数、Burp 请求模板
  ├── dotnet-auth-audit: 鉴权框架、路由鉴权映射、越权线索
  └── dotnet-vuln-scanner: NuGet/DLL 组件漏洞与触发条件

阶段3: 交叉筛选与优先级
  ├── 未鉴权/弱鉴权路由 + 高危 Sink 交叉
  ├── 组件漏洞触发入口确认
  └── 配置密钥放大链识别

阶段4: 调用链追踪
  └── dotnet-route-tracer: 从入口到 Sink 的参数传播与可达性证明

阶段5: 专项深度审计（按 surface_index 调度）
  ├── SQL / XXE / 文件上传 / 文件读取
  ├── 反序列化 / 命令执行 / SSRF
  ├── 配置密钥 / Web 综合风险
  └── Minimal API / Blazor / SignalR（现代 .NET）

阶段6: 质量校验与报告输出
  ├── 检查 quality_report.md 完整性（无 TODO、无省略、无裸密钥）
  ├── 校验安全输出（无默认武器化 payload）
  └── 输出唯一最终报告 quality_report.md
```

---

## 输出规范

**最终交付物**：`{output_path}/quality_report.md`

**必须包含：**
- 审计概况、授权边界、框架识别、反编译范围
- 攻击面总览、路由与鉴权状态、P0/P1 高危目标
- 每个漏洞的入口路由、参数来源、调用链、Sink、代码证据、证据标签、风险等级、影响、修复建议
- 每个高危问题的无害验证证据，或说明为何无法安全验证
- 反序列化 11 类 Formatter 覆盖情况
- 配置密钥脱敏展示和轮换建议
- 质量覆盖率、raw 来源头完整性、安全输出检查

**禁止出现：**
- 未替换的 `TODO`、`...`、`【填写】`
- 省略式输出（"同上"、"略"、"参考前文"）
- 完整密钥、token、连接串
- 默认输出可直接用于未授权目标的武器化 payload

---

## Support Matrix

| 框架 | 状态 | 说明 |
|-----------|--------|------|
| ASP.NET WebForms | 完整支持 | Page、Control、Handler、ASMX 全覆盖 |
| ASP.NET MVC 5 | 完整支持 | 属性路由、传统路由、Filter |
| ASP.NET Web API 2 | 完整支持 | ApiController、OData、MediaTypeFormatter |
| ASP.NET Core (2.x–9.x) | 完整支持 | MVC、Razor Pages、Middleware、Filter Pipeline |
| WCF | 完整支持 | ServiceContract、OperationContract、Binding |
| IIS 发布包 | 完整支持 | bin/、web.config、部署目录结构 |
| Blazor Server / WASM | v2.0 新增 | Circuit、JS Interop、组件渲染 |
| SignalR | v2.0 新增 | Hub、HubContext、Group、Message Broadcast |
| Minimal API | v2.0 新增 | MapGet/MapPost、EndpointFilter、Source Generator |
| gRPC (.NET) | 部分支持 | Proto、Service 基础识别 |

---

## 故障排查

| 问题 | 原因 | 解决方式 |
|------|------|----------|
| `collect_dotnet_surface.py` 报错 | Python 版本过低 | 升级到 Python 3.10+ |
| dnSpy 反编译失败 | 目标为 .NET Native / AOT | 记录失败 DLL，继续审计其他部分 |
| `quality_report.md` 中出现 `TODO` | 流水线阶段未完成 | 退回阶段6重新执行质量校验 |
| 反编译代码无 `.cs` 文件 | dnSpy 路径错误或目标为 Native DLL | 检查 dnSpy 安装路径与目标框架版本 |
| Skill 加载后无输出 | Agent 未正确识别 net-skill 目录 | 确认 net-skill/ 在工作目录下，并在提示词中显式指定路径 |

---

## 相关文档

| 文档 | 用途 |
|------|------|
| [AGENTS.md](AGENTS.md) | Agent 项目核心配置与使用指南 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Skill 新增规范、贡献流程、维护同步规则 |
| [CHANGELOG.md](CHANGELOG.md) | 版本变更记录 |
| [net-skill/README.md](net-skill/README.md) | 内部 Skill 索引与 Reference 速查 |

## 许可证

本项目采用 [Mulan PSL v2](LICENSE) 开源许可证。
