# URL Parser、重定向与 DNS 绕过检查

## URL 混淆点

| 类型 | 审计说明 |
|---|---|
| userinfo | `trusted.com@target` 使人工校验和实际 host 混淆 |
| 反斜杠 | 浏览器、代理、.NET `Uri` 对 `\` 处理可能不同 |
| 编码 | 单次/多次 decode 顺序影响 allowlist |
| IDN/punycode | Unicode host 与 ASCII host 比较不一致 |
| IPv6 | `[::1]`、IPv4-mapped IPv6 |
| 整数/短地址 | 某些库或代理可能接受非标准 IP 表达 |
| trailing dot | `example.com.` 与 `example.com` |

## 重定向链

审计 `AllowAutoRedirect` 和手动处理 `Location`。

- 校验第一跳不够，必须校验每一跳。
- 允许 HTTP 到 HTTPS 不代表允许 HTTPS 到 HTTP。
- 301/302/303/307/308 都要考虑。
- 限制最大跳数和最终 IP。

## DNS rebinding

危险模式：

1. 代码校验 `Uri.Host` 或第一次 DNS 结果。
2. 真实请求时重新解析。
3. 攻击域名在第二次解析返回私网地址。

防护：

- 解析后固定 IP 连接，或在连接前校验最终 remote endpoint。
- 禁止私网/loopback/link-local。
- 出网 ACL 作为最后防线。

## 无害验证

- 使用授权 callback 域名证明出站。
- 使用本地 mock server 验证重定向重校验。
- 不默认访问真实云 metadata 地址。
