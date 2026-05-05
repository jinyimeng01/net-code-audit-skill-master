# 自定义 Middleware / Module 鉴权审计

## 目录

- [ASP.NET Core 自定义 Middleware](#aspnet-core-自定义-middleware)
- [ASP.NET 自定义 HttpModule](#aspnet-自定义-httpmodule)
- [常见漏洞模式](#常见漏洞模式)
- [审计检查清单](#审计检查清单)

---

## ASP.NET Core 自定义 Middleware

### 识别特征

```csharp
public class AuthMiddleware
{
    private readonly RequestDelegate _next;

    public AuthMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // 自定义鉴权逻辑
        var path = context.Request.Path;
        // ...
        await _next(context);
    }
}

// 注册
app.UseMiddleware<AuthMiddleware>();
```

### 常见危险模式

```csharp
// 危险：路径获取方式
var path = context.Request.Path.Value;  // 原样返回

// 危险：字符串匹配
if (path.StartsWith("/admin"))  // 可被 /admin/ 绕过
if (path.Contains("/admin"))   // 可被 /public/admin 绕过
if (path.Equals("/admin"))     // 可被 /admin/ 绕过

// 危险：白名单检查
if (path.EndsWith(".js") || path.EndsWith(".css"))
{
    await _next(context);  // 放行静态资源
    return;
}
```

### 安全模式

```csharp
public async Task InvokeAsync(HttpContext context)
{
    // 安全：使用框架提供的认证信息
    if (!context.User.Identity?.IsAuthenticated ?? true)
    {
        context.Response.StatusCode = 401;
        return;
    }

    await _next(context);
}
```

---

## ASP.NET 自定义 HttpModule

### 识别特征

```csharp
public class AuthModule : IHttpModule
{
    public void Init(HttpApplication context)
    {
        context.BeginRequest += OnBeginRequest;
    }

    private void OnBeginRequest(object sender, EventArgs e)
    {
        var context = ((HttpApplication)sender).Context;
        var path = context.Request.Path;
        // 自定义鉴权逻辑
    }
}
```

### web.config 注册

```xml
<system.webServer>
  <modules>
    <add name="AuthModule" type="Namespace.AuthModule" />
  </modules>
</system.webServer>
```

### 常见危险模式

```csharp
// 危险：使用 Request.Path 进行匹配
var path = context.Request.Path;

// 危险：不检查 HTTP 方法
// GET /admin 可能被拦截，但 PUT /admin 可能放行

// 危险：不检查查询参数
// /admin?action=delete 可能被放行
```

---

## 常见漏洞模式

### 1. 路径获取方式不当

```csharp
// 危险：原样返回
var path = context.Request.Path.Value;

// 安全：使用框架 API
var path = context.Request.Path;  // 已解码
```

### 2. 匹配逻辑不严谨

```csharp
// 危险：前缀匹配可绕过
if (path.StartsWith("/admin"))
// /admin123 也会被拦截（误报）
// /ADMIN 不会被拦截（漏报）

// 安全：使用路由匹配
if (endpoint?.Metadata?.GetMetadata<AuthorizeAttribute>() != null)
```

### 3. 静态资源白名单绕过

```csharp
// 危险：后缀白名单
if (path.EndsWith(".js"))
{
    await _next(context);  // /admin;.js 可绕过
    return;
}

// 安全：使用 StaticFileOptions 配置
app.UseStaticFiles(new StaticFileOptions
{
    ServeUnknownFileTypes = true,
    DefaultContentType = "application/octet-stream"
});
```

### 4. 中间件注册顺序

```csharp
// 危险：鉴权中间件在路由之后
app.UseRouting();
app.UseEndpoints(...);
app.UseMiddleware<AuthMiddleware>();  // 太晚了

// 安全：鉴权中间件在路由之前
app.UseMiddleware<AuthMiddleware>();
app.UseRouting();
app.UseEndpoints(...);
```

### 5. 异常处理泄露信息

```csharp
// 危险：异常中泄露路径信息
try
{
    await _next(context);
}
catch (Exception ex)
{
    await context.Response.WriteAsync($"Error: {ex.Message}");  // 可能泄露文件路径
}
```

---

## 审计检查清单

### Middleware 审计

- [ ] 路径获取方式是否安全
- [ ] 匹配逻辑是否严谨（正则/框架 API vs 字符串匹配）
- [ ] 是否有静态资源白名单
- [ ] 中间件注册顺序是否正确
- [ ] 是否检查 HTTP 方法
- [ ] 异常处理是否安全

### HttpModule 审计

- [ ] web.config 注册是否正确
- [ ] 事件绑定是否正确（BeginRequest vs AuthenticateRequest）
- [ ] 路径匹配是否安全
- [ ] 是否与 Forms Authentication 冲突

### 通用检查

- [ ] 是否与框架鉴权（[Authorize]）冲突
- [ ] 是否有路径规范化处理
- [ ] 是否有编码处理
- [ ] 是否有双重鉴权（Middleware + [Authorize]）
