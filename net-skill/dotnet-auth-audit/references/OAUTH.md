# OAuth / OIDC 审计

## 识别

- `AddOAuth`, `AddOpenIdConnect`, `AddJwtBearer`, `Authority`, `ClientId`, `ClientSecret`
- `CallbackPath`, `SignedOutCallbackPath`, `ResponseType`, `SaveTokens`
- `redirect_uri`, `state`, `nonce`, `code_verifier`

## 风险点

- redirect URI 宽松匹配、通配子域、Open Redirect 串联。
- `state`、`nonce`、PKCE 缺失或未绑定会话。
- 使用前端可控 claim 决定角色或租户。
- token audience/issuer/signature/lifetime 校验缺失。
- `SaveTokens=true` 后 token 泄露到日志、cookie 或异常页。

## 审计要求

- 检查登录、绑定账号、回调、登出、刷新 token 全流程。
- 检查 claim 到本地用户/角色的映射代码。
- 检查回调 URL 构造是否受 Host Header 或配置污染。
- 修复建议包含严格 redirect allowlist、state/nonce/PKCE、issuer/audience/signature 校验、token 最小化存储。
