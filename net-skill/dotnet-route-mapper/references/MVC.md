# ASP.NET MVC 路由分析

## 目录

- [项目识别](#项目识别)
- [配置文件](#配置文件)
- [路由注解/属性](#路由注解属性)
- [参数绑定](#参数绑定)
- [Area 路由](#area-路由)
- [常见模式](#常见模式)

---

## 项目识别

**特征文件：**
```
packages.config / *.csproj - 检查 Microsoft.AspNet.Mvc 依赖
Web.config - 传统 MVC 配置
App_Start/RouteConfig.cs - 路由配置
Global.asax.cs - 应用启动配置
Views/ - Razor 视图目录
Controllers/ - 控制器目录
```

**特征类：**
```csharp
System.Web.Mvc.Controller
System.Web.Mvc.ApiController  // 注意: Web API 2 使用
System.Web.Mvc.ActionResult
```

---

## 配置文件

### RouteConfig.cs

```csharp
public class RouteConfig
{
    public static void RegisterRoutes(RouteCollection routes)
    {
        routes.IgnoreRoute("{resource}.axd/{*pathInfo}");

        routes.MapRoute(
            name: "Default",
            url: "{controller}/{action}/{id}",
            defaults: new { controller = "Home", action = "Index", id = UrlParameter.Optional }
        );

        routes.MapRoute(
            name: "Admin",
            url: "admin/{controller}/{action}/{id}",
            defaults: new { controller = "Dashboard", action = "Index", id = UrlParameter.Optional }
        );
    }
}
```

**提取规则：**
- `url` 模板定义路径格式
- `defaults` 定义默认值
- `constraints` 定义约束（如有）

### Global.asax.cs

```csharp
public class MvcApplication : System.Web.HttpApplication
{
    protected void Application_Start()
    {
        AreaRegistration.RegisterAllAreas();
        RouteConfig.RegisterRoutes(RouteTable.Routes);
        FilterConfig.RegisterGlobalFilters(GlobalFilters.Filters);
        BundleConfig.RegisterBundles(BundleTable.Bundles);
    }
}
```

---

## 路由注解/属性

### Controller 识别

```csharp
// 命名约定: XxxController → 路由前缀 /Xxx
public class UserController : Controller
{
    // Action: Index → GET /User/Index 或 GET /User/
    public ActionResult Index() { ... }

    // Action: Details → GET /User/Details/123
    public ActionResult Details(int id) { ... }
}
```

### [Route] 属性路由

```csharp
[RoutePrefix("api/users")]
public class UserController : Controller
{
    [Route("")]
    public ActionResult List() { ... }           // GET /api/users

    [Route("{id:int}")]
    public ActionResult Details(int id) { ... }  // GET /api/users/123

    [Route("{id}/orders")]
    public ActionResult Orders(int id) { ... }   // GET /api/users/123/orders
}
```

### HTTP 方法属性

| 属性 | HTTP 方法 | 示例 |
|------|-----------|------|
| `[HttpGet]` | GET | `[HttpGet] public ActionResult List()` |
| `[HttpPost]` | POST | `[HttpPost] public ActionResult Create()` |
| `[HttpPut]` | PUT | `[HttpPut] public ActionResult Update(int id)` |
| `[HttpDelete]` | DELETE | `[HttpDelete] public ActionResult Delete(int id)` |
| `[AcceptVerbs]` | 自定义 | `[AcceptVerbs("GET","POST")]` |

### 路由约束

```csharp
[Route("users/{id:int}")]
public ActionResult Details(int id) { ... }

[Route("users/{name:alpha}")]
public ActionResult ByName(string name) { ... }

[Route("files/{*path}")]  // 通配符
public ActionResult File(string path) { ... }
```

| 约束 | 说明 | 示例 |
|------|------|------|
| `:int` | 整数 | `{id:int}` |
| `:alpha` | 字母 | `{name:alpha}` |
| `:bool` | 布尔 | `{active:bool}` |
| `:datetime` | 日期 | `{date:datetime}` |
| `:decimal` | 小数 | `{price:decimal}` |
| `:guid` | GUID | `{id:guid}` |
| `:length(n)` | 长度 | `{name:length(5)}` |
| `:regex(pattern)` | 正则 | `{code:regex(^[A-Z]{3}$)}` |

---

## 参数绑定

### FromQuery

```csharp
public ActionResult Search(string keyword, int page = 1, int size = 10)
{
    // GET /User/Search?keyword=test&page=1&size=10
}
```

### FromForm

```csharp
[HttpPost]
public ActionResult Create(string username, string email)
{
    // POST 表单参数
}
```

### FromBody (JSON)

```csharp
[HttpPost]
public ActionResult Create([FromBody]UserDto user)
{
    // POST JSON Body
}
```

### FromUri / FromRoute

```csharp
[Route("users/{id}")]
public ActionResult Details(int id)
{
    // 路由参数自动绑定
}
```

### 复杂对象绑定

```csharp
public ActionResult Search(SearchQuery query)
{
    // GET /User/Search?Keyword=test&Page=1&SortBy=name
    // 属性名自动映射
}

public class SearchQuery
{
    public string Keyword { get; set; }
    public int Page { get; set; } = 1;
    public string SortBy { get; set; }
}
```

---

## Area 路由

### Area 注册

```csharp
// Areas/Admin/AdminAreaRegistration.cs
public class AdminAreaRegistration : AreaRegistration
{
    public override string AreaName { get { return "Admin"; } }

    public override void RegisterArea(AreaRegistrationContext context)
    {
        context.MapRoute(
            "Admin_default",
            "Admin/{controller}/{action}/{id}",
            new { controller = "Dashboard", action = "Index", id = UrlParameter.Optional }
        );
    }
}
```

**Area URL 格式：** `/Admin/User/List`

### Area 中的控制器

```csharp
// Areas/Admin/Controllers/UserController.cs
namespace MyApp.Web.Areas.Admin.Controllers
{
    public class UserController : Controller
    {
        public ActionResult List() { ... }
        // URL: /Admin/User/List
    }
}
```

---

## 常见模式

### RESTful CRUD

```csharp
[RoutePrefix("api/users")]
public class UserController : Controller
{
    [Route("")]
    [HttpGet]
    public ActionResult List() { ... }

    [Route("{id:int}")]
    [HttpGet]
    public ActionResult Details(int id) { ... }

    [Route("")]
    [HttpPost]
    public ActionResult Create(UserDto dto) { ... }

    [Route("{id:int}")]
    [HttpPut]
    public ActionResult Update(int id, UserDto dto) { ... }

    [Route("{id:int}")]
    [HttpDelete]
    public ActionResult Delete(int id) { ... }
}
```

### 分页查询

```csharp
[HttpGet]
public ActionResult List(int page = 1, int pageSize = 10, string sortBy = "Id")
{
    // GET /User/List?page=2&pageSize=20&sortBy=Name
}
```

### 文件上传

```csharp
[HttpPost]
public ActionResult Upload(HttpPostedFileBase file, string description)
{
    // Content-Type: multipart/form-data
}
```

### 过滤器

```csharp
[Authorize]  // 全控制器鉴权
public class AdminController : Controller
{
    [AllowAnonymous]  // 此方法免鉴权
    public ActionResult Login() { ... }

    [Authorize(Roles = "SuperAdmin")]
    public ActionResult DeleteUser(int id) { ... }
}
```
