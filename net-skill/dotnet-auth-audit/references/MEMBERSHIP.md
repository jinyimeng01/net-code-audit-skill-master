# ASP.NET Membership 审计

## 识别

- `Membership.ValidateUser`, `Roles.IsUserInRole`, `Profile`, `SqlMembershipProvider`
- `web.config`: `<membership>`, `<roleManager>`, `<machineKey>`
- Forms Authentication 与 Membership 混合使用

## 风险点

- 密码策略、锁定策略、重置流程配置过弱。
- `FormsAuthentication.SetAuthCookie` 在未完成二次校验前调用。
- 角色从可控字段、Cookie、QueryString 或隐藏表单读取。
- 自定义 provider SQL 拼接或错误处理泄露用户枚举信息。
- machineKey 泄露导致 FormsAuth ticket 风险。

## 审计要求

- 映射登录、注册、重置密码、修改邮箱、角色变更接口。
- 检查认证成功和授权决策是否分离。
- 检查 Membership provider 连接串和 SQL 实现。
- 修复建议包含强密码/锁定、统一授权、角色服务端查询、machineKey 轮换。
