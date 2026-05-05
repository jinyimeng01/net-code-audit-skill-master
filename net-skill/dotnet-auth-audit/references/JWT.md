# JWT Token 鉴权审计

## 目录

- [框架识别](#框架识别)
- [JWT 结构分析](#jwt-结构分析)
- [实现审计](#实现审计)
- [常见漏洞模式](#常见漏洞模式)
- [审计检查清单](#审计检查清单)

---

## 框架识别

### 识别特征

| 特征类型 | 特征内容 |
|----------|----------|
| NuGet 依赖 | `Microsoft.AspNetCore.Authentication.JwtBearer`, `System.IdentityModel.Tokens.Jwt` |
| 请求头 | `Authorization: Bearer <token>` |
| 核心类 | `JwtSecurityTokenHandler`, `TokenValidationParameters`, `ClaimsPrincipal` |

### 常用 JWT 库

```xml
<!-- ASP.NET Core JWT Bearer -->
<PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="6.0.0" />

<!-- JWT Handler -->
<PackageReference Include="System.IdentityModel.Tokens.Jwt" Version="6.20.0" />
```

---

## JWT 结构分析

### JWT 组成

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.    # Header
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikp.  # Payload
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  # Signature
```

### Header 检查

```json
{
  "alg": "HS256",  // 算法 - 检查是否为 none
  "typ": "JWT"
}
```

### Payload 检查

```json
{
  "sub": "1234567890",     // 主题 (用户ID)
  "name": "John Doe",      // 自定义声明
  "role": "admin",         // 权限信息
  "iat": 1516239022,       // 签发时间
  "exp": 1516242622,       // 过期时间
  "nbf": 1516239022        // 生效时间
}
```

---

## 实现审计

### Token 生成审计

```csharp
public class JwtService
{
    // 检查点 1: 密钥管理
    private static readonly string SecretKey = "mySecretKey123";  // 硬编码密钥!

    // 检查点 2: 密钥强度
    // 密钥太短，容易被暴力破解

    public string GenerateToken(User user)
    {
        var claims = new[]
        {
            new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),

            // 检查点 3: 过期时间
            // 30天太长
            new Claim(JwtRegisteredClaimNames.Exp,
                new DateTimeOffset(DateTime.Now.AddDays(30)).ToUnixTimeSeconds().ToString()),

            // 检查点 4: 敏感信息
            new Claim("password", user.PasswordHash),  // 不应包含密码!

            // 检查点 5: 权限信息
            new Claim(ClaimTypes.Role, user.Role)
        };

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(SecretKey));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: "myapp",
            audience: "myapp",
            claims: claims,
            expires: DateTime.Now.AddDays(30),  // 检查点 3: 过期时间过长
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

### Token 验证审计

```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
        .AddJwtBearer(options =>
        {
            options.TokenValidationParameters = new TokenValidationParameters
            {
                // 检查点 1: 是否验证签发者
                ValidateIssuer = true,
                ValidIssuer = "myapp",

                // 检查点 2: 是否验证受众
                ValidateAudience = true,
                ValidAudience = "myapp",

                // 检查点 3: 是否验证生命周期
                ValidateLifetime = true,

                // 检查点 4: 是否验证签名密钥
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(
                    Encoding.UTF8.GetBytes(Configuration["Jwt:Key"])),

                // 检查点 5: 签名算法验证
                // 默认允许 RS256/HS256 等，需确认是否限制
            };
        });
}
```

---

## 常见漏洞模式

### 1. Algorithm None 攻击

```csharp
// 漏洞: 未限制签名算法
// 攻击者可以将 header 改为 {"alg": "none"}
// 并移除签名部分，绕过签名验证

// 安全：显式限制算法
options.TokenValidationParameters.ValidAlgorithms = new[] { "HS256", "RS256" };
```

### 2. 密钥弱强度

```csharp
// 危险：弱密钥
private static readonly string Secret = "secret";  // 太短
private static readonly string Secret = "123456";  // 常见密码

// 安全：强密钥（至少 256 bits / 32 bytes）
private static readonly string Secret = "aVeryLongAndRandomSecretKeyThatIsAtLeast256BitsLong!@#$%";
```

### 3. 密钥硬编码

```csharp
// 危险：硬编码密钥
private static readonly string SecretKey = "mySecretKey123";

// 安全：从配置读取
var key = Configuration["Jwt:Key"];  // 从 appsettings.json 或环境变量
```

### 4. 过期时间过长

```csharp
// 危险：过期时间 30 天
expires: DateTime.Now.AddDays(30)

// 安全：Access Token 15 分钟
expires: DateTime.Now.AddMinutes(15)
```

### 5. 敏感信息泄露

```csharp
// 危险：Token 中包含敏感信息
new Claim("password", user.PasswordHash)
new Claim("email", user.Email)
new Claim("phone", user.PhoneNumber)

// JWT payload 是 base64 编码，可被解码
```

### 6. 无 Token 吊销机制

```csharp
// 危险：无法使已签发的 Token 失效
// 用户修改密码、被禁用后，旧 Token 仍然有效

// 安全：实现 Token 黑名单或短过期 + Refresh Token
```

### 7. 未验证用户状态

```csharp
// 危险：仅验证 Token，未验证用户状态
var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
// 直接使用 userId，未检查用户是否仍然有效

// 安全：验证用户状态
var user = await _userManager.FindByIdAsync(userId);
if (user == null || !user.IsActive)
{
    return Unauthorized();
}
```

### 8. Algorithm Confusion 攻击

```csharp
// 危险：RS256 到 HS256 的算法混淆
// 如果系统使用 RS256，攻击者可以：
// 1. 获取公钥
// 2. 将算法改为 HS256
// 3. 用公钥作为 HS256 的密钥签名

// 安全：显式指定允许的算法
options.TokenValidationParameters.ValidAlgorithms = new[] { "RS256" };
```

---

## 审计检查清单

### 密钥安全

- [ ] 密钥是否硬编码
- [ ] 密钥强度是否足够 (>= 256 bits)
- [ ] 密钥是否定期轮换
- [ ] 密钥是否安全存储（appsettings.json + 环境变量 / Key Vault）

### Token 生成

- [ ] 过期时间是否合理 (Access Token <= 15min)
- [ ] 是否包含敏感信息
- [ ] 算法选择是否安全

### Token 验证

- [ ] 是否验证签名
- [ ] 是否验证过期时间
- [ ] 是否验证算法 (防止 none 攻击)
- [ ] 是否验证用户状态
- [ ] TokenValidationParameters 各项是否全部启用

### Token 管理

- [ ] 是否有 Token 吊销机制
- [ ] 是否有 Refresh Token 机制
- [ ] Refresh Token 是否安全存储
