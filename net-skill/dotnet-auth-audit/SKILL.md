---
name: dotnet-auth-audit
version: 2.0.0
description: .NET 鉴权与越权审计 skill。覆盖 FormsAuth、ASP.NET Core Identity、JWT、OAuth/OIDC、Windows Auth、Membership、自定义鉴权模块、IDOR/BOLA/BFLA。输出路由鉴权映射、绕过模式和修复建议。
description_en: .NET authentication & authorization audit skill. Covers FormsAuth, ASP.NET Core Identity, JWT, OAuth/OIDC, Windows Auth, Membership, custom auth modules, IDOR/BOLA/BFLA. Outputs route-auth mapping, bypass patterns, and remediation.
author: net-code-audit-team
tags: ['dotnet', 'auth', 'authorization', 'jwt', 'oauth', 'idor']
compatibility: ['asp.net', 'asp.net-core', 'wcf']
---

# .NET 鉴权机制审计工具

扫描 .NET Web 项目源码或反编译结果，识别鉴权机制实现，检测鉴权绕过漏洞和越权访问缺陷。

## 漏洞分级标准

**详见 [SEVERITY_RATING.md](../shared/SEVERITY_RATING.md)**

- 漏洞编号格式: `{C/H/M/L}-AUTH-{序号}`

---

## 检测范围边界

**本技能检测范围仅包含以下类型：**
- 鉴权绕过漏洞（Bypass）
- 越权访问缺陷（Privilege Escalation）
- 会话管理缺陷
- 已知组件漏洞（CVE）

**以下不属于本技能检测范围：**
- 代码质量问题
- 通用安全漏洞（SQL 注入、XSS 等，使用专项技能）
- 架构设计建议

---

## 核心要求

**此技能必须完整检查所有鉴权相关代码，不允许省略。**

- 必须识别所有鉴权入口点（Filter/Module/Middleware/Attribute）
- 必须分析每个路由的鉴权状态
- 必须检测所有潜在的鉴权绕过模式
- 必须为每个漏洞点提供验证 PoC
- 禁止省略任何鉴权配置

---

## 技能协作流程（CRITICAL）

**dotnet-auth-audit 应在 dotnet-route-mapper 之后执行。**

```
[步骤1] dotnet-route-mapper → 路由列表 + 参数
    ↓
[步骤2] dotnet-auth-audit（本技能）→ 鉴权状态映射
    ↓
[步骤3] 输出鉴权审计报告
```

---

## 反编译支持（CRITICAL）

**当源码不可用时，必须使用 dnSpy.Console.exe 反编译鉴权相关程序集。**

```bash
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r bin/
```

### 必须反编译的目标

| 类型 | 匹配模式 | 目的 |
|------|----------|------|
| Auth Module | `*Auth*.dll`, `*Security*.dll` | 提取鉴权逻辑 |
| Filter | `*Filter*.dll` | 提取权限过滤器 |
| Identity | `*Identity*.dll` | 提取用户认证逻辑 |
| Middleware | `*Middleware*.dll` | 提取中间件鉴权 |

---

## 鉴权框架识别

### ASP.NET Core 鉴权

| 框架 | 识别特征 | 配置位置 | 参考资料 |
|------|---------|---------|---------|
| Cookie Authentication | `app.UseCookieAuthentication()` | `Program.cs`/`Startup.cs` | [ASPNETCORE_AUTH.md](references/ASPNETCORE_AUTH.md) |
| JWT Bearer | `app.UseJwtBearerAuthentication()` | `Program.cs`/`Startup.cs` | [JWT.md](references/JWT.md) |
| ASP.NET Core Identity | `AddIdentity<User, Role>()` | `Program.cs`/`Startup.cs` | [IDENTITY.md](references/IDENTITY.md) |
| Windows Authentication | `HttpListener.AuthenticationSchemes` | `Program.cs`/`web.config` | [WINDOWS_AUTH.md](references/WINDOWS_AUTH.md) |
| OAuth/OpenID Connect | `AddOAuth()`, `AddOpenIdConnect()` | `Program.cs`/`Startup.cs` | [OAUTH.md](references/OAUTH.md) |

### ASP.NET (Framework) 鉴权

| 框架 | 识别特征 | 配置位置 | 参考资料 |
|------|---------|---------|---------|
| Forms Authentication | `<authentication mode="Forms">` | `web.config` | [FORMS_AUTH.md](references/FORMS_AUTH.md) |
| Windows Authentication | `<authentication mode="Windows">` | `web.config` | [WINDOWS_AUTH.md](references/WINDOWS_AUTH.md) |
| ASP.NET Membership | `Membership.ValidateUser()` | `web.config` + 代码 | [MEMBERSHIP.md](references/MEMBERSHIP.md) |
| Custom HttpModule | `IHttpModule` + `AuthenticateRequest` | `web.config` + 代码 | [CUSTOM_MODULE.md](references/CUSTOM_MODULE.md) |
| AuthorizeAttribute | `[Authorize]`, `[Authorize(Roles=)]` | 代码属性 | [AUTHORIZE_ATTR.md](references/AUTHORIZE_ATTR.md) |

---

## 鉴权绕过检测规则

### 1. 路径绕过

| 绕过模式 | 说明 | 检测方法 |
|----------|------|---------|
| 分号绕过 | `/admin/;user` 绕过 ASP.NET 路径检查 | 检查路径规范化配置 |
| 双编码 | `%2e%2e/admin` 路径穿越 | 检查 `requestPathInvalidChars` |
| 大小写混合 | `/Admin/User` 绕过大小写敏感过滤 | 检查路由匹配规则 |
| 尾部斜杠 | `/admin/` vs `/admin` | 检查路径标准化 |

### 2. Filter/Module 绕过

| 绕过模式 | 说明 | 检测方法 |
|----------|------|---------|
| AllowAnonymous | `[AllowAnonymous]` 标注的路由无鉴权 | 检查是否有不该匿名访问的路由 |
| 顺序绕过 | Module 执行顺序导致鉴权被跳过 | 检查 `web.config` 中 module 顺序 |
| 条件缺失 | 某些 HTTP 方法未被 Filter 覆盖 | 检查 Filter 是否覆盖所有方法 |

### 3. 越权访问

| 类型 | 说明 | 检测方法 |
|------|------|---------|
| 水平越权 | 用户 A 访问用户 B 的资源 | 检查资源所有权校验 |
| 垂直越权 | 普通用户执行管理员操作 | 检查角色/权限校验 |
| IDOR | 通过修改 ID 访问他人数据 | 检查参数归属校验 |

---

## 输出格式

**严格按照 references/ 目录中的填充式模板生成输出文件。**

| 文件类型 | 模板 | 命名格式 | 数量 |
|---------|------|---------|------|
| 主报告 | [OUTPUT_TEMPLATE_MAIN.md](references/OUTPUT_TEMPLATE_MAIN.md) | `auth_audit/{project_name}_auth_audit_{timestamp}.md` | 1 个 |
| 映射表 | [OUTPUT_TEMPLATE_MAPPING.md](references/OUTPUT_TEMPLATE_MAPPING.md) | `auth_audit/{project_name}_auth_mapping_{timestamp}.md` | 1 个 |
| 说明文档 | [OUTPUT_TEMPLATE_README.md](references/OUTPUT_TEMPLATE_README.md) | `auth_audit/{project_name}_auth_README_{timestamp}.md` | 1 个 |

通用规范参考: [shared/DOTNET_OUTPUT_STANDARD.md](../shared/DOTNET_OUTPUT_STANDARD.md)

---

## 验证检查清单

- [ ] 所有鉴权框架已识别
- [ ] 每个路由的鉴权状态已分析
- [ ] 鉴权绕过模式已检测
- [ ] 越权访问缺陷已检查
- [ ] 反编译来源已标注（如适用）
- [ ] 报告已生成并通过自检清单
