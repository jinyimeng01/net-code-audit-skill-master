# .NET 反序列化 Formatter Playbook

本文件是默认结构化参考，提炼 11 课原文和通用攻防经验。需要逐字追溯时再读取 `references/raw/deserialization/`。

## 快速判定模型

| 问题 | 高危答案 |
|---|---|
| 输入来自哪里 | HTTP body、Cookie、ViewState、上传文件、队列、Remoting channel、数据库中用户可写字段 |
| 类型是否可控 | `Type.GetType(input)`、`$type`、`__type`、`__serverType`、`xsi:type`、assembly-qualified name |
| 对象图是否可控 | Binary/Base64/XML/JSON 直接进入 formatter |
| 有无防护 | 严格 binder、固定 DTO、ViewState MAC、`ViewStateUserKey`、签名/加密、KnownTypes allowlist |
| 是否可达 | 从 route/auth/tracer 可证明入口到 formatter sink |

## 1. XmlSerializer

**常见 sink**

- `new XmlSerializer(Type.GetType(input))`
- `new XmlSerializer(userControlledType)`
- `serializer.Deserialize(XmlReader|Stream|TextReader)`

**危险条件**

- `XmlSerializer` 的目标类型由请求参数、XML 属性、数据库字段或配置文件控制。
- XML 中能影响 `xsi:type`、扩展类型、包装类型或对象图。
- 项目引用 WPF/PresentationFramework、System.Activities、ObjectDataProvider 相关类型，且可进入类型构造/属性赋值路径。

**审计搜索**

```text
XmlSerializer
Type.GetType
GetType(
xsi:type
ObjectDataProvider
ExpandedWrapper
XamlReader
```

**排除条件**

- 固定 `typeof(SafeDto)` 且 DTO 只含普通字段。
- 输入 XML 使用安全 `XmlReaderSettings`，且类型不可控。

**修复**

- 固定反序列化类型，不接受外部 type name。
- 使用 DTO allowlist，不让框架类型进入对象图。
- XML 解析层同时按 XXE 要求禁用 DTD/外部实体。

## 2. Json.NET

**常见 sink**

- `JsonConvert.DeserializeObject(json, settings)`
- `JsonSerializerSettings.TypeNameHandling = TypeNameHandling.All|Auto|Objects|Arrays`
- 全局 MVC/Core Json.NET 配置中启用 TypeNameHandling。

**危险条件**

- 外部 JSON 可带 `$type`。
- `TypeNameHandling` 非 `None`。
- 缺少严格 `ISerializationBinder`，或 binder 按命名空间/前缀宽松放行。

**审计搜索**

```text
TypeNameHandling
JsonConvert.DeserializeObject
JsonSerializerSettings
ISerializationBinder
SerializationBinder
$type
```

**排除条件**

- `TypeNameHandling.None`，没有全局覆盖。
- binder 精确 allowlist 到业务 DTO，不允许系统类型或 UI/WPF 类型。

**修复**

- 禁用 TypeNameHandling。
- 使用固定泛型类型 `DeserializeObject<TDto>()`。
- 如果兼容性必须保留类型名，使用精确 binder 并记录拒绝日志。

## 3. Fastjson / .NET 兼容变体

**常见 sink**

- `JSON.ToObject`
- `DeserializeObject`
- auto type / type 字段驱动对象创建。

**危险条件**

- JSON 中类型字段可控。
- 运行时允许按字符串实例化任意类型。
- 反序列化类型不是固定 DTO。

**审计重点**

- 找 `Type`、`$type`、`@type`、`autoType`、`ToObject`。
- 检查是否能落到 `ProcessStartInfo`、`ObjectDataProvider`、反射调用、文件/网络对象等危险类型。

**修复**

- 禁用 auto type。
- 固定目标类型。
- 对多态业务对象使用显式枚举字段映射，不用 CLR type name。

## 4. JavaScriptSerializer

**常见 sink**

- `new JavaScriptSerializer(new SimpleTypeResolver())`
- `Deserialize<T>()`
- `DeserializeObject()`

**危险条件**

- 使用 `SimpleTypeResolver` 或宽松自定义 resolver。
- 外部 JSON 可控制 `__type` 或 `__serverType`。

**审计搜索**

```text
JavaScriptSerializer
SimpleTypeResolver
JavaScriptTypeResolver
DeserializeObject
__type
__serverType
```

**修复**

- 不使用 `SimpleTypeResolver` 处理外部输入。
- 改用固定 DTO 和安全 JSON serializer。

## 5. .NET Remoting

**常见 sink / 配置**

- `RemotingConfiguration.RegisterWellKnownServiceType`
- `HttpServerChannel` / `TcpServerChannel`
- `SoapServerFormatterSinkProvider`
- `BinaryServerFormatterSinkProvider`
- `TypeFilterLevel.Full`

**危险条件**

- Remoting channel 可被非信任客户端访问。
- formatter provider 使用 Full filter。
- HTTP/TCP channel 暴露到业务网络或公网。

**审计搜索**

```text
System.Runtime.Remoting
HttpServerChannel
TcpServerChannel
IpcServerChannel
TypeFilterLevel.Full
SoapServerFormatterSinkProvider
BinaryServerFormatterSinkProvider
RegisterWellKnownServiceType
```

**排除条件**

- 仅 IPC、本机、强 ACL，且不可被 Web 入口或外部网络访问。
- 已迁移到 WCF/gRPC/HTTP API，Remoting 代码不可达。

**修复**

- 禁用 Remoting。
- 如果遗留系统暂不能移除，限制网络、启用最低 filter、加认证、隔离进程账户。

## 6. DataContractSerializer

**常见 sink**

- `new DataContractSerializer(type)`
- `ReadObject(XmlReader|Stream)`
- `KnownTypes`
- `DataContractResolver`

**危险条件**

- `KnownTypes` 或 resolver 包含危险类型或被外部输入影响。
- 目标类型由外部控制。
- 配合不安全 XML reader 导致 XXE 或类型边界扩大。

**修复**

- 固定 contract。
- KnownTypes 只包含业务 DTO。
- 禁止外部控制 resolver。

## 7. NetDataContractSerializer

**关键差异**

`NetDataContractSerializer` 会保留 CLR 类型和程序集信息，风险接近 BinaryFormatter，不适合处理不可信输入。

**常见 sink**

- `new NetDataContractSerializer()`
- `ReadObject`
- `Deserialize`

**危险条件**

- 外部 XML 可控并进入 `ReadObject`。
- XML 中完整类型信息可控。

**修复**

- 不用于不可信输入。
- 改用 DataContractSerializer + 固定 DTO allowlist。

## 8. SoapFormatter

**常见 sink**

- `new SoapFormatter().Deserialize(stream)`
- `IRemotingFormatter.Deserialize`
- 文件/XML/HTTP SOAP 流进入 formatter。

**危险条件**

- SOAP/XML 流来自用户上传、HTTP 请求、消息队列或远程服务。
- 没有签名或可信来源校验。

**修复**

- 移除 SoapFormatter。
- SOAP 业务改用固定 contract 的 WCF/XmlSerializer DTO，并按 XXE 规则配置 XML reader。

## 9. BinaryFormatter

**常见 sink**

- `BinaryFormatter.Deserialize`
- `UnsafeDeserialize`
- `DeserializeMethodResponse`
- `UnsafeDeserializeMethodResponse`

**危险条件**

- 外部 Base64、Cookie、上传文件、队列消息、缓存字段进入 sink。
- `SerializationBinder` 不存在或宽松。

**指纹**

- Base64 常见前缀：`AAEAAAD`
- 二进制头可见 `00 01 00 00 00` 相关序列。

**修复**

- 完全移除 BinaryFormatter。
- 迁移到 System.Text.Json / protobuf / MessagePack 固定 schema。
- 历史数据迁移必须离线、可信、一次性转换。

## 10. ObjectStateFormatter

**常见场景**

- ViewState 内部对象格式。
- 应用显式调用 `ObjectStateFormatter.Deserialize(string)`.

**危险条件**

- 应用主动反序列化外部字符串。
- ViewState 保护被关闭或 machineKey 泄露。

**修复**

- 不主动处理外部 ObjectStateFormatter 字符串。
- ViewState 按 [VIEWSTATE_MACHINEKEY.md](VIEWSTATE_MACHINEKEY.md) 加固。

## 11. LosFormatter

**常见场景**

- ASP.NET WebForms ViewState / ControlState。
- `LosFormatter.Deserialize` 处理外部字符串。

**危险条件**

- `enableViewStateMac=false`。
- machineKey 泄露或弱密钥。
- 没有 `ViewStateUserKey`，跨用户重放风险更高。

**修复**

- 开启 ViewState MAC 和 EventValidation。
- 配置强随机 machineKey 并轮换泄露密钥。
- 对敏感页面设置 `ViewStateUserKey`。

## 报告字段

每个反序列化发现必须写：

- Formatter / serializer。
- 输入入口与格式。
- 类型控制点。
- 对象图控制点。
- 防护状态。
- 调用链。
- 证据标签：Confirmed / Reachable / Potential / Not exploitable。
- 修复方案和迁移建议。
