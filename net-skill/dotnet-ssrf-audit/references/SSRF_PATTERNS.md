# .NET SSRF 模式

## 出站请求 Sink

- `HttpClient.GetAsync/PostAsync/SendAsync`
- `WebClient.DownloadString/DownloadFile/OpenRead`
- `WebRequest.Create`, `HttpWebRequest`
- `GrpcChannel.ForAddress`
- SOAP/WCF 客户端 endpoint
- 图片、文件、PDF、Office、SVG、SAML/OIDC metadata 远程导入
- 代理、webhook、URL preview、RSS/Atom、HTML to PDF

## .NET 审计重点

| 点 | 问题 |
|---|---|
| `Uri` 构造 | 相对 URL、userinfo、IDN、IPv6、默认端口、反斜杠解析 |
| `HttpClientHandler.AllowAutoRedirect` | 302/307 后是否重新校验最终 host/IP |
| DNS 解析 | 校验 host 后是否锁定最终 IP，是否防 DNS rebinding |
| Proxy | 系统代理、环境变量、自定义 proxy 是否可控 |
| Timeout | SSRF 端口探测和 DoS 影响 |
| Response handling | 是否回显响应、保存到文件、解析 XML/JSON |

## 高危条件

- 用户可传完整 URL。
- 只用字符串 `StartsWith` / `Contains` / `EndsWith` 做 allowlist。
- 允许重定向且只校验第一跳。
- 没有阻止 loopback、private、link-local、metadata 地址。
- 出站响应进入文件写入、反序列化、XML 解析或模板渲染。

## 安全实现

- 业务上固定目的地，不接受完整 URL。
- parse、decode、normalize、DNS resolve 后再校验。
- 每次重定向后重新校验。
- 网络层 egress ACL 阻止私网和 metadata。
- 响应大小、Content-Type、超时、下载路径都要限制。
