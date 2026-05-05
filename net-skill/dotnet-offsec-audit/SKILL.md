---
name: dotnet-offsec-audit
version: 2.0.0
description: .NET 攻防一体化代码审计总控 skill。用于授权环境下对 ASP.NET WebForms、MVC、Web API、ASP.NET Core、WCF、IIS 部署包、反编译 DLL/EXE 执行全链路安全审计；编排路由提取、鉴权、组件漏洞、调用链追踪、SQL/XXE/文件类漏洞、反序列化、命令执行、SSRF、配置密钥、XSS/CSRF/CORS/Host Header/业务越权等专项检查，并输出唯一可复核 quality_report.md。适用于源码审计、红队实验室验证、防守加固复核、仅有 bin 目录或反编译代码的 .NET 项目。
description_en: .NET offensive security unified audit orchestrator. Performs full-stack security audits on ASP.NET WebForms, MVC, Web API, ASP.NET Core, WCF, IIS packages, and decompiled DLL/EXE. Orchestrates route extraction, auth, component vulnerabilities, call-chain tracing, SQL/XXE/file/deserialization/command-exec/SSRF/secrets/web-risk audits.
author: net-code-audit-team
tags: ['dotnet', 'orchestrator', 'offensive-security', 'audit', 'master']
compatibility: ['asp.net', 'asp.net-core', 'wcf', 'iis']
---

# .NET 攻防一体化审计总控

在授权范围内执行 .NET Web 项目的完整攻击面梳理、代码可达性验证、红队实验室复现建议和修复建议。默认输出无害验证证据；需要利用链时先读取 [REDTEAM_LAB_BOUNDARY.md](../shared/REDTEAM_LAB_BOUNDARY.md)，只在隔离实验室中使用。

## 输入

- `source_path`: 源码目录、站点目录、发布包或 bin 目录。
- `output_path`: 默认 `{source_path}_audit`。
- `mode`: 默认 `redteam-lab`，可选 `defense-hardening` 或 `triage-only`。
- `dnspy_path`: 可选；未提供时按 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md) 搜索。

## 总流程

1. 先确认授权边界、项目类型和输出目录；不要对未知第三方系统生成可直接投递的武器化 payload。
2. 当源码不完整或存在 `.dll/.exe` 时，先执行 dnSpy 全量反编译并记录失败程序集。
3. 运行 `scripts/collect_dotnet_surface.py` 生成 `surface_index.json` 与 `attack_surface_matrix.md`，用它决定专项审计优先级。
   - `surface_index.json` 每条命中保留 `category/rule_id/severity_hint/file/line/snippet`，并补充 `recommended_skill`、`confidence`、`evidence_kind`，供流水线调度专项 agent。
   - 需要追溯原始 hack-skill 资料时读取 [RAW_REFERENCE_INDEX.md](references/RAW_REFERENCE_INDEX.md)。
4. 并行或分阶段调用既有基础 skill：
   - [dotnet-route-mapper](../dotnet-route-mapper/SKILL.md): 全量路由、参数、Burp 请求模板。
   - [dotnet-auth-audit](../dotnet-auth-audit/SKILL.md): 鉴权框架、路由鉴权映射、越权。
   - [dotnet-vuln-scanner](../dotnet-vuln-scanner/SKILL.md): NuGet/DLL 组件漏洞。
   - [dotnet-route-tracer](../dotnet-route-tracer/SKILL.md): 参数到 sink 的可达调用链。
5. 依据 sink 类型调用专项 skill：
   - SQL: [dotnet-sql-audit](../dotnet-sql-audit/SKILL.md)
   - XXE/XML: [dotnet-xxe-audit](../dotnet-xxe-audit/SKILL.md)
   - 文件上传: [dotnet-file-upload-audit](../dotnet-file-upload-audit/SKILL.md)
   - 文件读取/路径穿越: [dotnet-file-read-audit](../dotnet-file-read-audit/SKILL.md)
   - 反序列化: [dotnet-deserialization-audit](../dotnet-deserialization-audit/SKILL.md)
   - 命令/动态代码执行: [dotnet-command-exec-audit](../dotnet-command-exec-audit/SKILL.md)
   - SSRF/出站请求: [dotnet-ssrf-audit](../dotnet-ssrf-audit/SKILL.md)
   - 配置密钥/部署暴露: [dotnet-config-secrets-audit](../dotnet-config-secrets-audit/SKILL.md)
   - Web 风险与业务授权: [dotnet-web-risk-audit](../dotnet-web-risk-audit/SKILL.md)
6. 汇总为唯一最终报告 `quality_report.md`，中间产物保留在输出目录下供复核。

## 优先级路由

| 观察 | 优先专项 |
|---|---|
| 无鉴权高危路由、管理接口、ID 参数 | auth -> route-tracer -> web-risk |
| `BinaryFormatter`、`TypeNameHandling`、`LosFormatter`、`ViewState` | deserialization |
| `Process.Start`、`PowerShell`、`CodeDomProvider`、`XslCompiledTransform` | command-exec |
| `HttpClient`、`WebRequest`、URL 参数、webhook、导入远程资源 | ssrf |
| `machineKey`、连接串、JWT 密钥、debug、ELMAH、Swagger | config-secrets |
| `File.ReadAllText`、`Response.WriteFile`、`PhysicalFile` | file-read |
| `IFormFile`、`SaveAs`、`RadAsyncUpload` | file-upload |
| `XmlDocument.LoadXml`、SOAP、OOXML/SVG 导入 | xxe |

## 证据规则

- 每个确认漏洞必须包含入口路由、参数来源、调用链、sink、代码位置、鉴权状态、可达性结论、影响、修复建议。
- PoC 默认使用无害验证：响应差异、错误回显、DNS/HTTP callback、文件名回显、固定字符串命令输出或日志证据。
- 红队实验室 payload 只能放在“授权实验室验证建议”小节，不作为默认可复制攻击包。
- 对反编译代码必须标注来源 DLL 与反编译路径。

## 输出目录

```text
{output_path}/
├── decompiled/
├── surface/surface_index.json
├── surface/attack_surface_matrix.md
├── route_mapper/
├── auth_audit/
├── specialized/
├── trace/
└── quality_report.md
```

## 自检

- 全量路由与鉴权映射已覆盖。
- 高危路由至少完成一个入口到 sink 的可达性追踪。
- 每个新增专项有“未发现/发现/无法判断”的明确结论。
- `surface_index.json` 的新增字段完整，Critical/High 命中均进入 `specialized_surface_targets.md` 或最终报告说明。
- 最终报告中没有未替换占位符、初始化标记或省略式输出。
