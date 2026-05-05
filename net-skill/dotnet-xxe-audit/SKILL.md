---
name: dotnet-xxe-audit
version: 2.0.0
description: .NET XXE 与 XML 解析审计 skill。覆盖 XmlDocument、XmlReader、XDocument、XmlSerializer、XslCompiledTransform、SOAP 解析、OOXML/SVG 导入。追踪用户可控输入到 XML 解析 sink，输出 XXE 证据和修复建议。
description_en: .NET XXE & XML parser audit skill. Covers XmlDocument, XmlReader, XDocument, XmlSerializer, XslCompiledTransform, SOAP parsing, OOXML/SVG import. Traces user input to XML parsing sinks.
author: net-code-audit-team
tags: ['dotnet', 'xxe', 'xml', 'xslt', 'soap', 'ooxml']
compatibility: ['asp.net', 'asp.net-core', 'wcf', 'iis']
---

# .NET XXE 漏洞审计工具

检查 .NET Web 项目源码或反编译结果，识别 XML 解析实现，检测 XXE (XML External Entity) 注入漏洞。

## 核心要求

**此技能必须完整检查所有 XML 解析相关代码，不允许省略。**

- 必须识别所有 XML 解析入口点（5 种解析器）
- 必须检查每个解析器的外部实体防护配置
- 必须追踪 XML 输入来源（用户可控性）
- 必须检测回显点（数据是否返回给用户）
- 禁止省略任何 XML 解析操作
- 禁止跳过反编译步骤

---

## 漏洞分级标准

**详见 [SEVERITY_RATING.md](../shared/SEVERITY_RATING.md)**

- 漏洞编号格式: `{C/H/M/L}-XXE-{序号}`

---

## 反编译支持（CRITICAL）

**当源码不可用时，必须使用 dnSpy.Console.exe 反编译。**

```bash
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r bin/
```

详见 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md)

---

## XML 解析器识别与检测规则

### 1. XmlReader（推荐安全解析器）

| 模式 | 安全/危险 | 代码 |
|------|----------|------|
| 默认配置 | **安全** | `XmlReader.Create(stream)` — .NET 4.5.2+ 默认禁用 DTD |
| 显式启用 DTD | **危险** | `XmlReaderSettings { DtdProcessing = DtdProcessing.Parse }` |
| 启用外部实体 | **危险** | `XmlResolver = new XmlUrlResolver()` |

### 2. XmlDocument

| 模式 | 安全/危险 | 代码 |
|------|----------|------|
| 默认配置 | **危险**（.NET Framework） | `new XmlDocument()` — 默认允许 DTD |
| 禁用实体 | **安全** | `XmlDocument { XmlResolver = null }` |

### 3. XDocument / LINQ to XML

| 模式 | 安全/危险 | 代码 |
|------|----------|------|
| 默认配置 | **安全**（.NET 4.5.2+） | `XDocument.Load(stream)` |
| 自定义 XmlReader | 取决于配置 | `XDocument.Load(XmlReader.Create(...))` |

### 4. XmlSerializer

| 模式 | 安全/危险 | 代码 |
|------|----------|------|
| 默认配置 | **安全** | `new XmlSerializer(typeof(T))` — 不处理 DTD |
| 自定义 Reader | 取决于配置 | 配合不安全的 XmlReader 使用 |

### 5. DataContractSerializer

| 模式 | 安全/危险 | 代码 |
|------|----------|------|
| 默认配置 | **安全** | 不支持 DTD/外部实体 |

---

## 检测规则速查

### 危险模式

```csharp
// XmlDocument 默认危险
XmlDocument doc = new XmlDocument();
doc.LoadXml(userInput);  // XXE

// XmlReader 启用 DTD
XmlReaderSettings settings = new XmlReaderSettings();
settings.DtdProcessing = DtdProcessing.Parse;  // 危险
settings.XmlResolver = new XmlUrlResolver();     // 危险
XmlReader reader = XmlReader.Create(stream, settings);
```

### 安全模式

```csharp
// XmlDocument 安全配置
XmlDocument doc = new XmlDocument();
doc.XmlResolver = null;  // 安全

// XmlReader 安全配置
XmlReaderSettings settings = new XmlReaderSettings();
settings.DtdProcessing = DtdProcessing.Prohibit;  // 安全
settings.XmlResolver = null;                        // 安全
```

---

## 技能协作流程

**dotnet-xxe-audit 应在 dotnet-route-mapper 之后执行。**

需要深度追踪时调用 dotnet-route-tracer。

---

## 输出格式

**严格按照 [references/OUTPUT_TEMPLATE.md](references/OUTPUT_TEMPLATE.md) 中的填充式模板生成输出文件。**

- 文件名格式: `{project_name}_xxe_audit_{YYYYMMDD_HHMMSS}.md`
- 通用规范参考: [shared/DOTNET_OUTPUT_STANDARD.md](../shared/DOTNET_OUTPUT_STANDARD.md)

---

## 验证检查清单

- [ ] 所有 XML 解析入口点已识别
- [ ] 每个解析器的外部实体防护已检查
- [ ] XML 输入来源已追踪
- [ ] 回显点已分析
- [ ] 反编译来源已标注（如适用）
- [ ] 报告已生成并通过自检清单
