# ASP.NET Web API 路由分析

## 目录

- [项目识别](#项目识别)
- [配置文件](#配置文件)
- [路由属性](#路由属性)
- [参数绑定](#参数绑定)
- [HTTP 方法映射](#http-方法映射)
- [常见模式](#常见模式)

---

## 项目识别

**特征文件：**
```
packages.config / *.csproj - Microsoft.AspNet.WebApi.Core 依赖
App_Start/WebApiConfig.cs - Web API 路由配置
Global.asax.cs - 应用启动配置
Controllers/ - ApiController 所在目录
```

**特征类：**
```csharp
System.Web.Http.ApiController
System.Web.Http.IHttpActionResult
System.Net.Http.HttpResponseMessage
```

---

## 配置文件

### WebApiConfig.cs

```csharp
public static class WebApiConfig
{
    public static void Register(HttpConfiguration config)
    {
        // 约定式路由
        config.Routes.MapHttpRoute(
            name: "DefaultApi",
            routeTemplate: "api/{controller}/{id}",
            defaults: new { id = RouteParameter.Optional }
        );

        // 属性路由
        config.MapHttpAttributeRoutes();
    }
}
```

**提取规则：**
- `routeTemplate` 定义 URL 模式
- `MapHttpAttributeRoutes()` 启用属性路由
- Web API 路由与 MVC 路由独立

### Global.asax.cs

```csharp
protected void Application_Start()
{
    GlobalConfiguration.Configure(WebApiConfig.Register);
}
```

---

## 路由属性

### [RoutePrefix] 类级别前缀

```csharp
[RoutePrefix("api/users")]
public class UserController : ApiController
{
    // 所有方法路径前缀为 /api/users
}
```

### [Route] 方法级别路由

```csharp
[RoutePrefix("api/users")]
public class UserController : ApiController
{
    [Route("")]
    public IHttpActionResult GetAll() { ... }        // GET /api/users

    [Route("{id:int}")]
    public IHttpActionResult GetById(int id) { ... } // GET /api/users/123

    [Route("{id}/orders")]
    public IHttpActionResult GetOrders(int id) { ... } // GET /api/users/123/orders
}
```

### 独立 [Route]（无前缀）

```csharp
public class UserController : ApiController
{
    [Route("api/users")]
    public IHttpActionResult GetAll() { ... }

    [Route("api/users/{id}")]
    public IHttpActionResult GetById(int id) { ... }
}
```

### [Route] 属性模板

| 模板 | 说明 | 示例 URL |
|------|------|----------|
| `"{id}"` | 单参数 | `/api/users/123` |
| `"{id:int}"` | 带约束 | `/api/users/123` |
| `"{*path}"` | 通配符 | `/api/files/a/b/c` |
| `"{id}/{subId}"` | 多参数 | `/api/users/123/orders/456` |

---

## 参数绑定

### [FromUri] 查询/路径参数

```csharp
[Route("search")]
public IHttpActionResult Search([FromUri] SearchQuery query)
{
    // GET /api/users/search?Keyword=test&Page=1
}
```

### [FromBody] 请求体参数

```csharp
[Route("")]
[HttpPost]
public IHttpActionResult Create([FromBody] UserDto user)
{
    // POST /api/users
    // Content-Type: application/json
}
```

**注意：** Web API 中 `[FromBody]` 每个方法只能用于一个参数。

### 基本类型绑定

```csharp
[Route("{id}")]
public IHttpActionResult GetById(int id)  // 路由参数自动绑定
{
}

[Route("search")]
public IHttpActionResult Search(string keyword, int page = 1) // 查询参数自动绑定
{
}
```

### 复杂类型默认规则

| 参数类型 | 默认绑定来源 | 覆盖方式 |
|----------|-------------|----------|
| 基本类型 | FromUri | `[FromBody]` |
| 复杂类型 | FromBody | `[FromUri]` |
| string | FromUri | `[FromBody]` |
| 数组 | FromUri | `[FromBody]` |

---

## HTTP 方法映射

### 属性方式

```csharp
[HttpGet]
[Route("users")]
public IHttpActionResult GetUsers() { ... }

[HttpPost]
[Route("users")]
public IHttpActionResult CreateUser([FromBody] UserDto dto) { ... }

[HttpPut]
[Route("users/{id}")]
public IHttpActionResult UpdateUser(int id, [FromBody] UserDto dto) { ... }

[HttpDelete]
[Route("users/{id}")]
public IHttpActionResult DeleteUser(int id) { ... }

[HttpPatch]
[Route("users/{id}")]
public IHttpActionResult PatchUser(int id, [FromBody] UserDto dto) { ... }
```

### 方法名约定（无属性时）

| 方法名前缀 | HTTP 方法 | 示例 |
|-----------|-----------|------|
| `Get` | GET | `GetUsers()` → GET /api/users |
| `Post` | POST | `PostUser()` → POST /api/users |
| `Put` | PUT | `PutUser()` → PUT /api/users |
| `Delete` | DELETE | `DeleteUser()` → DELETE /api/users |
| `Patch` | PATCH | `PatchUser()` → PATCH /api/users |

### AcceptVerbs

```csharp
[AcceptVerbs("GET", "POST")]
[Route("users")]
public IHttpActionResult GetOrCreate() { ... }
```

---

## 常见模式

### RESTful CRUD

```csharp
[RoutePrefix("api/orders")]
public class OrderController : ApiController
{
    [Route("")]
    [HttpGet]
    public IHttpActionResult GetAll() { ... }

    [Route("{id:int}")]
    [HttpGet]
    public IHttpActionResult GetById(int id) { ... }

    [Route("")]
    [HttpPost]
    public IHttpActionResult Create([FromBody] OrderDto dto) { ... }

    [Route("{id:int}")]
    [HttpPut]
    public IHttpActionResult Update(int id, [FromBody] OrderDto dto) { ... }

    [Route("{id:int}")]
    [HttpDelete]
    public IHttpActionResult Delete(int id) { ... }
}
```

### OData 风格

```csharp
[Route("api/products")]
public class ProductsController : ApiController
{
    [HttpGet]
    [EnableQuery]
    public IHttpActionResult Get()
    {
        return Ok(db.Products);
    }
}
// GET /api/products?$filter=Price gt 100&$orderby=Name&$top=10
```

### 文件上传

```csharp
[Route("upload")]
[HttpPost]
public async Task<IHttpActionResult> Upload()
{
    var provider = new MultipartFormDataStreamProvider(Path.GetTempPath());
    await Request.Content.ReadAsMultipartAsync(provider);
    // ...
}
```

### IHttpActionResult 返回类型

| 返回方法 | HTTP 状态码 | 说明 |
|----------|-----------|------|
| `Ok(data)` | 200 | 成功 |
| `Created(url, data)` | 201 | 已创建 |
| `NotFound()` | 404 | 未找到 |
| `BadRequest(msg)` | 400 | 错误请求 |
| `Unauthorized()` | 401 | 未授权 |
| `Content(status, data)` | 自定义 | 自定义状态码 |
