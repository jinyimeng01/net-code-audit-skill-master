# ASP.NET Core 鉴权审计

## 目录

- [框架识别](#框架识别)
- [配置分析](#配置分析)
- [核心组件审计](#核心组件审计)
- [常见漏洞模式](#常见漏洞模式)
- [审计检查清单](#审计检查清单)

---

## 框架识别

### 识别特征

| 特征类型 | 特征内容 |
|----------|----------|
| NuGet 依赖 | `Microsoft.AspNetCore.Authentication`, `Microsoft.AspNetCore.Identity` |
| 中间件 | `app.UseAuthentication()`, `app.UseAuthorization()` |
| 属性 | `[Authorize]`, `[AllowAnonymous]`, `[Authorize(Roles = "...")]` |
| 配置类 | `AuthenticationOptions`, `AuthorizationOptions` |

### 版本检测

```xml
<PackageReference Include="Microsoft.AspNetCore.Authentication" Version="2.2.0" />
<PackageReference Include="Microsoft.AspNetCore.Identity" Version="2.2.0" />
```

---

## 配置分析

### ASP.NET Core 3.1+ 配置

```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
        .AddCookie(options =>
        {
            options.LoginPath = "/Account/Login";
            options.AccessDeniedPath = "/Account/AccessDenied";
        });

    services.AddAuthorization(options =>
    {
        options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
        options.AddPolicy("Over18", policy => policy.Requirements.Add(new MinimumAgeRequirement(18)));
    });
}

public void Configure(IApplicationBuilder app)
{
    app.UseAuthentication();
    app.UseAuthorization();
}
```

### ASP.NET Core 6+ Minimal API 配置

```csharp
builder.Services.AddAuthentication()
    .AddJwtBearer(options => { /* ... */ });

builder.Services.AddAuthorization();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
```

---

## 核心组件审计

### [Authorize] 属性审计

```csharp
[Authorize]  // 需要认证
public class AdminController : Controller
{
    [AllowAnonymous]  // 允许匿名
    public IActionResult Login() => View();

    [Authorize(Roles = "Admin")]  // 需要 Admin 角色
    public IActionResult Dashboard() => View();

    [Authorize(Policy = "Over18")]  // 需要满足策略
    public IActionResult Restricted() => View();
}
```

### 自定义 AuthorizationHandler 审计

```csharp
public class MinimumAgeHandler : AuthorizationHandler<MinimumAgeRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        MinimumAgeRequirement requirement)
    {
        var ageClaim = context.User.FindFirst(c => c.Type == "Age");
        if (ageClaim != null && int.Parse(ageClaim.Value) >= requirement.MinimumAge)
        {
            context.Succeed(requirement);
        }
        return Task.CompletedTask;
    }
}
```

---

## 常见漏洞模式

### 1. 缺少全局鉴权

```csharp
// 危险：未配置默认鉴权策略
services.AddAuthorization();  // 无默认策略

// 安全：配置默认鉴权策略
services.AddAuthorization(options =>
{
    options.FallbackPolicy = new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        .Build();
});
```

### 2. [AllowAnonymous] 滥用

```csharp
// 危险：在控制器级别 [Authorize]，但方法级别 [AllowAnonymous]
[Authorize]
public class AdminController : Controller
{
    [AllowAnonymous]  // 此方法完全绕过鉴权
    public IActionResult GetUsers() => Json(_userService.GetAll());
}
```

### 3. 中间件顺序错误

```csharp
// 危险：UseAuthorization 在 UseRouting 之前
app.UseAuthorization();
app.UseRouting();
app.UseEndpoints(...);

// 安全：正确顺序
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.UseEndpoints(...);
```

### 4. CORS 配置不当

```csharp
// 危险：允许所有来源带凭据
services.AddCors(options =>
{
    options.AddPolicy("AllowAll", builder =>
    {
        builder.AllowAnyOrigin()
               .AllowAnyMethod()
               .AllowAnyHeader()
               .AllowCredentials();  // 与 AllowAnyOrigin 冲突
    });
});
```

### 5. Cookie 安全配置不当

```csharp
// 危险：Cookie 安全配置不足
services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.Cookie.HttpOnly = false;  // 应为 true
        options.Cookie.SecurePolicy = CookieSecurePolicy.None;  // 应为 SameAsRequest 或 Always
        options.Cookie.SameSite = SameSiteMode.None;  // 应为 Lax 或 Strict
    });
```

### 6. Claims 未验证

```csharp
// 危险：直接使用 Claims 未验证
var role = User.FindFirst("Role")?.Value;
if (role == "Admin")
{
    // 直接信任 Claim 值
}

// 安全：使用授权策略
[Authorize(Roles = "Admin")]
public IActionResult AdminOnly() => View();
```

---

## 审计检查清单

### 配置审计

- [ ] 是否配置了默认鉴权策略（FallbackPolicy）
- [ ] 中间件顺序是否正确（Routing -> Authentication -> Authorization）
- [ ] CORS 配置是否过于宽松
- [ ] Cookie 安全配置是否完整（HttpOnly、Secure、SameSite）
- [ ] 是否有 JWT Token 验证配置

### 授权审计

- [ ] [Authorize] 属性是否正确应用
- [ ] [AllowAnonymous] 是否滥用
- [ ] 角色和策略定义是否合理
- [ ] 自定义 AuthorizationHandler 逻辑是否安全

### 认证审计

- [ ] 登录失败处理是否安全（不泄露用户信息）
- [ ] 密码策略是否足够强
- [ ] 是否有账户锁定机制
- [ ] Remember Me 功能是否安全
- [ ] 外部登录（OAuth）是否安全配置
