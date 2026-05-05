<!--
Source: G:\tmp\安全项目研究\.netskill\.NET高级代码审计（第九课） BinaryFormatter反序列化漏洞.pdf-eacae671-393f-431c-952c-aaf3682621f6\full.md
Archived as: BinaryFormatter raw lesson material
Purpose: provenance-only reference for authorized .NET code audit skill development.
Do not load by default; prefer structured references unless exact source context is needed.
-->
.NET 高级代码审计（第九课） BinaryFormatter 反序列化漏洞

Ivan1ee@360 天眼云影实验室

2019 年 03 月 01 日

# 0x00 前言

BinaryFormatter 和 SoapFormatter 两个类之间的区别在于数据流的格式不同，其他的功能上两者差不多，BinaryFormatter 位于命名空间

System.Runtime.Serialization.Formatters.Binary 它是直接用二进制方式把对象进行序列化，优点是速度较快，在不同版本的.NET 平台里都可以兼容。但是使用反序列化不受信任的二进制文件会导致反序列化漏洞从而实现远程 RCE 攻击，本文笔者从原理和代码审计的视角做了相关介绍和复现。

# 0x01 BinaryFormatter 序列化

使用 BinaryFormatter 类序列化的过程中，用[Serializable]声明这个类是可以被序列化的，当然有些不想被序列化的元素可以用[NoSerialized]属性来规避。下面通过一个实例来说明问题，首先定义 TestClass 对象

[Serializable]   
public class TestClass{ private string classname; private string name; private int age; public string classname { get $\Rightarrow$ classname; set $\Rightarrow$ classname $=$ value;} public string Name { get $\Rightarrow$ name; set $\Rightarrow$ name $=$ value;} public int Age { get $\Rightarrow$ age; set $\Rightarrow$ age $=$ value;} public override stringToString() { return base.ToString(); } public static void ClassMethod( string value) { Process.Start(value); }

定义了三个成员，并实现了一个静态方法 ClassMethod 启动进程。 序列化通过创建对

象实例分别给成员赋值

```matlab
TestClass testClass = new TestClass();
testClass.Age = 18;
testClass.Name = "Ivan1ee";
testClass.Classname = "360";
FileStream stream = new FileStream(@"d:\Binary1.dat", FileMode.Create);
BinaryFormatter bFormat = new BinaryFormatter();
bFormat SZeralyze(stream, testClass);
stream.Close(); 
```

常规下使用 Serialize 得到序列化后的二进制文件内容打开后显示的数据格式如下

启动 Binary.dat Binary1.dat 编辑为：十六进制00 运行脚本 运行模板 0123456789ABCDEF 0000h: 00 01 00 00 00 FF FF FF FF 01 00 00 00 00 00 00 00 00 .yyyy. . . .>WpfApp1, 0010h: 00 0C 02 00 00 00 3E 57 70 66 41 70 70 31 2C 20 .Version=1.0.0.0, 0020h: 56 65 72 73 69 6F 6E 3D 31 2E 30 2E 30 2E 30 2C Culture $\equiv$ neutral 0030h: 20 43 75 6C 74 75 72 65 3D 6E 65 75 74 72 61 6C .PublicKeyToken =null.....WpfAp 0040h: 2C 20 50 75 62 6C 69 63 4B 65 79 54 6F 6B 65 6E ,PublicKeyToken =null.....WpfAp   
0050h: 3D 6E 75 6C 6C 05 01 00 00 00 11 57 70 66 41 70 p1.TestClass... .classname.name.. age....   
0060h: 70 31 2E 54 65 73 74 43 6C 61 73 73 O3 OO OO .classname.name..   
0070h: O9636C6173736E616D65O46E616D65O3   
0080h: O16765O1O1Oo8O2OooOooO6O3OooO Oage....   
O99oh: O3333630O6O4OooOooOoo74976616E3165 I.360.....Ivanle   
OOAoh: O512OooOooOB

# 0x02 BinaryFormatter 反序列化

# 2.1、反序列化用法

反序列过程是将二进制数据转换为对象，通过创建一个新对象的方式调用 Deserialize多个重载方法实现的，查看定义可以看出和 SoapFormatter 格式化器一样实现了

IRemotingFormatter、IFormatter 接口

```cs
namespace System.Runtime serialization.Formatters.Binary   
{ public sealed class BinaryFormatter : IRemotingFormatter, IFormatter   
public BinaryFormatter(); public BinaryFormatter(ISurrogateSelector selector, StreamingContext context); public FormatterLineStyle TypeFormat { get; set;} public FormatterAssemblyStyle AssemblyFormat { get; set;} public TypeFilterLevel FilterLevel { get; set;} public ISurrogateSelector SurrogateSelector { get; set;} public SZializationBinder Binder { get; set;} public StreamingContext Context { get; set;}   
public object DeserializationStream serializationStream); public object DeserializationStream,HeaderHandler handler); public object DeserializationMethodResponse(Stream serializationStream,HeaderHandler handler,IMethodCallMessage methodCallMessage); public void Deserialization(Strem serializationStream,object graph); public void Deserialization(Strem serializationStream,object graph,Header[] headers); public object UnsafeDeserialization(Strem serializationStream,HeaderHandler handler); public object UnsafeDeserializationMethodResponse(Strem serializationStream,HeaderHandler handler,IMethodCallMessage methodCallMess 
```

我们得到系统提供的四个不同的反序列方法，分别是 Deserialize、

DeserializeMethodResponse、UnsafeDeserialize、

UnsafeDeserializeMethodResponse。笔者通过创建新对象的方式调用 Deserialize

方法实现的具体实现代码可参考以下

```txt
FileStream stream2 = new FileInputStream(@"d:\Binary1.dat", FileMode.Open);  
BinaryFormatter bFormat2 = new BinaryFormatter();  
var person = bFormat2.Deserialization(stream2);  
Console.WriteLine((TestClass.person).Name);  
stream2.Close(); 
```

反序列化后得到 TestClass 类的成员 Name 的值。

![](images/6476167c6883275c49159091f4a2d9bf632cab4877ac568cbf2d76b18c648971.jpg)

D:\Tmp\Csharp\WPF\WpfApp1\WpfApp1\bin\Debug\WpfApp1.exe

Ivanlee

# 2.2、攻击向量—ActivitySurrogateSelector

由于上一篇中已经介绍了漏洞的原理，所以本篇就不再冗余的叙述，没有看的朋友请参考《.NET 高级代码审计（第八课） SoapFormatter 反序列化漏洞》，两者之间唯一的区 别 是 用 了 BinaryFormatter 类 序 列 化 数 据 ， 同 样 也 是 通 过 重 写

ISerializationSurrogate 调用自定义代码，笔者这里依旧用计算器做演示，生成的二进

制文件打开后如下图

![](images/4ce5ca4f69f0daced6dec078bacd4c5a7890b10697cbd3b93683dc43476b47ee.jpg)

按照惯例用 BinaryFormatter 类的 Deserialize 方法反序列化

```txt
FileStream stream2 = new FileInputStream(@"d:\Binary.dat", FileMode.Open);  
BinaryFormatter bFormat2 = new BinaryFormatter();  
var person = bFormat2.Deserialization(stream2);  
Console.WriteLine((TestClass.person).Name);  
stream2.Close(); 
```

计算器弹出，但同时也抛出了异常，这在WEB服务情况下会返回500错误。

![](images/afb6c41ef815220b88be0f2946bfc1d09ea5acb31205e34ded49637120cb4a3f.jpg)

# 2.3、攻击向量—WindowsIdentity

有关 WindowsIdentity 原理没有看的朋友请参考《.NET 高级代码审计（第二课）Json.Net 反序列化漏洞》，因为 WindowsIdentity 最终是解析 Base64 编码后的数据，所以这里将 Serializer 后的二进制文件反序列化后弹出计算器

![](images/6c01782f7bdc5f0e409a27dde53ba4eedbac2211fc80d4dbe1cbf046e8a4c730.jpg)

![](images/0cdb3a1cf58ffc269eeecb4795350734e747b88186968e8292bd14e08a0d511c.jpg)

# 0x03 代码审计视角

# 3.1、UnsafeDeserialize

从代码审计的角度找到漏洞的 EntryPoint，相比 Deserialize，UnsafeDeserialize 提供了更好的性能，这个方法需要传入两个必选参数，第二个参数可以为 null，这种方式不算很常见的，需要了解一下，下面是不安全的代码：

public static object UnsafeDeserialization(string path)   
{ FileStream fs $=$ File.Open(path,FileMode.Open); BinaryFormatter binaryFormatter $\equiv$ new BinaryFormatter(); var objects $=$ binaryFormatter.UnsafeDeserialization(fs,null); fs.close(); return objects;

攻击者只需要控制传入字符串参数path便可轻松实现反序列化漏洞攻击。

# 3.2、UnsafeDeserializeMethodResponse

相比 DeserializeMethodResponse，UnsafeDeserializeMethodResponse 性能上更加出色，这个方法需要传入三个必选参数，第二和第三个参数都可为 null，这种方式也不算很常见，只需要了解一下，下面是不安全的代码：

public static object UnsafeDeserializationMethodResponseData(string path)   
{ FileStream fs $=$ File.Open(path,FileMode.Open); BinaryFormatter binaryFormatter $\equiv$ new BinaryFormatter(); var objects $=$ binaryFormatter.UnsafeDeserializationMethodResponse(fs,null,null); fs.Close(); return objects;

# 3.3、Deserialize

Deserialize 方法很常见，开发者通常用这个方法反序列化，此方法有两个重载，下面是不安全的代码

public static object DeserializationData(string path)   
{ FileStream fs $=$ File.Open(path,FileMode.Open); BinaryFormatter binaryFormatter $\equiv$ new BinaryFormatter(); var objects $=$ binaryFormatter.Deserialization(fs); fs.Close(); return objects;

# 3.4、DeserializeMethodResponse

相比 Deserialize，DeserializeMethodResponse 可对远程方法响应提供的 Stream 流进行反序列化，这个方法需要传入三个必选参数，第二和第三个参数都可为 null，这种方式也不算很常见，只需要了解一下，下面是不安全的代码：

public static object DeserializationMethodResponseData(string path)   
{ FileStream fs $=$ File.Open(path,FileMode.Open); BinaryFormatter binaryFormatter $\equiv$ new BinaryFormatter(); var objects $=$ binaryFormatter.DeserializationMethodResponse(fs,null,null); fs.Close(); return objects;

最后用这个方法弹出计算器，附上动图

![](images/c519448a445848b62d6a26d8c0308296a89ad9fd2eabbfa51facb2aa330f5b39.jpg)

# 0x04 总结

实际开发中 BinaryFormatter 类从.NET Framework 2.0 开始，官方推荐使用

BinaryFormatter 来替代 SoapFormatter，特点是 BinaryFormatter 能更好的支持泛

型等数据，而在反序列化二进制文件时要注意数据本身的安全性，否则就会产生反序列

化漏洞。最后.NET 反序列化系列课程笔者会同步到 https://github.com/Ivan1ee/ 、

https://ivan1ee.gitbook.io/ ，后续笔者将陆续推出高质量的.NET 反序列化漏洞文

章，欢迎大伙持续关注，交流，更多的.NET安全和技巧可关注实验室公众号。
