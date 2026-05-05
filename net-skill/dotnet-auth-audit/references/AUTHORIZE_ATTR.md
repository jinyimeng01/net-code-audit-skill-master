# [Authorize] 属性审计

## 目录

- [属性识别](#属性识别)
- [常见漏洞模式](#常见漏洞模式)
- [审计检查清单](#审计检查清单)

---

## 属性识别

### ASP.NET Core [Authorize]

```csharp
using Microsoft.AspNetCore.Authorization;

[Authorize]                    // 需要认证
[Authorize(Roles = "Admin")]   // 需要 Admin 角色
[Authorize(Policy = "Over18")] // 需要满足策略
[AllowAnonymous]               // 允许匿名访问
```

### ASP.NET MVC 5 [Authorize]

```csharp
using System.Web.Mvc;

[Authorize]                    // 需要认证
[Authorize(Roles = "Admin")]   // 需要 Admin 角色
[Authorize(Users = "john")]    // 需要特定用户
[AllowAnonymous]               // 允许匿名访问
```

### WebForms 不支持属性

WebForms 使用 `web.config` 的 `<authorization>` 节或代码中手动检查 `User.Identity.IsAuthenticated`。

---

## 常见漏洞模式

### 1. 控制器缺少 [Authorize]

```csharp
// 危险：控制器无 [Authorize]，所有方法默认公开
public class AdminController : Controller
{
    public IActionResult Dashboard() => View();
    public IActionResult Users() => View();
}

// 安全：控制器级别 [Authorize]
[Authorize(Roles = "Admin")]
public class AdminController : Controller
{
    public IActionResult Dashboard() => View();
    public IActionResult Users() => View();
}
```

### 2. [AllowAnonymous] 覆盖 [Authorize]

```csharp
[Authorize(Roles = "Admin")]
public class AdminController : Controller
{
    // 危险：[AllowAnonymous] 完全绕过控制器级别鉴权
    [AllowAnonymous]
    public IActionResult GetSecretData() => Json(_secretService.GetAll());
}
```

### 3. 仅认证无授权

```csharp
// 中危：仅检查登录状态，无角色校验
[Authorize]  // 只检查是否登录
public class AdminController : Controller
{
    public IActionResult Dashboard() => View();  // 任何登录用户都能访问
}

// 安全：添加角色校验
[Authorize(Roles = "Admin")]
public class AdminController : Controller
```

### 4. 角色字符串硬编码

```csharp
// 潜在问题：角色名硬编码，难以维护
[Authorize(Roles = "Admin,SuperAdmin")]

// 建议：使用常量或策略
[Authorize(Policy = "AdminOnly")]
```

### 5. Action 级别覆盖不一致

```csharp
[Authorize(Roles = "Admin")]
public class AdminController : Controller
{
    // 危险：方法级别缩小角色范围，逻辑混乱
    [Authorize(Roles = "SuperAdmin")]
    public IActionResult CriticalAction() => View();
}
```

### 6. API 控制器缺少鉴权

```csharp
// 危险：API 控制器无鉴权
[ApiController]
[Route("api/[controller]")]
public class UserController : ControllerBase
{
    [HttpGet("{id}")]
    public IActionResult GetUser(int id) => Json(_userService.GetById(id));
}

// 安全：添加鉴权
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class UserController : ControllerBase
{
    [HttpGet("{id}")]
    public IActionResult GetUser(int id) => Json(_userService.GetById(id));
}
```

---

## 审计检查清单

### 全局配置

- [ ] 是否配置了全局 [Authorize] 策略（FallbackPolicy）
- [ ] 是否有不需要鉴权的白名单路由

### 控制器级别

- [ ] 每个控制器是否都有 [Authorize]
- [ ] 控制器级别的角色要求是否合理

### 方法级别

- [ ] [AllowAnonymous] 是否必要
- [ ] 方法级别的角色要求是否与控制器级别一致
- [ ] 敏感方法是否有额外的角色要求

### API 控制器

- [ ] 所有 API 控制器是否都有鉴权
- [ ] REST API 的 PUT/DELETE 是否有额外角色校验
