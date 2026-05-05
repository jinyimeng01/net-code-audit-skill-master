# .NET 反序列化矩阵

本矩阵提炼自本项目 11 课 .NET 反序列化资料和通用攻防参考，仅用于授权代码审计与隔离实验室验证。

## Formatter 与审计点

| 主题 | Sink | 触发条件 | 审计关键点 | 修复 |
|---|---|---|---|---|
| XmlSerializer | `new XmlSerializer(type)` + `Deserialize` | `type` 或 XML 类型信息可控 | `Type.GetType(input)`、`xsi:type`、ODP/XAML 相关类型 | 固定 DTO 类型，禁止外部类型名 |
| Json.NET | `JsonConvert.DeserializeObject` | `TypeNameHandling` 非 `None` | `$type`、全局 `JsonSerializerSettings`、缺少 binder | `TypeNameHandling.None`，严格 binder |
| Fastjson/.NET 变体 | `JSON.ToObject` / auto type | auto type 或类型名可控 | `Type` 字段、对象实例化边界 | 禁用 auto type，固定类型 |
| JavaScriptSerializer | `Deserialize` / `DeserializeObject` | 使用 `SimpleTypeResolver` | `__type` / `__serverType` 解析 | 不使用 resolver，使用固定模型 |
| .NET Remoting | `SoapServerFormatterSinkProvider` / `BinaryServerFormatterSinkProvider` | channel 暴露且 `TypeFilterLevel.Full` | HTTP/TCP channel、端口、formatter provider | 禁用 Remoting 或限制内网与 Low filter |
| DataContractSerializer | `ReadObject` | resolver/KnownTypes 边界错误 | `KnownTypes` 是否含危险类型、输入来源 | 固定 contract，最小 KnownTypes |
| NetDataContractSerializer | `ReadObject` / `Deserialize` | 不可信 XML 带完整类型信息 | `z:Type` / assembly 信息可控 | 不处理外部数据，替换 serializer |
| SoapFormatter | `Deserialize` | 不可信 SOAP/XML 流 | 文件/HTTP/XML 输入到 formatter | 移除 formatter |
| BinaryFormatter | `Deserialize` / `UnsafeDeserialize` | 不可信二进制/Base64 流 | `AAEAAAD`、Cookie、文件、队列 | 移除 formatter，使用安全 DTO |
| ObjectStateFormatter | `Deserialize` | 外部字符串或 ViewState 相关输入可控 | `__VIEWSTATE`、MAC、machineKey | 启用 MAC，保护 machineKey |
| LosFormatter | `Deserialize` | ViewState 或外部字符串可控 | `enableViewStateMac=false`、泄露 machineKey | 启用 MAC/UserKey，轮换 machineKey |

## 常见类型控制标记

- JSON: `$type`, `__type`, `__serverType`
- XML: `xsi:type`, `z:Type`, `type=`, assembly-qualified name
- ViewState: `__VIEWSTATE`, `__EVENTVALIDATION`, base64 前缀
- Binary: `AAEAAAD`, `AAEAAAD/////`

## 误报排除

- 固定 `typeof(SafeDto)` 且输入只填充字段，通常不是类型控制。
- Json.NET `TypeNameHandling.None` 且没有全局覆盖，通常不可利用。
- 自定义 binder 如果严格 allowlist 到业务 DTO，可降级。
- ViewState 有 MAC、未泄露 machineKey、使用 `ViewStateUserKey`，通常不可伪造。

## 实验室验证提示

需要 ysoserial.net、ODP、ActivitySurrogateSelector、TypeConfuseDelegate 等链时，仅在隔离实验室使用；默认报告只写链路类型、依赖条件和无害证明，不输出生产可投递 payload。
