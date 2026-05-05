# .NET 攻击面分类

用于统一 surface collector、总控流水线和专项 skill 的分类。

`surface_index.json` 兼容旧字段，并要求每条 finding 具备以下字段：

- `category`: 下表分类。
- `rule_id`: 具体命中规则。
- `severity_hint`: 静态风险提示，不等同最终评级。
- `recommended_skill`: 后续推荐专项。
- `confidence`: `High` / `Medium` / `Low`，表示静态证据可信度。
- `evidence_kind`: `sink`、`config`、`route-declaration`、`type-control`、`proxy-header` 等证据类型。
- `file`、`line`、`snippet`: 复核位置和最小证据。

| 分类 | 典型 sink / 观察 | 推荐 skill |
|---|---|---|
| route | Controller、Page、Handler、WCF Operation | dotnet-route-mapper |
| auth | Authorize、AllowAnonymous、Middleware、FormsAuth、JWT、OAuth | dotnet-auth-audit |
| sql | SqlCommand、FromSqlRaw、Dapper Query、HQL | dotnet-sql-audit |
| xxe | XmlDocument、XmlReader、XDocument、XmlSerializer、XslCompiledTransform | dotnet-xxe-audit |
| file-read | File.ReadAllText、FileStream、Response.WriteFile、PhysicalFile | dotnet-file-read-audit |
| file-upload | HttpPostedFile、IFormFile、SaveAs、CopyToAsync | dotnet-file-upload-audit |
| deserialization | BinaryFormatter、SoapFormatter、LosFormatter、ObjectStateFormatter、TypeNameHandling、UnsafeDeserializeMethodResponse、ViewState、PSObject | dotnet-deserialization-audit |
| command-exec | Process.Start、ProcessStartInfo、PowerShell、CodeDom、Roslyn、XAML/XSLT、Assembly.Load、MSBuild/InstallUtil | dotnet-command-exec-audit |
| ssrf | HttpClient、WebRequest、WebClient、AllowAutoRedirect、Uri/Dns/IPAddress、metadata、X-Original-URL、X-Rewrite-URL | dotnet-ssrf-audit |
| config-secret | machineKey、connectionStrings、JWT/OAuth/SAML secret、证书私钥、debug、ELMAH、Hangfire、Swagger | dotnet-config-secrets-audit |
| web-risk | XSS、CSRF/SameSite、CORS Origin、Open Redirect、Host Header、IDOR/BOLA/BFLA、IIS/cache/request smuggling | dotnet-web-risk-audit |
| minimal-api | MapGet/MapPost/MapPut/MapDelete/MapPatch、EndpointFilter、RequestDelegate、Source Generator、OpenAPI | dotnet-minimal-api-audit |
| blazor | Blazor Server/WASM、IJSRuntime、MarkupString、Circuit、AuthenticationStateProvider | dotnet-blazor-audit |
| signalr | Hub、HubContext、HubLifetimeManager、WebSocket、Group、Message broadcast | dotnet-signalr-audit |

## 优先级默认值

1. 未认证入口 + RCE/反序列化/命令执行/file-write。
2. 未认证入口 + 文件读取/SSRF/SQL 注入/XXE。
3. 认证入口 + 越权/IDOR/敏感数据。
4. 配置密钥泄露与组件漏洞，需要结合可达入口再定级。
