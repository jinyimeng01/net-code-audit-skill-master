# .NET 攻防审计路由矩阵

先从 `surface_index.json` 和 route/auth 结果中选专项，不要凭单个关键字直接下漏洞结论。

| 发现 | 下一步 |
|---|---|
| `AllowAnonymous` 管理接口 | auth-audit -> web-risk -> route-tracer |
| `TypeNameHandling` / `$type` / formatter | deserialization-audit |
| `Process.Start` / `PowerShell` / `CodeDomProvider` | command-exec-audit |
| `HttpClient` 目标 URL 可控 | ssrf-audit |
| `machineKey` 或 JWT signing key | config-secrets-audit -> deserialization/auth |
| 上传后可访问路径 | file-upload-audit -> command-exec/deserialization |
| XML/SOAP/OOXML/SVG 导入 | xxe-audit -> ssrf-audit |
| ID、tenantId、role、price、status | web-risk-audit |

## 分析顺序

1. 入口和鉴权。
2. 参数可控性。
3. Sink 类型。
4. 防护和规范化。
5. 可达性和执行条件。
6. 无害验证。
7. 修复与残余风险。
