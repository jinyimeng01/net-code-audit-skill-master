# 类型控制与 Gadget 审计

本文件只用于判断风险和实验室验证条件，不默认输出可投递 payload。

## 类型控制来源

| 格式 | 标记 |
|---|---|
| Json.NET | `$type` |
| JavaScriptSerializer | `__type`, `__serverType` |
| XML | `xsi:type`, `z:Type`, `type`, assembly-qualified name |
| 代码 | `Type.GetType(input)`, `Activator.CreateInstance`, custom binder |
| ViewState | `__VIEWSTATE` + machineKey/MAC 条件 |

## 常见 Gadget 条件

| Gadget / 类型 | 依赖条件 |
|---|---|
| `ObjectDataProvider` | WPF/PresentationFramework 可用，属性赋值可触发方法调用 |
| `ExpandedWrapper` | 常见于 XmlSerializer/Json.NET 链中辅助包装类型 |
| `ActivitySurrogateSelector` | 依赖特定 .NET Framework 类型和 formatter 行为 |
| `PSObject` | PowerShell 相关程序集/类型可用 |
| `MulticastDelegate` | 委托链类型控制，常见于 NetDataContract/Los 等研究链 |
| `WindowsIdentity` / `ClaimsIdentity` | ISerializable 构造、身份对象反序列化边界 |
| `TypeConfuseDelegate` | BinaryFormatter/LosFormatter 实验室常见链 |

## 审计重点

- 不要只看 formatter 名称，还要看应用加载的程序集。
- 检查 `bin/`、`.deps.json`、`packages.config`、`.csproj` 中是否引用 WPF、System.Activities、PowerShell、Telerik、DotNetNuke、ServiceStack。
- 检查 binder 是否能阻止系统类型、WPF 类型、委托类型、反射类型。
- 检查反序列化发生的运行账号和权限。

## 报告措辞

- `Confirmed`: 授权实验室无害验证成功。
- `Reachable`: 类型控制与 sink 可达，但未执行 payload。
- `Potential`: formatter 存在，输入可控或 gadget 条件未完全确认。
- `Not exploitable`: 固定 DTO、严格 binder、不可达或签名保护有效。
