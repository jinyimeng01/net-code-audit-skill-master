# Windows Authentication 审计

## 识别

- `web.config`: `<authentication mode="Windows">`
- IIS: Windows Authentication enabled, Anonymous disabled/enabled 混用
- ASP.NET Core: `AddNegotiate()`, IIS Integration, `HttpSysOptions.Authentication`
- 代码: `User.Identity.Name`, Windows groups, `IsInRole`

## 风险点

- 生产环境同时开启 Anonymous，导致部分路由绕过 Windows Auth。
- 仅依赖前端或代理传入的用户名 header。
- 组名/域名大小写、别名、嵌套组处理错误。
- Kerberos/NTLM 代理部署中 `ForwardedHeaders` 或双跳配置错误。

## 审计要求

- 对每条路由标注是否需要 Windows 身份。
- 检查匿名访问与 Windows 认证的 IIS/module 顺序。
- 检查角色判断是否覆盖对象归属和租户边界。
- 修复建议包含 IIS 认证统一、后端强制授权、最小组权限。
