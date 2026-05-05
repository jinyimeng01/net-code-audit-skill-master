# 浏览器与代理边界

## CORS 检查

- `AllowAnyOrigin`、`SetIsOriginAllowed(_ => true)`。
- `AllowCredentials` 与动态 Origin。
- regex/EndsWith allowlist。
- `Origin: null`。
- `Vary: Origin`。

## CSRF 检查

- Cookie 认证接口是否都有 antiforgery。
- SameSite 配置是否符合业务。
- JSON API 是否接受 `text/plain`、form-urlencoded 或 GET 状态变更。
- 登录 CSRF、绑定账号 CSRF、OAuth state 缺失。

## Host Header 检查

- 密码重置、邮箱确认、邀请链接是否用 `Request.Host`。
- 是否信任 `X-Forwarded-Host`、`Forwarded`。
- KnownProxies/KnownNetworks 是否配置。
- IIS URL Rewrite 是否使用 `X-Original-URL`、`X-Rewrite-URL`。

## Open Redirect 检查

- `returnUrl`, `redirect`, `next`, `url`, `callback`。
- `Url.IsLocalUrl` 是否使用正确。
- 反斜杠、双编码、协议相对 URL、userinfo、fragment 混淆。
- OAuth redirect_uri 与应用 Open Redirect 串联。
