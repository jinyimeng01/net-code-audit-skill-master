# .NET XML 解析器 XXE 审计详解

## 目录

- [1. XmlReader](#1-xmlreader)
- [2. XmlDocument](#2-xmldocument)
- [3. XDocument (LINQ to XML)](#3-xdocument-linq-to-xml)
- [4. XmlSerializer](#4-xmlserializer)
- [5. DataContractSerializer](#5-datacontractserializer)
- [6. 其他 XML 组件](#6-其他-xml-组件)
- [7. 通用审计要点](#7-通用审计要点)

---

## 1. XmlReader

### 识别特征

```csharp
using System.Xml;
```

### 危险模式

```csharp
// 高危：未设置任何安全特性
XmlReader reader = XmlReader.Create(request.InputStream);
while (reader.Read()) { /* ... */ }

// 高危：使用 XmlReaderSettings 但未禁用 DTD
XmlReaderSettings settings = new XmlReaderSettings();
XmlReader reader = XmlReader.Create(stream, settings);
```

### 安全模式

```csharp
// 安全：禁用 DTD（推荐）
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,  // .NET 4.0+
    XmlResolver = null
};
XmlReader reader = XmlReader.Create(stream, settings);

// 安全：禁用外部实体
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Ignore,
    XmlResolver = null  // 禁止解析外部实体
};
XmlReader reader = XmlReader.Create(stream, settings);
```

### 检测规则

| 检查项 | 安全 | 危险 |
|--------|------|------|
| `DtdProcessing = DtdProcessing.Prohibit` | 安全 | 未设置 |
| `DtdProcessing = DtdProcessing.Ignore` | 安全（需配合 XmlResolver=null） | 未设置 |
| `XmlResolver = null` | 安全 | 未设置或使用 XmlUrlResolver |

### .NET 版本差异

| .NET 版本 | DtdProcessing 默认值 | 默认安全 |
|-----------|---------------------|----------|
| .NET Framework 4.5.2+ | Prohibit | 是 |
| .NET Framework 4.0-4.5.1 | Parse（如果显式创建） | 否 |
| .NET Core / .NET 5+ | Prohibit | 是 |
| .NET Framework 3.5 及更早 | 无 DtdProcessing 属性 | 否 |

### 搜索正则

```bash
grep -rn "XmlReader.Create\|new XmlReader" --include="*.cs"
```

---

## 2. XmlDocument

### 识别特征

```csharp
using System.Xml;
```

### 危险模式

```csharp
// 高危：默认加载外部实体
XmlDocument doc = new XmlDocument();
doc.Load(request.InputStream);

// 高危：使用 XmlUrlResolver
XmlDocument doc = new XmlDocument();
doc.XmlResolver = new XmlUrlResolver();  // 显式启用外部实体解析
doc.LoadXml(xmlString);
```

### 安全模式

```csharp
// 安全：设置 XmlResolver 为 null
XmlDocument doc = new XmlDocument
{
    XmlResolver = null  // 禁止解析外部实体
};
doc.Load(stream);

// 安全：使用安全的 XmlReader 加载
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,
    XmlResolver = null
};
XmlDocument doc = new XmlDocument();
doc.Load(XmlReader.Create(stream, settings));
```

### .NET 版本差异

| .NET 版本 | XmlDocument 默认 XmlResolver | 默认安全 |
|-----------|------------------------------|----------|
| .NET Framework 4.5.2+ | null | 是 |
| .NET Framework 4.0-4.5.1 | XmlUrlResolver | 否 |
| .NET Core / .NET 5+ | null | 是 |
| .NET Framework 3.5 及更早 | XmlUrlResolver | 否 |

### 搜索正则

```bash
grep -rn "new XmlDocument\|XmlDocument.*Load\|\.LoadXml" --include="*.cs"
```

---

## 3. XDocument (LINQ to XML)

### 识别特征

```csharp
using System.Xml.Linq;
```

### 危险模式

```csharp
// 高危：直接从流加载
XDocument doc = XDocument.Load(request.InputStream);

// 高危：从字符串解析
XDocument doc = XDocument.Parse(xmlString);
```

### 安全模式

```csharp
// 安全：使用安全的 XmlReader 加载
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,
    XmlResolver = null
};
XDocument doc = XDocument.Load(XmlReader.Create(stream, settings));
```

### 注意事项

- `XDocument.Load(Stream)` 在 .NET Framework 4.5.2+ 默认安全
- 在 .NET Framework 4.0-4.5.1 中可能不安全
- 推荐始终使用 XmlReader 中间层

### 搜索正则

```bash
grep -rn "XDocument.Load\|XDocument.Parse\|XElement.Load\|XElement.Parse" --include="*.cs"
```

---

## 4. XmlSerializer

### 识别特征

```csharp
using System.Xml.Serialization;
```

### 危险模式

```csharp
// 高危：直接反序列化不受信任的 XML
XmlSerializer serializer = new XmlSerializer(typeof(User));
User user = (User)serializer.Deserialize(request.InputStream);
```

### 安全模式

```csharp
// 安全：先使用安全 XmlReader 解析，再反序列化
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,
    XmlResolver = null
};
XmlSerializer serializer = new XmlSerializer(typeof(User));
User user = (User)serializer.Deserialize(XmlReader.Create(stream, settings));
```

### 注意事项

- `XmlSerializer` 本身不解析 DTD/外部实体（它使用内部 Reader）
- 但如果直接传入 Stream，内部 Reader 的安全取决于 .NET 版本
- 推荐始终使用安全的 XmlReader 中间层
- `XmlSerializer` 存在反序列化漏洞风险（如 `ObjectDataProvider`、`XslCompiledTransform` gadget），需单独评估

### 搜索正则

```bash
grep -rn "new XmlSerializer\|XmlSerializer.*Deserialize" --include="*.cs"
```

---

## 5. DataContractSerializer

### 识别特征

```csharp
using System.Runtime.Serialization;
```

### 危险模式

```csharp
// 高危：直接反序列化不受信任的 XML
DataContractSerializer serializer = new DataContractSerializer(typeof(User));
User user = (User)serializer.ReadObject(request.InputStream);
```

### 安全模式

```csharp
// 安全：使用安全的 XmlReader
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,
    XmlResolver = null
};
DataContractSerializer serializer = new DataContractSerializer(typeof(User));
User user = (User)serializer.ReadObject(XmlReader.Create(stream, settings));
```

### 注意事项

- `DataContractSerializer` 不支持 DTD，XXE 风险较低
- 但存在类型混淆反序列化风险，需设置已知类型列表

### 搜索正则

```bash
grep -rn "DataContractSerializer\|\.ReadObject" --include="*.cs"
```

---

## 6. 其他 XML 组件

### XslCompiledTransform (XSLT)

```csharp
// 高危：XSLT 样式表可能加载外部资源
XslCompiledTransform xslt = new XslCompiledTransform();
xslt.Load("transform.xslt");  // 可能加载外部实体

// 安全：禁用脚本和文档函数
XsltSettings settings = new XsltSettings(false, false);  // 禁用脚本和文档函数
XmlResolver resolver = null;
xslt.Load(XmlReader.Create("transform.xslt", xmlSettings), settings, resolver);
```

### XPathDocument

```csharp
// 高危：从不受信任的源加载
XPathDocument doc = new XPathDocument(request.InputStream);

// 安全：使用安全的 XmlReader
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,
    XmlResolver = null
};
XPathDocument doc = new XPathDocument(XmlReader.Create(stream, settings));
```

### DataSet.ReadXml

```csharp
// 高危：DataSet.ReadXml 可能加载外部实体
DataSet ds = new DataSet();
ds.ReadXml(request.InputStream);

// 安全：先使用安全 XmlReader
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,
    XmlResolver = null
};
DataSet ds = new DataSet();
ds.ReadXml(XmlReader.Create(stream, settings));
```

### XmlSchema.Read

```csharp
// 高危：XML Schema 验证可能加载外部实体
XmlSchema schema = XmlSchema.Read(stream, null);

// 安全：设置 XmlResolver
XmlReaderSettings settings = new XmlReaderSettings
{
    DtdProcessing = DtdProcessing.Prohibit,
    XmlResolver = null
};
XmlSchema schema = XmlSchema.Read(XmlReader.Create(stream, settings), null);
```

---

## 7. 通用审计要点

### 安全配置有效性判断

| 配置 | 防护效果 | 备注 |
|------|----------|------|
| `DtdProcessing = Prohibit` | **完全防护** | 拒绝所有 DTD，最安全 |
| `DtdProcessing = Ignore` + `XmlResolver = null` | **完全防护** | 忽略 DTD 且不解析外部实体 |
| `XmlResolver = null` | **部分防护** | 禁止外部实体解析，但 DTD 可能仍被处理 |
| `DtdProcessing = Ignore`（无 XmlResolver=null） | **部分防护** | DTD 被忽略但外部实体可能仍被解析 |
| 仅使用 `XmlReader.Create(stream)` 无 settings | **取决于版本** | .NET 4.5.2+ 安全，更早版本不安全 |
| `ProhibitDtd = true` (.NET 2.0-3.5) | **完全防护** | 旧版本使用此属性 |

### 完整防护要求

**至少满足以下之一：**

1. 设置 `DtdProcessing = DtdProcessing.Prohibit`（推荐）
2. 同时设置 `DtdProcessing = DtdProcessing.Ignore` **且** `XmlResolver = null`

### 常见误判场景

| 场景 | 说明 | 判定 |
|------|------|------|
| 仅设置 `XmlResolver = null` | 阻止外部实体但不阻止 DTD 处理 | **.NET 4.5.2+ 安全** |
| 在 .NET 4.0 中使用默认 XmlReader.Create | 默认允许 DTD | **仍然危险** |
| 使用 XmlDocument.Load 无设置 | .NET 4.5.2+ 默认安全 | **需确认版本** |
| 仅用 `XmlReader.Create(stream)` 无 settings | .NET 4.5.2+ 默认安全 | **需确认版本** |

### 版本相关安全差异

| .NET 版本 | 默认行为 |
|-----------|----------|
| .NET Framework 4.5.2+ | XmlReader/XmlDocument 默认安全 |
| .NET Framework 4.0-4.5.1 | 需手动设置安全配置 |
| .NET Core 1.0+ | 默认安全 |
| .NET 5/6/7/8+ | 默认安全 |
| .NET Framework 3.5 及更早 | 默认不安全，需手动设置 ProhibitDtd=true |
