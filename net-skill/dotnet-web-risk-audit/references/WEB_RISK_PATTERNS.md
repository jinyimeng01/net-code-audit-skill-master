# .NET Web 风险模式

## XSS

- Razor 默认编码被 `Html.Raw`、`MvcHtmlString.Create`、自定义 `IHtmlContent` 绕过。
- WebForms 中 `ValidateRequest=false`、`RequestValidationMode=2.0`、直接 `Response.Write`。
- 前端 JSON 注入关注 `JavaScriptStringEncode`、HTML attribute context、URL context。
- 富文本、Markdown、文件预览、SVG 上传要和 upload/XXE 联动检查。

## CSRF

- MVC/Core 表单缺少 `[ValidateAntiForgeryToken]` 或全局 antiforgery。
- JSON API 依赖 Cookie 认证但没有 token 或 SameSite 策略。
- GET/无幂等接口执行状态变更。
- `SameSite=None` 必须配合 Secure，并确认跨站业务必要性。

## CORS

- `AllowAnyOrigin` 与凭据组合。
- 动态反射 Origin，或 allowlist 使用 `EndsWith` / regex 错误。
- `Origin: null`、子域接管、Unicode/punycode、端口混淆。
- 缺少 `Vary: Origin` 可能造成缓存污染。

## Open Redirect / Host Header

- `Redirect(returnUrl)`、`LocalRedirect` 误用、OAuth redirect_uri 拼接。
- `Request.Url`、`Request.Host` 构造密码重置、邀请链接、回调链接。
- `X-Forwarded-Host`、`ForwardedHeadersOptions` 未限制 KnownProxies/KnownNetworks。
- IIS/代理关注 `X-Original-URL`、`X-Rewrite-URL`、absolute-URI request line、double Host。

## IDOR / BOLA / BFLA

- URL/body/header 中的 `id`、`userId`、`tenantId`、`orgId`、`role`、`status`、`price`。
- 只校验登录，不校验对象归属。
- DTO 批量绑定允许用户写入 `IsAdmin`、`Role`、`OwnerId`。
- 后台接口只靠前端隐藏按钮控制。

## IIS、缓存、请求边界

- 短文件名枚举、危险 handler/module、目录浏览、备份文件下载。
- `requestFiltering`、`handlers`、`modules` 与 URL rewrite 顺序不当。
- 缓存 key 未包含 Host/Origin/Authorization。
- 反向代理和 Kestrel/IIS header 解析差异可能放大请求走私或 host routing 风险。
