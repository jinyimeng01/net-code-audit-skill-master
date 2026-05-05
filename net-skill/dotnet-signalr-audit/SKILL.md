---
name: dotnet-signalr-audit
version: 2.0.0
description: .NET SignalR 安全审计 skill。覆盖 Hub、HubContext、HubLifetimeManager、连接鉴权、组管理、消息广播、流处理、WebSocket 传输层。追踪用户可控输入到消息处理、命令执行、信息泄露等 sink，输出鉴权绕过、消息伪造和拒绝服务证据。
description_en: .NET SignalR security audit skill. Covers Hub, HubContext, HubLifetimeManager, connection authentication, group management, message broadcasting, streaming, and WebSocket transport. Traces user input to message processing, command execution, and information disclosure sinks.
author: net-code-audit-team
tags: ["dotnet","signalr","websocket","hub","message-broadcast","auth-bypass","audit"]
compatibility: ["asp.net-core"]
---

# .NET SignalR 审计

检查 ASP.NET Core SignalR 的 Hub 鉴权、消息处理、组管理和传输层中的安全风险。

## 工作流

1. 搜索所有 `Hub` 子类、`IHubContext<T>` 注入点、`HubLifetimeManager` 自定义实现。
2. 检查 Hub 方法上的 `[Authorize]` / `[AllowAnonymous]`，确认是否存在未鉴权的 admin/管理方法。
3. 检查 `OnConnectedAsync`、`OnDisconnectedAsync` 中的用户身份验证和组分配逻辑。
4. 检查 `Clients.Group`、`Clients.User`、`Clients.Client` 等目标选择器，确认是否存在组名/用户名校验绕过。
5. 检查 Hub 方法参数中的用户可控输入是否传递到 SQL、文件、命令、反序列化 sink。
6. 检查流处理（`ChannelReader<T>` / `IAsyncEnumerable<T>`）中的资源耗尽和 DoS 风险。
7. 检查 CORS 配置和 WebSocket 升级请求中的 Origin 校验。
8. 检查 `HubPipelineModule` / `IHubFilter` 中的输入校验和异常处理，确认是否泄露敏感信息。
9. 输出漏洞或排除理由；默认只给无害验证和修复建议。

## Reference 选择

| 任务 | 读取 |
|---|---|
| Hub 鉴权与访问控制 | [HUB_AUTHORIZATION.md](references/HUB_AUTHORIZATION.md) |
| 消息与组管理安全 | [MESSAGE_AND_GROUP_SECURITY.md](references/MESSAGE_AND_GROUP_SECURITY.md) |
| 传输层与 CORS | [TRANSPORT_AND_CORS.md](references/TRANSPORT_AND_CORS.md) |

## 高危 sink 速查

| Sink | 危险条件 |
|---|---|
| Hub 方法无 `[Authorize]` | 敏感操作允许匿名调用 |
| `Clients.Group(userControlledGroup)` | 组名可控导致消息发送到未授权用户 |
| `Context.UserIdentifier` 信任过度 | 未验证的 user ID 用于数据库查询或文件操作 |
| `ChannelReader` 无大小限制 | 客户端发送超大流导致内存耗尽 |
| `IAsyncEnumerable` 无取消令牌 | 长时间流占用资源，拒绝服务 |
| WebSocket 升级无 Origin 校验 | 跨站 WebSocket 连接伪造 |

## 输出要求

- 漏洞编号格式：`{C/H/M/L}-SIGNALR-{序号}`。
- 必须说明 Hub 名、方法名、鉴权属性、消息目标选择器、调用链、sink。
- 修复优先建议：Hub 方法统一鉴权、组名白名单、消息大小限制、流超时/取消、WebSocket Origin 校验。

## 自检

- [ ] 已覆盖全部 Hub 类和公开方法。
- [ ] 已检查所有 Hub 方法的鉴权属性。
- [ ] 已评估组名/用户 ID 的可控性和校验。
- [ ] 已检查流处理中的资源限制和 DoS 风险。
- [ ] 每个 sink 都有输入可控性结论。
