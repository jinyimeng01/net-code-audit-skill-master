---
name: dotnet-blazor-audit
version: 2.0.0
description: .NET Blazor 安全审计 skill。覆盖 Blazor Server / Blazor WebAssembly 的 Circuit 生命周期、JS Interop、组件渲染、事件处理、状态管理、SignalR 底层连接。追踪用户可控输入到 DOM 操作、命令执行、文件操作等 sink，输出 XSS、信息泄露和 RCE 证据。
description_en: .NET Blazor security audit skill. Covers Blazor Server / Blazor WebAssembly circuit lifecycle, JS Interop, component rendering, event handling, state management, and underlying SignalR connections. Traces user input to DOM manipulation, command execution, and file operation sinks.
author: net-code-audit-team
tags: ["dotnet","blazor","blazor-server","blazor-wasm","xss","js-interop","circuit","audit"]
compatibility: ["asp.net-core"]
---

# .NET Blazor 审计

检查 Blazor Server 和 Blazor WebAssembly 项目的组件渲染、JS Interop、Circuit 和 SignalR 连接中的安全风险。

## 工作流

1. 识别项目类型：`Blazor Server`（`_Host.cshtml` + `App.razor` + Circuit）或 `Blazor WebAssembly`（`wwwroot/index.html` + 客户端下载）。
2. 搜索 `IJSRuntime.InvokeAsync`、`JSInvokable`、`OnAfterRenderAsync` 中的 JS Interop 调用，检查用户输入是否传递到 `eval`、`innerHTML`、`document.write` 或动态脚本加载。
3. 检查组件中的 `@((MarkupString)userInput)`、`@Html.Raw` 等未编码渲染。
4. 检查 `CircuitHandler` 和 `AuthenticationStateProvider` 中的状态管理，确认是否存在会话固定或状态泄露。
5. 检查 `HubConnection` 配置（Blazor Server 底层使用 SignalR），确认是否启用了正确的鉴权和消息校验。
6. 检查 `_Imports.razor` 和共享组件库中的全局指令，确认是否有危险的 using 或服务注册。
7. 检查 `appsettings.json` 中的 API 基地址和 CORS 配置（Blazor WASM）。
8. 追踪用户可控输入到 sink：DOM XSS、命令执行（通过 JS Interop 调用 Node/Electron API）、文件读取/写入（通过浏览器 File API + Blazor 传递）。
9. 输出漏洞或排除理由；默认只给无害验证和修复建议。

## Reference 选择

| 任务 | 读取 |
|---|---|
| Blazor 渲染与 XSS | [BLAZOR_RENDERING_XSS.md](references/BLAZOR_RENDERING_XSS.md) |
| JS Interop 安全 | [JS_INTEROP_SECURITY.md](references/JS_INTEROP_SECURITY.md) |
| Circuit 与状态管理 | [CIRCUIT_STATE_MANAGEMENT.md](references/CIRCUIT_STATE_MANAGEMENT.md) |

## 高危 sink 速查

| Sink | 危险条件 |
|---|---|
| `MarkupString` / `@((MarkupString)input)` | 用户输入未经编码直接渲染 |
| `IJSRuntime.InvokeAsync("eval", ...)` | JS 执行用户可控字符串 |
| `JSInvokable` 方法接收用户输入 | 未校验的输入传递到 DOM 操作或本地 API |
| `CircuitHandler` 中存储敏感数据 | 多用户 Circuit 共享状态导致信息泄露 |
| `HubConnection` 无鉴权 | Blazor Server SignalR 连接允许匿名访问 admin 组件 |

## 输出要求

- 漏洞编号格式：`{C/H/M/L}-BLAZOR-{序号}`。
- 必须说明组件名、渲染模式、JS Interop 调用点、Circuit 状态、调用链、sink。
- 修复优先建议：使用 `@bind` 安全绑定、避免 `MarkupString`、JS Interop 输入校验、Circuit 隔离、SignalR 鉴权。

## 自检

- [ ] 已区分 Blazor Server 与 Blazor WASM。
- [ ] 已检查所有 `IJSRuntime` / `JSInvokable` 调用。
- [ ] 已确认组件渲染中无未编码用户输入。
- [ ] 已评估 Circuit / SignalR 的鉴权和状态隔离。
- [ ] 每个 sink 都有输入可控性结论。
