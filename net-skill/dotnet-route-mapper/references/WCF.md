# WCF 服务路由分析

## 目录

- [项目识别](#项目识别)
- [ServiceContract 识别](#servicecontract-识别)
- [配置文件](#配置文件)
- [绑定类型](#绑定类型)
- [SOAP 操作提取](#soap-操作提取)
- [常见模式](#常见模式)

---

## 项目识别

**特征文件：**
```
.svc - WCF 服务文件
web.config / app.config - WCF 端点配置
Service References/ - 服务引用目录
```

**特征类：**
```csharp
System.ServiceModel.ServiceContract
System.ServiceModel.OperationContract
System.ServiceModel.BasicHttpBinding
System.ServiceModel.WSHttpBinding
```

---

## ServiceContract 识别

### 接口定义

```csharp
[ServiceContract(Namespace = "http://example.com/services")]
public interface IUserService
{
    [OperationContract]
    User GetUser(int id);

    [OperationContract]
    List<User> SearchUsers(string keyword);

    [OperationContract]
    bool CreateUser(UserDto user);
}
```

**提取规则：**
- `[ServiceContract]` 标记服务接口
- `[OperationContract]` 标记可调用的操作方法
- `Namespace` 属性定义 XML 命名空间

### 服务实现

```csharp
public class UserService : IUserService
{
    public User GetUser(int id) { ... }
    public List<User> SearchUsers(string keyword) { ... }
    public bool CreateUser(UserDto user) { ... }
}
```

### DataContract

```csharp
[DataContract(Namespace = "http://example.com/types")]
public class User
{
    [DataMember]
    public int Id { get; set; }

    [DataMember]
    public string Username { get; set; }

    [DataMember(IsRequired = true)]
    public string Email { get; set; }
}
```

---

## 配置文件

### .svc 文件

```
<%@ ServiceHost Language="C#"
    Service="MyApp.Services.UserService"
    CodeBehind="UserService.svc.cs" %>
```

**提取规则：**
- `Service` 属性 → 服务类全限定名
- URL 路径为 `/UserService.svc`

### web.config 端点配置

```xml
<configuration>
  <system.serviceModel>
    <services>
      <service name="MyApp.Services.UserService"
               behaviorConfiguration="serviceBehavior">
        <!-- basicHttpBinding 端点 -->
        <endpoint
            address=""
            binding="basicHttpBinding"
            contract="MyApp.Services.IUserService" />

        <!-- wsHttpBinding 端点 -->
        <endpoint
            address="secure"
            binding="wsHttpBinding"
            contract="MyApp.Services.IUserService" />

        <!-- 元数据交换端点 -->
        <endpoint
            address="mex"
            binding="mexHttpBinding"
            contract="IMetadataExchange" />
      </service>
    </services>

    <behaviors>
      <serviceBehaviors>
        <behavior name="serviceBehavior">
          <serviceMetadata httpGetEnabled="true" />
          <serviceDebug includeExceptionDetailInFaults="true" />
        </behavior>
      </serviceBehaviors>
    </behaviors>

    <!-- 服务托管配置 -->
    <serviceHostingEnvironment>
      <serviceActivations>
        <add relativeAddress="UserService.svc"
             service="MyApp.Services.UserService" />
      </serviceActivations>
    </serviceHostingEnvironment>
  </system.serviceModel>
</configuration>
```

### URL 路径计算

```
完整 WCF URL = 上下文路径 + .svc 文件路径 + endpoint address
```

| 配置项 | 值 | 说明 |
|:-------|:---|:-----|
| 上下文路径 | `/myapp` | IIS 站点路径 |
| .svc 文件路径 | `/Services/UserService.svc` | 文件路径 |
| endpoint address | `""` (空) | 默认端点 |

**完整路径：** `/myapp/Services/UserService.svc`

如果 endpoint address = `"secure"`：
**完整路径：** `/myapp/Services/UserService.svc/secure`

---

## 绑定类型

| 绑定类型 | 协议 | 安全性 | 典型端口 | 说明 |
|----------|------|--------|----------|------|
| `basicHttpBinding` | SOAP 1.1 / HTTP | 低 | 80 | 兼容旧版 ASMX |
| `wsHttpBinding` | SOAP 1.2 / HTTP | 中 | 80 | WS-* 标准支持 |
| `wsDualHttpBinding` | SOAP / HTTP 双工 | 中 | 80 | 双工通信 |
| `netTcpBinding` | SOAP / TCP | 高 | 808 | WCF 专用协议 |
| `netNamedPipeBinding` | SOAP / Named Pipe | 高 | - | 本机通信 |
| `netMsmqBinding` | SOAP / MSMQ | 中 | - | 消息队列 |
| `webHttpBinding` | REST / HTTP | 低 | 80 | REST 风格 |

### basicHttpBinding 安全配置

```xml
<bindings>
  <basicHttpBinding>
    <binding name="secureBinding">
      <security mode="Transport">
        <transport clientCredentialType="Windows" />
      </security>
    </binding>
    <binding name="insecureBinding">
      <security mode="None" />
    </binding>
  </basicHttpBinding>
</bindings>
```

### webHttpBinding (REST)

```xml
<endpoint
    address="rest"
    binding="webHttpBinding"
    contract="MyApp.Services.IUserService"
    behaviorConfiguration="restBehavior" />

<endpointBehaviors>
  <behavior name="restBehavior">
    <webHttp />
  </behavior>
</endpointBehaviors>
```

```csharp
[ServiceContract]
public interface IUserService
{
    [OperationContract]
    [WebGet(UriTemplate = "/users/{id}", ResponseFormat = WebMessageFormat.Json)]
    User GetUser(string id);

    [OperationContract]
    [WebInvoke(UriTemplate = "/users", Method = "POST",
               RequestFormat = WebMessageFormat.Json)]
    bool CreateUser(UserDto user);
}
```

---

## SOAP 操作提取

### SOAP 请求格式

```xml
POST /UserService.svc HTTP/1.1
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://example.com/services/IUserService/GetUser"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetUser xmlns="http://example.com/services">
      <id>123</id>
    </GetUser>
  </soap:Body>
</soap:Envelope>
```

### SOAPAction 计算

```
SOAPAction = ServiceContract Namespace + 接口名 + 方法名
```

示例：
```
Namespace: http://example.com/services
Interface: IUserService
Method: GetUser
→ SOAPAction: "http://example.com/services/IUserService/GetUser"
```

### WSDL 获取

```
GET /UserService.svc?wsdl        → WSDL 文档
GET /UserService.svc?singleWsdl  → 单文件 WSDL
```

**WSDL 中提取信息：**
- 服务端点地址
- 操作名称和参数
- 消息格式（Document/RPC）
- 绑定类型

---

## 常见模式

### 默认端点配置（无 .svc 文件）

```csharp
// Global.asax.cs
public class Global : HttpApplication
{
    void Application_Start(object sender, EventArgs e)
    {
        RouteTable.Routes.Add(new ServiceRoute("api/users",
            new WebServiceHostFactory(), typeof(UserService)));
    }
}
// URL: /api/users (无 .svc 后缀)
```

### Windsor/Castle WCF 集成

```xml
<serviceActivations>
  <add relativeAddress="UserService.svc"
       service="MyApp.Services.IUserService, MyApp.Services" />
</serviceActivations>
```

### WCF REST 服务

```csharp
[ServiceContract]
public interface IOrderService
{
    [WebGet(UriTemplate = "/orders?status={status}")]
    List<Order> GetOrders(string status);

    [WebInvoke(UriTemplate = "/orders", Method = "POST")]
    Order CreateOrder(OrderDto dto);

    [WebInvoke(UriTemplate = "/orders/{id}", Method = "PUT")]
    Order UpdateOrder(string id, OrderDto dto);

    [WebInvoke(UriTemplate = "/orders/{id}", Method = "DELETE")]
    void DeleteOrder(string id);
}
```

### Burp Suite 请求模板

```http
POST /UserService.svc HTTP/1.1
Host: 【填写：目标主机】
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://example.com/services/IUserService/GetUser"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetUser xmlns="http://example.com/services">
      <id>【填写：用户ID】</id>
    </GetUser>
  </soap:Body>
</soap:Envelope>
```
