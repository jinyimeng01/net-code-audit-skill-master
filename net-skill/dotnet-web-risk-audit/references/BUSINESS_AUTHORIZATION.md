# 业务授权与对象级权限

## 必查对象参数

- `userId`, `accountId`, `tenantId`, `orgId`, `companyId`
- `role`, `roleId`, `permission`, `isAdmin`
- `ownerId`, `createdBy`, `departmentId`
- `status`, `state`, `workflowStep`
- `price`, `discount`, `amount`, `quota`

## .NET 常见模式

- Controller 有 `[Authorize]`，Service/Repository 没有对象归属校验。
- EF 查询使用 `Find(id)` 后直接返回，没有追加 `OwnerId == currentUser`。
- DTO/model binding 接收了服务端应控制的字段。
- 管理接口只靠路由前缀或菜单隐藏。
- 多租户系统只在前端传 `tenantId`，后端不从登录态绑定。

## 验证思路

- 至少使用两个授权测试主体或两个对象。
- 证明“主体 A 的凭据 + 对象 B 的 ID”能否访问或修改。
- 对状态机问题，证明是否能跳过前置状态。
- 对批量赋值，证明隐藏字段是否被后端接受。

## 修复

- 对象查询强制绑定当前用户/租户。
- 服务层集中授权，不能只依赖 Controller 属性。
- DTO allowlist，禁止绑定敏感字段。
- 状态迁移服务端校验。
