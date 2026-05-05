# machineKey、Token 与认证影响

## machineKey

`machineKey` 影响 ASP.NET Framework 的多类安全边界。

| 功能 | 影响 |
|---|---|
| Forms Authentication | 可能伪造或篡改认证票据 |
| ViewState MAC | 可配合 ViewState/LosFormatter 风险 |
| AntiForgeryToken | 可能影响 token 完整性 |
| 多节点部署 | 复用密钥导致一个节点泄露影响全站 |

## JWT / OAuth / OIDC

检查：

- `IssuerSigningKey`、`SigningCredentials`、`TokenValidationParameters`。
- 是否关闭 `ValidateIssuerSigningKey`、`ValidateIssuer`、`ValidateAudience`、`ValidateLifetime`。
- `ClientSecret` 是否出现在前端配置、日志或异常页。
- token 是否保存在不安全 Cookie、localStorage 或明文日志。

## SAML

检查：

- 私钥文件路径和读取权限。
- 是否验证签名、Audience、Recipient、InResponseTo、NotBefore/NotOnOrAfter。
- 是否允许 unsigned assertion 或只签 Response 不签 Assertion 的混淆。

## 轮换建议

- 泄露密钥立即轮换，并失效相关 token/session。
- 缩小密钥权限和有效期。
- 使用托管密钥服务或受限 secret store。
- 清理历史日志、备份、发布包。
