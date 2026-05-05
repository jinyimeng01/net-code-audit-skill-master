---
name: dotnet-command-exec-audit
version: 2.0.0
description: .NET 命令执行与动态代码执行审计 skill。覆盖 Process.Start、ProcessStartInfo、PowerShell、CodeDomProvider、Roslyn、XAML/XSLT、Assembly.Load、插件机制、MSBuild/InstallUtil。追踪用户可控输入到代码执行 sink，输出无害验证证据和修复建议。
description_en: .NET command execution & dynamic code loading audit skill. Covers Process.Start, ProcessStartInfo, PowerShell, CodeDom, Roslyn, XAML/XSLT, Assembly.Load, plugin mechanisms, MSBuild/InstallUtil. Traces user input to code-execution sinks.
author: net-code-audit-team
tags: ['dotnet', 'command-injection', 'rce', 'code-execution', 'powershell']
compatibility: ['asp.net', 'asp.net-core', 'wcf', 'iis']
---

# .NET 命令与动态代码执行审计

目标是证明“外部输入能否影响可执行程序、参数、动态代码或加载路径”。详细 sink 参考 [COMMAND_EXEC_SINKS.md](references/COMMAND_EXEC_SINKS.md)，动态验证边界参考 [SAFE_VALIDATION.md](references/SAFE_VALIDATION.md)。

## 工作流

1. 搜索命令和代码执行 sink：`Process.Start`、`ProcessStartInfo`、`cmd.exe`、`powershell`、`CodeDomProvider`、`CSharpScript`、`XamlReader.Parse`、`Assembly.Load`、`Type.GetType`、`InvokeMember`。
2. 追踪输入来源：路由参数、上传文件名、配置项、模板内容、导入文件、队列消息、数据库可写字段。
3. 判断控制面：可执行路径、命令参数、shell 开关、工作目录、环境变量、动态源码、程序集字节、XSLT 扩展对象。
4. 分析防护：参数数组化、白名单、固定可执行文件、禁止 shell、路径规范化、签名校验、沙箱/低权限账户。
5. 需要时调用 [dotnet-route-tracer](../dotnet-route-tracer/SKILL.md) 证明入口到 sink 可达。
6. 如需验证，先按 [SAFE_VALIDATION.md](references/SAFE_VALIDATION.md) 选择无害证据。

## 分级

- Critical：未认证或低权限用户可影响命令/动态代码并执行。
- High：认证用户可执行命令，或可写插件/脚本/模板导致代码执行。
- Medium：仅能控制参数造成敏感文件操作、SSRF 转命令、有限工具参数注入。
- Low：仅内部配置可控或需要本地管理员权限。

## 输出要求

- 漏洞编号格式：`{C/H/M/L}-CMD-{序号}`。
- 记录入口、参数、sink、可控字段、执行身份、工作目录、部署平台 Windows/Linux/IIS/Kestrel。
- 默认 PoC 使用无害命令或行为差异证明，例如固定字符串回显、临时文件名、DNS callback；不要默认生成破坏性命令。
- 修复建议必须给出替代 API、参数白名单、禁用 shell、签名校验和最小权限运行账户。

## 自检

- 区分命令注入、参数注入、动态代码执行、插件加载、反射调用。
- 对每个风险说明执行条件，不把不可达工具调用误报为 RCE。
