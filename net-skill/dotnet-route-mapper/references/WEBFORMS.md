# ASP.NET WebForms 路由分析

## 目录

- [项目识别](#项目识别)
- [文件类型识别](#文件类型识别)
- [路由模式](#路由模式)
- [参数提取](#参数提取)
- [web.config URL 映射](#webconfig-url-映射)
- [常见模式](#常见模式)

---

## 项目识别

**特征文件：**
```
.aspx - WebForms 页面
.asmx - Web 服务
.ashx - 通用处理程序
.ascx - 用户控件
web.config - 配置文件
Global.asax - 全局应用配置
App_Code/ - 代码目录
```

**特征类：**
```csharp
System.Web.UI.Page
System.Web.UI.UserControl
System.Web.IHttpHandler
System.Web.Services.WebService
```

---

## 文件类型识别

### .aspx 页面

```aspx
<%@ Page Language="C#" AutoEventWireup="true"
    CodeBehind="UserList.aspx.cs"
    Inherits="MyApp.Web.UserList" %>
```

**提取规则：**
- `Inherits` 属性 → 类全限定名
- `CodeBehind` 属性 → 源文件路径
- 文件路径即为 URL 路径（如 `/UserList.aspx`）

### .asmx Web 服务

```asmx
<%@ WebService Language="C#"
    CodeBehind="UserService.asmx.cs"
    Class="MyApp.Web.UserService" %>
```

**提取规则：**
- `Class` 属性 → 类全限定名
- URL 路径为 `/UserService.asmx`

### .ashx 通用处理程序

```csharp
public class ImageHandler : IHttpHandler
{
    public void ProcessRequest(HttpContext context)
    {
        string id = context.Request.QueryString["id"];
        // 处理逻辑
    }

    public bool IsReusable { get { return false; } }
}
```

**提取规则：**
- 实现 `IHttpHandler` 接口的类
- 在 web.config 中注册 URL 路径

---

## 路由模式

### Page_Load 事件

```csharp
public partial class UserList : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        if (!IsPostBack)
        {
            string id = Request.QueryString["id"];
            // 首次加载
        }
    }
}
```

**提取要点：**
- `Page_Load` 是默认入口方法
- `IsPostBack` 区分 GET 和 POST

### 按钮点击事件

```csharp
public partial class UserEdit : System.Web.UI.Page
{
    protected void btnSave_Click(object sender, EventArgs e)
    {
        string username = txtUsername.Text;
        // 保存逻辑
    }

    protected void btnDelete_Click(object sender, EventArgs e)
    {
        string id = Request.Form["id"];
        // 删除逻辑
    }
}
```

**提取要点：**
- 按钮事件名格式: `控件ID_Click`
- 对应 POST 请求
- 参数来自表单控件

### ASP.NET 回调模式

```csharp
public partial class UserList : System.Web.UI.Page, ICallbackEventHandler
{
    public string GetCallbackResult()
    {
        // 返回回调结果
    }

    public void RaiseCallbackEvent(string eventArgument)
    {
        // 处理回调参数
    }
}
```

---

## 参数提取

### 查询参数

```csharp
string id = Request.QueryString["id"];
string name = Request.QueryString["name"];
```

### 表单参数

```csharp
string username = Request.Form["username"];
string password = Request.Form["password"];
```

### 请求参数（Query + Form）

```csharp
string param = Request["param"];
```

### 控件值

```csharp
string username = txtUsername.Text;
int age = int.Parse(txtAge.Text);
```

### Cookie 参数

```csharp
string sessionId = Request.Cookies["ASP.NET_SessionId"]?.Value;
```

### Header 参数

```csharp
string authHeader = Request.Headers["Authorization"];
```

### ViewState

```csharp
// WebForms 使用 ViewState 维持状态
// ViewState 是 Base64 编码的隐藏字段
string viewState = Request.Form["__VIEWSTATE"];
string eventValidation = Request.Form["__EVENTVALIDATION"];
```

---

## web.config URL 映射

### URL 映射

```xml
<configuration>
  <system.web>
    <urlMappings enabled="true">
      <add url="~/home" mappedUrl="~/Default.aspx"/>
      <add url="~/about" mappedUrl="~/About.aspx"/>
    </urlMappings>
  </system.web>
</configuration>
```

### URL 重写

```xml
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="User Profile" stopProcessing="true">
          <match url="^user/([0-9]+)$" />
          <action type="Rewrite" url="UserProfile.aspx?id={R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### 自定义 HttpHandler 注册

```xml
<configuration>
  <system.web>
    <httpHandlers>
      <add verb="*" path="*.image" type="MyApp.Web.ImageHandler, MyApp"/>
      <add verb="GET" path="/api/data" type="MyApp.Web.DataHandler, MyApp"/>
    </httpHandlers>
  </system.web>

  <system.webServer>
    <handlers>
      <add name="ImageHandler" verb="*" path="*.image"
           type="MyApp.Web.ImageHandler, MyApp"/>
    </handlers>
  </system.webServer>
</configuration>
```

### 路由配置（FriendlyUrl）

```csharp
// Global.asax.cs
void Application_Start(object sender, EventArgs e)
{
    RouteConfig.RegisterRoutes(RouteTable.Routes);
}

// App_Start/RouteConfig.cs
public static class RouteConfig
{
    public static void RegisterRoutes(RouteCollection routes)
    {
        routes.MapPageRoute("UserList", "users", "~/UserList.aspx");
        routes.MapPageRoute("UserDetail", "user/{id}", "~/UserDetail.aspx");
    }
}
```

---

## 常见模式

### MasterPage + ContentPage

```csharp
// UserList.aspx 使用 MasterPage
// ContentPlaceHolder 内的控件可通过 FindControl 获取
ContentPlaceHolder cph = (ContentPlaceHolder)Master.FindControl("MainContent");
TextBox txt = (TextBox)cph.FindControl("txtUsername");
```

### 用户控件 (.ascx)

```aspx
<%@ Register Src="~/Controls/UserInfo.ascx" TagPrefix="uc" TagName="UserInfo" %>
<uc:UserInfo ID="UserInfo1" runat="server" UserId='<%# Eval("Id") %>' />
```

### ASP.NET AJAX

```csharp
[System.Web.Services.WebMethod]
public static string GetUserData(string id)
{
    // 可通过 AJAX POST 调用
    // URL: /UserList.aspx/GetUserData
    // Content-Type: application/json
}
```

**请求模板：**
```http
POST /UserList.aspx/GetUserData HTTP/1.1
Content-Type: application/json

{"id":"123"}
```
