# Changelog

所有显著的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.0.0] - 2026-05-05

### 🚀 Added

- **全球顶级基础设施**
  - 新增 `AGENTS.md` — AI Agent 项目核心配置与使用指南。
  - 新增 `CONTRIBUTING.md` — 贡献规范与维护同步规则。
  - 新增 `CHANGELOG.md` — 版本变更记录。
  - 新增 `.github/workflows/validate.yml` — GitHub Actions CI 质量校验。
- **双语国际化**
  - 新增 `README_EN.md` — 完整英文版 README。
  - 所有 SKILL.md frontmatter 新增 `description_en` 字段。
- **现代 .NET 覆盖（3 个全新专项 skill）**
  - `dotnet-minimal-api-audit` — ASP.NET Core Minimal API 路由、Endpoint Filter、Source Generator 审计。
  - `dotnet-blazor-audit` — Blazor Server / WASM 渲染、JS Interop、Circuit 鉴权审计。
  - `dotnet-signalr-audit` — SignalR Hub、HubContext、消息鉴权与跨站 WebSocket 审计。
- **Skill 元数据升级**
  - 全部 18 个 skill 的 frontmatter 新增 `version`、`author`、`tags`、`compatibility`。
  - 全部 agents/openai.yaml 升级：新增 `model.hints`、`tools.recommended`、`file_associations`。
- **攻击面索引增强**
  - `collect_dotnet_surface.py` 新增 Minimal API、Blazor、SignalR、gRPC 识别规则。
  - `DOTNET_ATTACK_SURFACE_TAXONOMY.md` 同步更新分类映射。

### 🔧 Changed

- **仓库治理**
  - 重写 `.gitignore`，适配 Python / .NET / Skill 项目标准。
  - dnSpy 二进制从仓库移除，改为 `tools/setup-dnspy.ps1` 自动下载脚本。
  - 截图归档至 `docs/assets/` 并语义化命名。
- **文档结构**
  - 根目录 README 重新组织，增加英文引导、Support Matrix、安装指南。

### 🛡️ Security

- 明确安全边界：武器化 payload 仅允许在 "Authorized Lab Validation" 章节出现。
- 所有密钥、token、连接串在输出中必须脱敏。

## [1.0.0] - 2025-04

### 🎉 Initial Release

- 15 个专项 skill 覆盖 .NET 全链路代码审计：
  - 总控：dotnet-offsec-audit、dotnet-audit-pipeline
  - 基础：dotnet-route-mapper、dotnet-auth-audit、dotnet-route-tracer、dotnet-vuln-scanner
  - 专项：dotnet-sql-audit、dotnet-xxe-audit、dotnet-file-upload-audit、dotnet-file-read-audit、dotnet-deserialization-audit、dotnet-command-exec-audit、dotnet-ssrf-audit、dotnet-config-secrets-audit、dotnet-web-risk-audit
- 攻击面索引脚本 `collect_dotnet_surface.py`。
- 依赖漏洞扫描脚本 `scan_dotnet_dependencies.py`。
- 共享标准：`DOTNET_ATTACK_SURFACE_TAXONOMY.md`、`DOTNET_DECOMPILE_STRATEGY.md`、`DOTNET_OUTPUT_STANDARD.md`、`SEVERITY_RATING.md`、`REDTEAM_LAB_BOUNDARY.md`。
- 原文归档：.NET 反序列化 11 课、hack-skills 18 类。
