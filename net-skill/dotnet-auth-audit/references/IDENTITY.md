# ASP.NET Core Identity 鉴权审计

## 目录

- [框架识别](#框架识别)
- [配置分析](#配置分析)
- [常见漏洞模式](#常见漏洞模式)
- [审计检查清单](#审计检查清单)

---

## 框架识别

### 识别特征

| 特征类型 | 特征内容 |
|----------|----------|
| NuGet 依赖 | `Microsoft.AspNetCore.Identity`, `Microsoft.AspNetCore.Identity.EntityFrameworkCore` |
| 核心类 | `UserManager<T>`, `SignInManager<T>`, `RoleManager<T>` |
| 数据模型 | `IdentityUser`, `IdentityRole`, `IdentityDbContext` |

---

## 配置分析

### Identity 注册配置

```csharp
services.AddIdentity<IdentityUser, IdentityRole>(options =>
{
    // 密码策略
    options.Password.RequiredLength = 8;
    options.Password.RequireNonAlphanumeric = true;
    options.Password.RequireUppercase = true;
    options.Password.RequireLowercase = true;
    options.Password.RequireDigit = true;

    // 锁定策略
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.Lockout.AllowedForNewUsers = true;

    // 用户策略
    options.User.RequireUniqueEmail = true;

    // 登录策略
    options.SignIn.RequireConfirmedEmail = false;  // 检查点：是否要求邮箱验证
    options.SignIn.RequireConfirmedPhoneNumber = false;
})
.AddEntityFrameworkStores<ApplicationDbContext>()
.AddDefaultTokenProviders();
```

---

## 常见漏洞模式

### 1. 弱密码策略

```csharp
// 危险：弱密码策略
services.AddIdentity<IdentityUser, IdentityRole>(options =>
{
    options.Password.RequiredLength = 6;
    options.Password.RequireNonAlphanumeric = false;
    options.Password.RequireUppercase = false;
    options.Password.RequireLowercase = false;
    options.Password.RequireDigit = false;
});
```

### 2. 未启用账户锁定

```csharp
// 危险：未启用锁定
options.Lockout.AllowedForNewUsers = false;
options.Lockout.MaxFailedAccessAttempts = int.MaxValue;
```

### 3. 用户枚举

```csharp
// 危险：登录时区分"用户不存在"和"密码错误"
var result = await _signInManager.PasswordSignInAsync(model.Username, model.Password, false, false);
if (result.IsNotAllowed)
{
    return BadRequest("User not found");  // 泄露用户是否存在
}
if (!result.Succeeded)
{
    return BadRequest("Invalid password");
}

// 安全：统一错误消息
if (!result.Succeeded)
{
    return BadRequest("Invalid username or password");
}
```

### 4. 邮箱确认绕过

```csharp
// 危险：不要求邮箱确认
options.SignIn.RequireConfirmedEmail = false;

// 用户可注册任意邮箱，无需验证
```

### 5. Token 提供者配置

```csharp
// 检查点：Token 生成是否安全
options.Tokens.EmailConfirmationTokenProvider = TokenOptions.DefaultProvider;
options.Tokens.PasswordResetTokenProvider = TokenOptions.DefaultProvider;

// 危险：使用默认 DataProtectorTokenProvider 且密钥弱
```

---

## 审计检查清单

### 密码安全

- [ ] 密码长度 >= 8
- [ ] 密码复杂度要求合理
- [ ] 是否有密码历史检查
- [ ] 是否有常见密码黑名单

### 账户锁定

- [ ] 是否启用账户锁定
- [ ] 锁定时间是否合理
- [ ] 最大失败次数是否合理

### 用户注册

- [ ] 是否要求邮箱确认
- [ ] 注册接口是否有防刷机制
- [ ] 是否有 CAPTCHA

### 登录安全

- [ ] 错误消息是否统一
- [ ] 是否有双因素认证
- [ ] 记住我功能是否安全
