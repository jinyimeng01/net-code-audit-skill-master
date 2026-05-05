# ASP.NET Core 路由分析

## 目录

- [项目识别](#项目识别)
- [端点配置](#端点配置)
- [ControllerBase 识别](#controllerbase-识别)
- [参数绑定](#参数绑定)
- [Minimal API](#minimal-api)
- [Razor Pages](#razor-pages)
- [常见模式](#常见模式)

---

## 项目识别

**特征文件：**
```
*.csproj - Microsoft.AspNetCore.App 框架引用
Program.cs - 应用配置（.NET 6+）或 Startup.cs（.NET 5-）
appsettings.json - 应用配置
Controllers/ - 控制器目录
Pages/ - Razor Pages 目录
```

**特征类：**
```csharp
Microsoft.AspNetCore.Mvc.ControllerBase
Microsoft.AspNetCore.Mvc.Controller
Microsoft.AspNetCore.Mvc.RazorPages.PageModel
Microsoft.AspNetCore.Builder.WebApplication
```

---

## 端点配置

### Program.cs (.NET 6+)

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddRazorPages();

var app = builder.Build();

app.MapControllers();         // 映射属性路由控制器
app.MapRazorPages();          // 映射 Razor Pages
app.MapControllerRoute(       // 映射约定式路由
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

// Minimal API 端点
app.MapGet("/api/health", () => "OK");
app.MapPost("/api/data", (DataDto data) => Results.Ok(data));

app.Run();
```

### Startup.cs (.NET 5 及以下)

```csharp
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        services.AddControllers();
        services.AddRazorPages();
    }

    public void Configure(IApplicationBuilder app)
    {
        app.UseRouting();
        app.UseEndpoints(endpoints =>
        {
            endpoints.MapControllers();
            endpoints.MapRazorPages();
            endpoints.MapControllerRoute(
                name: "default",
                pattern: "{controller=Home}/{action=Index}/{id?}");
        });
    }
}
```

---

## ControllerBase 识别

### [ApiController] 属性

```csharp
[ApiController]
[Route("api/[controller]")]   // 路由模板: /api/User
public class UserController : ControllerBase
{
    [HttpGet]
    public IEnumerable<User> GetAll() { ... }

    [HttpGet("{id}")]
    public User GetById(int id) { ... }

    [HttpPost]
    public ActionResult<User> Create(UserDto dto) { ... }

    [HttpPut("{id}")]
    public IActionResult Update(int id, UserDto dto) { ... }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id) { ... }
}
```

**[ApiController] 行为：**
- 自动 HTTP 400 响应（模型验证失败）
- 推断参数来源（[FromBody] / [FromQuery] 等）
- 推断多部分/表单数据请求
- 属性路由要求

### 路由模板

| 模板 | 说明 | 示例 URL |
|------|------|----------|
| `"[controller]"` | 控制器名 | `/User` |
| `"[action]"` | Action 名 | `/User/List` |
| `"api/[controller]"` | 带前缀 | `/api/User` |
| `"{id:int}"` | 约束参数 | `/api/User/123` |
| `"{**path}"` | catch-all | `/api/files/a/b/c` |

### HTTP 方法属性

| 属性 | HTTP 方法 | 示例 |
|------|-----------|------|
| `[HttpGet]` | GET | `[HttpGet("{id}")]` |
| `[HttpPost]` | POST | `[HttpPost]` |
| `[HttpPut]` | PUT | `[HttpPut("{id}")]` |
| `[HttpDelete]` | DELETE | `[HttpDelete("{id}")]` |
| `[HttpPatch]` | PATCH | `[HttpPatch("{id}")]` |

---

## 参数绑定

### [FromQuery] 查询参数

```csharp
[HttpGet("search")]
public ActionResult<List<User>> Search([FromQuery] string keyword, [FromQuery] int page = 1)
{
    // GET /api/user/search?keyword=test&page=1
}
```

### [FromRoute] 路由参数

```csharp
[HttpGet("{id:int}")]
public ActionResult<User> GetById([FromRoute] int id)
{
    // GET /api/user/123
}
```

### [FromBody] 请求体

```csharp
[HttpPost]
public ActionResult<User> Create([FromBody] UserDto dto)
{
    // POST /api/user
    // Content-Type: application/json
}
```

### [FromForm] 表单参数

```csharp
[HttpPost("upload")]
public IActionResult Upload([FromForm] IFormFile file, [FromForm] string description)
{
    // Content-Type: multipart/form-data
}
```

### [FromHeader] 请求头

```csharp
[HttpGet("data")]
public ActionResult GetData([FromHeader] string authorization)
{
}
```

### [FromServices] 依赖注入

```csharp
[HttpGet("config")]
public ActionResult GetConfig([FromServices] IConfiguration config)
{
}
```

### 参数推断规则（[ApiController]）

| 参数类型 | 推断来源 |
|----------|---------|
| 基本类型 (int, string, bool...) | [FromQuery] |
| 复杂类型 | [FromBody] |
| IFormFile | [FromForm] |
| IFormCollection | [FromForm] |
| 服务类型 | [FromServices] |

---

## Minimal API

### 基本端点

```csharp
app.MapGet("/api/users", (AppDbContext db) => db.Users.ToList());

app.MapGet("/api/users/{id}", (int id, AppDbContext db) =>
    db.Users.Find(id) is User user ? Results.Ok(user) : Results.NotFound());

app.MapPost("/api/users", (UserDto dto, AppDbContext db) =>
{
    var user = new User { Name = dto.Name };
    db.Users.Add(user);
    db.SaveChanges();
    return Results.Created($"/api/users/{user.Id}", user);
});

app.MapPut("/api/users/{id}", (int id, UserDto dto, AppDbContext db) =>
{
    var user = db.Users.Find(id);
    if (user is null) return Results.NotFound();
    user.Name = dto.Name;
    db.SaveChanges();
    return Results.NoContent();
});

app.MapDelete("/api/users/{id}", (int id, AppDbContext db) =>
{
    var user = db.Users.Find(id);
    if (user is null) return Results.NotFound();
    db.Users.Remove(user);
    db.SaveChanges();
    return Results.NoContent();
});
```

### 带过滤器的端点

```csharp
app.MapGet("/api/admin/users", (AppDbContext db) => db.Users.ToList())
    .RequireAuthorization("AdminPolicy");

app.MapGet("/api/public/config", () => new { Version = "1.0" })
    .AllowAnonymous();
```

### 参数来源

```csharp
app.MapPost("/api/upload", (IFormFile file, HttpContext context) =>
{
    // IFormFile 自动从表单绑定
    // HttpContext 注入请求上下文
});
```

---

## Razor Pages

### 页面模型

```csharp
// Pages/Users/Index.cshtml.cs
public class IndexModel : PageModel
{
    public List<User> Users { get; set; }

    public void OnGet()
    {
        // GET /Users
        Users = _dbContext.Users.ToList();
    }
}
```

### 处理方法

```csharp
// Pages/Users/Create.cshtml.cs
public class CreateModel : PageModel
{
    [BindProperty]
    public UserDto User { get; set; }

    public void OnGet()
    {
        // GET /Users/Create - 显示表单
    }

    public IActionResult OnPost()
    {
        // POST /Users/Create - 提交表单
        if (!ModelState.IsValid) return Page();
        // 保存逻辑
        return RedirectToPage("./Index");
    }

    public IActionResult OnPostDelete(int id)
    {
        // POST /Users/Create?handler=Delete
        // 或 POST /Users/Create/Delete (自定义)
        return RedirectToPage("./Index");
    }
}
```

### 处理方法命名

| 方法名 | HTTP 方法 | URL |
|--------|-----------|-----|
| `OnGet` | GET | `/Users/Create` |
| `OnPost` | POST | `/Users/Create` |
| `OnPostDelete` | POST | `/Users/Create?handler=Delete` |
| `OnPut` | PUT | `/Users/Create` |
| `OnDelete` | DELETE | `/Users/Create` |

### 自定义路由

```csharp
@page "/users/{id:int}"
@model EditModel

public class EditModel : PageModel
{
    [BindProperty]
    public UserDto User { get; set; }

    public IActionResult OnGet(int id)
    {
        // GET /users/123
    }

    public IActionResult OnPost(int id)
    {
        // POST /users/123
    }
}
```

---

## 常见模式

### RESTful API

```csharp
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    [HttpGet]
    public ActionResult<PagedResult<Product>> List([FromQuery] int page = 1, [FromQuery] int size = 20)
    {
        // GET /api/products?page=1&size=20
    }

    [HttpGet("{id}")]
    public ActionResult<Product> Get(int id)
    {
        // GET /api/products/123
    }

    [HttpPost]
    public ActionResult<Product> Create(ProductDto dto)
    {
        // POST /api/products
    }

    [HttpPut("{id}")]
    public IActionResult Update(int id, ProductDto dto)
    {
        // PUT /api/products/123
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        // DELETE /api/products/123
    }
}
```

### 中间件端点

```csharp
app.Map("/api/legacy/{**path}", (HttpContext context) =>
{
    // 匹配 /api/legacy/ 下的所有路径
});
```
