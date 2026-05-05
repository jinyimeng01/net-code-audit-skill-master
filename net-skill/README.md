# net-skill 内部索引

本目录是 .NET 攻防代码审计 skill 集合。优先从总控入口启动；专项 skill 只在明确 sink 或流水线调度时加载，避免一次性塞入过多上下文。

## 入口选择

| 场景 | 推荐入口 |
|:-----|:---------|
| 完整授权审计、需要最终报告 | [dotnet-offsec-audit](dotnet-offsec-audit/SKILL.md) |
| 需要 agent 分阶段执行和质量门 | [dotnet-audit-pipeline](dotnet-audit-pipeline/SKILL.md) |
| 只想先摸攻击面 | [collect_dotnet_surface.py](dotnet-offsec-audit/scripts/collect_dotnet_surface.py) |
| 只审某一类漏洞 | 直接加载下方对应专项 skill |

## 基础与编排 Skill

| Skill | 作用 | 关键输出 |
|:------|:-----|:---------|
| [dotnet-offsec-audit](dotnet-offsec-audit/SKILL.md) | 总控入口，确认授权边界、运行攻击面索引、调度基础与专项审计 | `quality_report.md` |
| [dotnet-audit-pipeline](dotnet-audit-pipeline/SKILL.md) | 流水线编排，定义阶段、agent、质量门和最终报告规范 | `cross_analysis/`, `specialized/`, `quality_report.md` |
| [dotnet-route-mapper](dotnet-route-mapper/SKILL.md) | 枚举 HTTP/WCF/WebForms 路由、参数和请求模板 | `route_mapper/` |
| [dotnet-auth-audit](dotnet-auth-audit/SKILL.md) | 鉴权框架、路由鉴权状态、绕过和越权线索 | `auth_audit/` |
| [dotnet-vuln-scanner](dotnet-vuln-scanner/SKILL.md) | NuGet/DLL/配置依赖漏洞与触发条件 | 组件漏洞报告 |
| [dotnet-route-tracer](dotnet-route-tracer/SKILL.md) | 从入口到 sink 的调用链、参数传播和可达性 | `trace/` |

## 专项 Skill

| 分类 | Skill | 典型 sink / 观察 |
|:-----|:------|:-----------------|
| SQL | [dotnet-sql-audit](dotnet-sql-audit/SKILL.md) | `SqlCommand`, `FromSqlRaw`, Dapper, NHibernate, 动态 SQL |
| XXE/XML | [dotnet-xxe-audit](dotnet-xxe-audit/SKILL.md) | `XmlDocument`, `XmlReader`, `XDocument`, SOAP, XSLT, OOXML/SVG |
| 文件上传 | [dotnet-file-upload-audit](dotnet-file-upload-audit/SKILL.md) | `HttpPostedFile`, `IFormFile`, `SaveAs`, `CopyToAsync` |
| 文件读取 | [dotnet-file-read-audit](dotnet-file-read-audit/SKILL.md) | `File.ReadAllText`, `FileStream`, `Response.WriteFile`, `PhysicalFile` |
| 反序列化 | [dotnet-deserialization-audit](dotnet-deserialization-audit/SKILL.md) | `BinaryFormatter`, `SoapFormatter`, `LosFormatter`, `ObjectStateFormatter`, `TypeNameHandling`, Remoting, ViewState |
| 命令/动态代码执行 | [dotnet-command-exec-audit](dotnet-command-exec-audit/SKILL.md) | `Process.Start`, `ProcessStartInfo`, PowerShell, CodeDom/Roslyn, XAML/XSLT, `Assembly.Load` |
| SSRF | [dotnet-ssrf-audit](dotnet-ssrf-audit/SKILL.md) | `HttpClient`, `WebRequest`, `AllowAutoRedirect`, DNS/URL parser, metadata, proxy headers |
| 配置密钥 | [dotnet-config-secrets-audit](dotnet-config-secrets-audit/SKILL.md) | `machineKey`, `connectionStrings`, JWT/OAuth/SAML secret, Swagger/ELMAH/Hangfire |
| Web 风险 | [dotnet-web-risk-audit](dotnet-web-risk-audit/SKILL.md) | XSS, CSRF/SameSite, CORS, Host Header, Open Redirect, IDOR/BOLA/BFLA, cache/request smuggling |

## Shared Reference

| 文件 | 用途 |
|:-----|:-----|
| [DOTNET_ATTACK_SURFACE_TAXONOMY.md](shared/DOTNET_ATTACK_SURFACE_TAXONOMY.md) | `surface_index.json` 分类、字段和推荐 skill 映射 |
| [DOTNET_DECOMPILE_STRATEGY.md](shared/DOTNET_DECOMPILE_STRATEGY.md) | dnSpy 反编译策略、失败处理和来源标注 |
| [DOTNET_OUTPUT_STANDARD.md](shared/DOTNET_OUTPUT_STANDARD.md) | 输出完整性、证据字段、禁止省略规则 |
| [SEVERITY_RATING.md](shared/SEVERITY_RATING.md) | 风险评级标准 |
| [REDTEAM_LAB_BOUNDARY.md](shared/REDTEAM_LAB_BOUNDARY.md) | 授权实验室边界和默认无害验证规则 |

## 关键 Reference

| 专题 | 结构化 reference |
|:-----|:-----------------|
| Minimal API 路由与过滤器 | [MINIMAL_API_ROUTES_AND_FILTERS.md](dotnet-minimal-api-audit/references/MINIMAL_API_ROUTES_AND_FILTERS.md) |
| Blazor 渲染与 XSS | [BLAZOR_RENDERING_XSS.md](dotnet-blazor-audit/references/BLAZOR_RENDERING_XSS.md) |
| SignalR Hub 鉴权 | [HUB_AUTHORIZATION.md](dotnet-signalr-audit/references/HUB_AUTHORIZATION.md) |
| 反序列化 11 类 formatter | [FORMATTER_PLAYBOOK.md](dotnet-deserialization-audit/references/FORMATTER_PLAYBOOK.md) |
| ViewState / machineKey | [VIEWSTATE_MACHINEKEY.md](dotnet-deserialization-audit/references/VIEWSTATE_MACHINEKEY.md) |
| 类型控制与 gadget 条件 | [TYPE_CONTROL_AND_GADGETS.md](dotnet-deserialization-audit/references/TYPE_CONTROL_AND_GADGETS.md) |
| 命令执行 sink | [COMMAND_EXEC_SINKS.md](dotnet-command-exec-audit/references/COMMAND_EXEC_SINKS.md) |
| 命令执行无害验证 | [SAFE_VALIDATION.md](dotnet-command-exec-audit/references/SAFE_VALIDATION.md) |
| SSRF 模式 | [SSRF_PATTERNS.md](dotnet-ssrf-audit/references/SSRF_PATTERNS.md) |
| URL parser / redirect / DNS | [URL_PARSER_AND_REDIRECTS.md](dotnet-ssrf-audit/references/URL_PARSER_AND_REDIRECTS.md) |
| 远程导入与 metadata 链 | [IMPORT_AND_METADATA_CHAINS.md](dotnet-ssrf-audit/references/IMPORT_AND_METADATA_CHAINS.md) |
| 配置密钥清单 | [CONFIG_SECRETS_CHECKLIST.md](dotnet-config-secrets-audit/references/CONFIG_SECRETS_CHECKLIST.md) |
| machineKey / token 影响 | [MACHINEKEY_TOKEN_IMPACT.md](dotnet-config-secrets-audit/references/MACHINEKEY_TOKEN_IMPACT.md) |
| 部署暴露与 IIS | [DEPLOYMENT_EXPOSURE.md](dotnet-config-secrets-audit/references/DEPLOYMENT_EXPOSURE.md) |
| Web 风险模式 | [WEB_RISK_PATTERNS.md](dotnet-web-risk-audit/references/WEB_RISK_PATTERNS.md) |
| 业务授权 | [BUSINESS_AUTHORIZATION.md](dotnet-web-risk-audit/references/BUSINESS_AUTHORIZATION.md) |
| 浏览器与代理边界 | [BROWSER_AND_PROXY_BOUNDARIES.md](dotnet-web-risk-audit/references/BROWSER_AND_PROXY_BOUNDARIES.md) |

## Raw 归档

raw 只作追溯材料，默认不直接装入主上下文。

| 归档 | 数量 | 索引 |
|:-----|----:|:-----|
| .NET 反序列化 11 课 | 11 个 lesson | [RAW_REFERENCE_INDEX.md](dotnet-deserialization-audit/references/RAW_REFERENCE_INDEX.md) |
| hack-skills | 18 类 skill family / 29 个 md | [RAW_REFERENCE_INDEX.md](dotnet-offsec-audit/references/RAW_REFERENCE_INDEX.md) |

使用规则：

- 结构化 reference 不足以判断时再读取 raw。
- 引用 raw 时记录来源路径和提炼结论。
- 不把 raw 中的攻击样例原样输出到最终报告。

## 攻击面索引脚本

```powershell
python .\dotnet-offsec-audit\scripts\collect_dotnet_surface.py <source_path> -o <output_path>\surface
```

输出：

- `surface_index.json`
- `attack_surface_matrix.md`

每条 finding 必须包含：

- `category`
- `rule_id`
- `severity_hint`
- `recommended_skill`
- `confidence`
- `evidence_kind`
- `file`
- `line`
- `snippet`

## 维护检查

新增规则或专项时同步：

1. 对应 `SKILL.md`。
2. 对应 `references/`。
3. [shared/DOTNET_ATTACK_SURFACE_TAXONOMY.md](shared/DOTNET_ATTACK_SURFACE_TAXONOMY.md)。
4. [dotnet-offsec-audit/scripts/collect_dotnet_surface.py](dotnet-offsec-audit/scripts/collect_dotnet_surface.py)。
5. [dotnet-audit-pipeline/SKILL.md](dotnet-audit-pipeline/SKILL.md) 与 [quality_check_templates.md](dotnet-audit-pipeline/references/quality_check_templates.md)。
6. 根目录 [README.md](../README.md)。
