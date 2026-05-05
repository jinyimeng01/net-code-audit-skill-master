# .NET Offensive Security & Code Audit Skill Suite

[![License](https://img.shields.io/badge/license-Mulan%20PSL%20v2-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-18-green.svg)](#核心能力)
[![Coverage](https://img.shields.io/badge/coverage-.NET%20Full%20Stack-orange.svg)](#support-matrix)
[![English](https://img.shields.io/badge/README-English-blue.svg)](README_EN.md)

> 一套面向 .NET 全生态的 AI Agent 安全审计 Skill 集合，覆盖从传统 ASP.NET WebForms 到现代 ASP.NET Core 9.x、Blazor、SignalR、Minimal API 的完整攻击面。

## 适用范围

- **框架**：ASP.NET WebForms、MVC 5、Web API 2、ASP.NET Core (2.x–9.x)、WCF、IIS 部署包
- **场景**：授权源码审计、二进制-only 审计（dnSpy 反编译）、防守加固复核、红队实验室验证
- **交付**：唯一、可复核、默认无害验证的 `quality_report.md`

## 安全边界

- 默认报告仅输出无害验证证据与修复建议。
- 涉及命令执行、反序列化、SSRF、凭据伪造、ViewState/machineKey 的内容必须遵守 [REDTEAM_LAB_BOUNDARY.md](net-skill/shared/REDTEAM_LAB_BOUNDARY.md)。
- 不默认生成可直接用于未授权目标的武器化 payload、完整密钥或 token。

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

> 📖 [English README](README_EN.md)

## 快速开始

### 推荐执行流

```text
阶段0: 授权边界 + 源码识别 + dnSpy 反编译
阶段1: collect_dotnet_surface.py → surface_index.json + attack_surface_matrix.md
阶段2: route-mapper + auth-audit + vuln-scanner
阶段3: 高危路由分级 + 专项攻击面聚合
阶段4: route-tracer 调用链追踪
阶段5: SQL / XXE / 文件 / 反序列化 / 命令执行 / SSRF / 密钥 / Web / Minimal API / Blazor / SignalR
阶段6: 质量校验 → 唯一最终报告 quality_report.md
```

### 攻击面索引

```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py <source_path> -o <output_path>\surface
```

输出 `surface_index.json`（机器可读）与 `attack_surface_matrix.md`（人工复核矩阵），每条 finding 包含 `category`、`rule_id`、`recommended_skill`、`confidence`、`evidence_kind`。

### 提示词模板

```text
使用当前目录下 net-skill 的 dotnet-offsec-audit 和 dotnet-audit-pipeline，
在授权范围内审计当前 .NET 项目。若源码不完整先反编译，输出目录为 ./audit-output。
最终只生成一个 quality_report.md，默认使用无害验证，密钥和 token 必须脱敏。
```

## 架构概览

```text
net-skill/
├── dotnet-offsec-audit/          # 总控编排
├── dotnet-audit-pipeline/        # 流水线 + 质量门
├── dotnet-route-mapper/          # 路由枚举
├── dotnet-auth-audit/            # 鉴权审计
├── dotnet-route-tracer/          # 调用链追踪
├── dotnet-vuln-scanner/          # 组件漏洞扫描
├── dotnet-sql-audit/             # SQL 注入
├── dotnet-xxe-audit/             # XXE / XML
├── dotnet-file-upload-audit/     # 文件上传
├── dotnet-file-read-audit/       # 文件读取 / 路径穿越
├── dotnet-deserialization-audit/ # 反序列化（11 类 Formatter）
├── dotnet-command-exec-audit/    # 命令执行
├── dotnet-ssrf-audit/            # SSRF
├── dotnet-config-secrets-audit/  # 配置密钥
├── dotnet-web-risk-audit/        # Web 综合风险
├── dotnet-minimal-api-audit/     # Minimal API
├── dotnet-blazor-audit/          # Blazor
├── dotnet-signalr-audit/         # SignalR
└── shared/                       # 共享标准与分类
```

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

## 工具链

| 脚本 | 用途 |
|------|------|
| `net-skill/dotnet-offsec-audit/scripts/collect_dotnet_surface.py` | 攻击面索引生成 |
| `net-skill/dotnet-vuln-scanner/scripts/scan_dotnet_dependencies.py` | 依赖 CVE 扫描 |
| `tools/setup-dnspy.ps1` | dnSpy 自动下载与配置 |

## 质量与标准

- **最终报告**：`{output_path}/quality_report.md` — 唯一、完整、可复核
- **安全输出**：默认无害验证，密钥脱敏，武器化 payload 仅限实验室场景
- **CI 验证**：GitHub Actions 自动校验 Skill 结构、Python 语法、Frontmatter 完整性
- **维护同步**：修改 Skill 需同步更新 references、taxonomy、脚本、README、流水线模板

## 相关文档

- [AGENTS.md](AGENTS.md) — Agent 使用指南
- [CONTRIBUTING.md](CONTRIBUTING.md) — 贡献规范
- [CHANGELOG.md](CHANGELOG.md) — 版本变更
- [LICENSE](LICENSE) — Mulan PSL v2

## License

本项目采用 [Mulan PSL v2](LICENSE) 开源许可证。
