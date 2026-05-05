---
name: dotnet-deserialization-audit
version: 2.0.0
description: .NET 反序列化漏洞审计 skill。用于授权源码审计或红队实验室中识别和验证 XmlSerializer、Newtonsoft.Json Json.NET TypeNameHandling、Fastjson、JavaScriptSerializer SimpleTypeResolver、.NET Remoting、DataContractSerializer、NetDataContractSerializer、SoapFormatter、BinaryFormatter、ObjectStateFormatter、LosFormatter/ViewState、Telerik/DotNetNuke/ServiceStack 等 .NET 反序列化风险；要求追踪用户可控输入到 Deserialize/ReadObject/formatter sink，并输出安全修复建议和无害验证证据。
description_en: .NET deserialization vulnerability audit skill. Identifies and validates risks in XmlSerializer, Json.NET TypeNameHandling, Fastjson, JavaScriptSerializer, .NET Remoting, DataContractSerializer, NetDataContractSerializer, SoapFormatter, BinaryFormatter, ObjectStateFormatter, LosFormatter/ViewState, and third-party components.
author: net-code-audit-team
tags: ['dotnet', 'deserialization', 'rce', 'formatter', 'viewstate', 'gadget-chain']
compatibility: ['asp.net', 'asp.net-core', 'wcf', 'iis']
---

# .NET 反序列化审计

检查用户可控数据是否进入危险 formatter、类型解析器或 ViewState/Remoting 反序列化路径。先读取 [FORMATTER_PLAYBOOK.md](references/FORMATTER_PLAYBOOK.md)；需要 ViewState 细节读 [VIEWSTATE_MACHINEKEY.md](references/VIEWSTATE_MACHINEKEY.md)；需要类型控制和 gadget 条件读 [TYPE_CONTROL_AND_GADGETS.md](references/TYPE_CONTROL_AND_GADGETS.md)。需要原文追溯时读 [RAW_REFERENCE_INDEX.md](references/RAW_REFERENCE_INDEX.md)，实验室边界读取 [REDTEAM_LAB_BOUNDARY.md](../shared/REDTEAM_LAB_BOUNDARY.md)。

## 工作流

1. 从 route mapper 和 surface index 获取入口、参数、Content-Type、Cookie、Header、文件上传和 SOAP/WCF 入口。
2. 搜索 sink：`Deserialize`、`ReadObject`、`UnsafeDeserialize`、`DeserializeObject`、`TypeNameHandling`、`SimpleTypeResolver`、`BinaryFormatter`、`LosFormatter`、`ObjectStateFormatter`、`NetDataContractSerializer`。
3. 追踪输入来源：Request body、Cookie、ViewState、Session、文件、消息队列、Remoting channel、数据库中的用户可控字段。
4. 判断是否允许类型控制或对象图控制：`Type.GetType(input)`、`$type`、`__type`、`__serverType`、`xsi:type`、ViewState MAC/machineKey、Binder 白名单。
5. 使用 [dotnet-route-tracer](../dotnet-route-tracer/SKILL.md) 证明入口到 sink 的可达性。
6. 输出漏洞或排除理由；默认只给无害验证和修复建议。

## Reference 选择

| 任务 | 读取 |
|---|---|
| 11 类 formatter 总体审计 | [FORMATTER_PLAYBOOK.md](references/FORMATTER_PLAYBOOK.md) |
| ViewState、LosFormatter、machineKey | [VIEWSTATE_MACHINEKEY.md](references/VIEWSTATE_MACHINEKEY.md) |
| ODP、ActivitySurrogateSelector、PSObject、委托链、身份对象 | [TYPE_CONTROL_AND_GADGETS.md](references/TYPE_CONTROL_AND_GADGETS.md) |
| 原始课程复盘 | [RAW_REFERENCE_INDEX.md](references/RAW_REFERENCE_INDEX.md) |

## 高危 sink 速查

| 类型 | 危险条件 |
|---|---|
| `BinaryFormatter` / `SoapFormatter` | 任意不可信流进入 `Deserialize`、`UnsafeDeserialize`、`DeserializeMethodResponse` |
| `LosFormatter` / `ObjectStateFormatter` | ViewState 未启用 MAC、machineKey 泄露、应用主动反序列化外部字符串 |
| Json.NET | `TypeNameHandling` 非 `None` 且缺少严格 `ISerializationBinder` |
| `JavaScriptSerializer` | 使用 `SimpleTypeResolver` 或自定义宽松 resolver 处理外部 JSON |
| `XmlSerializer` | 类型参数由外部输入控制，或配合危险类型/XAML/ODP |
| `DataContractSerializer` | `KnownTypes`/resolver 可被污染，或类型边界错误 |
| `NetDataContractSerializer` | 反序列化不可信 XML，完整类型信息可控 |
| .NET Remoting | `TypeFilterLevel.Full`、HTTP/TCP channel 暴露、formatter sink provider 不安全 |

## 输出要求

- 漏洞编号格式：`{C/H/M/L}-DESER-{序号}`。
- 必须说明 formatter、输入格式、类型控制点、调用链、是否有 Binder/MAC/签名/白名单。
- 对 ViewState 必须检查 `enableViewStateMac`、`ViewStateUserKey`、`machineKey` 来源和泄露路径。
- 对组件漏洞必须关联组件版本与实际触发入口，不只按版本下结论。
- 修复优先建议：移除危险 formatter、改用 DTO/安全 serializer、禁用类型名处理、启用严格 binder、签名和密钥轮换。

## 自检

- 已覆盖 11 类 .NET 反序列化入口。
- 每个 sink 都有输入可控性结论。
- 没有默认输出可直接攻击真实系统的命令执行 payload。
