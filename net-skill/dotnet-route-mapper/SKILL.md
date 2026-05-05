---
name: dotnet-route-mapper
version: 2.0.0
description: .NET 路由与参数枚举 skill。覆盖 ASP.NET Core Minimal API / MVC / Web API、ASP.NET WebForms、WCF OperationContract、ASHX / ASMX / SVC。输出全量路由表、参数来源、HTTP 方法、Burp 请求模板。
description_en: .NET route & parameter enumeration skill. Covers ASP.NET Core Minimal API, MVC, Web API, WebForms, WCF OperationContract, ASHX/ASMX/SVC. Outputs full route tables, parameter sources, HTTP methods, and Burp request templates.
author: net-code-audit-team
tags: ['dotnet', 'route-mapping', 'recon', 'attack-surface']
compatibility: ['asp.net', 'asp.net-core', 'wcf']
---

# .NET Source Route & Parameter Mapper

从 .NET Web 项目源码或反编译结果中提取所有 HTTP 路由与请求参数结构，生成 Burp Suite Repeater 请求模板。**不进行安全漏洞评估、代码质量分析或任何路由提取范围之外的内容输出。**

## 核心要求：完整输出

**此技能必须输出所有发现的接口，不允许省略。**

- 必须每个接口都有完整的参数分析
- 必须每个接口都有 Burp Suite 请求模板（必须放在 md 代码块中）
- 必须输出接口总数和清单供核对
- 禁止使用"..."、"等"、"其他"省略
- 禁止只输出"关键接口"或"重要接口"
- 禁止因为数量大而省略

---

## 漏洞分级标准

**详见 [SEVERITY_RATING.md](../shared/SEVERITY_RATING.md)**

---

## 反编译支持（CRITICAL）

**当源码不可用（只有 .dll/.exe）时，必须使用 dnSpy.Console.exe 反编译。**

详细策略参见 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md)

### 反编译命令

```bash
# 反编译整个 bin 目录
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r bin/

# 反编译单个程序集
mkdir -p {output_path}/decompiled/MyApp
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled/MyApp -r bin/MyApp.dll
```

### 必须反编译的目标

| 类型 | 匹配模式 | 目的 |
|------|----------|------|
| Controller | `*Controller.dll` | 提取路由和 Action 方法 |
| Handler | `*Handler.dll` | 提取 HTTP Handler 映射 |
| WCF Service | `*Service.dll` | 提取服务端点和操作契约 |
| Module | `*Module.dll` | 提取 IHttpModule 路由拦截 |
| API | `*Api.dll`, `*Web.dll` | 提取 Web API 路由 |

---

## 工作流程

### 1. 项目扫描初始化

```
输入: 项目源码路径或编译输出路径
      可选: 项目上下文路径、已知框架信息
```

**初始化步骤：**

1. 识别项目类型和框架（通过配置文件和目录结构）
2. 确定路由加载方式（注解/属性驱动 / XML 配置 / 混合）
3. 提取基础 URL 和虚拟路径

### 2. 框架识别与任务制定

| 框架 | 识别特征 | 配置文件 | 参考资料 |
|------|---------|---------|---------|
| ASP.NET WebForms | `.aspx`/`.asmx`/`.ashx` 文件、`Page` 类 | `web.config` | [WEBFORMS.md](references/WEBFORMS.md) |
| ASP.NET MVC | `Controller` 类、`[Route]`/`[HttpGet]` 属性 | `RouteConfig.cs`、`web.config` | [MVC.md](references/MVC.md) |
| ASP.NET Web API | `ApiController` 类、`[RoutePrefix]` | `WebApiConfig.cs` | [WEBAPI.md](references/WEBAPI.md) |
| ASP.NET Core | `ControllerBase`、`[ApiController]`、`Program.cs` | `Program.cs`、`appsettings.json` | [ASPNETCORE.md](references/ASPNETCORE.md) |
| WCF Service | `ServiceContract`、`OperationContract` | `web.config`、`*.svc` | [WCF.md](references/WCF.md) |

### 3. 路由枚举

扫描项目源码或反编译结果，提取所有对外可访问的 HTTP 路由。

**扫描范围：**
- ASP.NET WebForms: `.aspx`/`.asmx`/`.ashx` 文件
- ASP.NET MVC: `Controller` 类的 `Action` 方法
- ASP.NET Web API: `ApiController` 的 Action 方法
- ASP.NET Core: `Controller`/`ControllerBase` 的 Action 方法
- WCF Service: `ServiceContract` 定义的操作

### 4. 参数结构解析

对每个路由解析其参数结构。

**参数来源：**
- **Query 参数**: `[FromQuery]`、`Request.QueryString`
- **Body 参数**: `[FromBody]`、`Request.Form`、`Request.InputStream`
- **Route 参数**: `[FromRoute]`、路由模板 `{id}`
- **Header 参数**: `[FromHeader]`、`Request.Headers`
- **Cookie 参数**: `Request.Cookies`

### 5. 生成输出

**严格按照 references/ 目录中的填充式模板生成输出文件。**

| 文件类型 | 模板 | 命名格式 | 数量 |
|---------|------|---------|------|
| 主索引 | [OUTPUT_TEMPLATE_INDEX.md](references/OUTPUT_TEMPLATE_INDEX.md) | `route_mapper/{project_name}_route_mapper_{YYYYMMDD_HHMMSS}.md` | 1 个 |
| 模块详情 | [OUTPUT_TEMPLATE_MODULE.md](references/OUTPUT_TEMPLATE_MODULE.md) | `route_mapper/{module_name}/{project_name}_module_{module_name}_{YYYYMMDD_HHMMSS}.md` | N 个 |
| 说明文档 | [OUTPUT_TEMPLATE_README.md](references/OUTPUT_TEMPLATE_README.md) | `route_mapper/{project_name}_route_README_{YYYYMMDD_HHMMSS}.md` | 1 个 |

---

## 各框架路由输出格式

### ASP.NET MVC / Web API / Core 路由

```markdown
=== [1] GET /api/users/{id} ===
位置: UserController.GetUser (UserController.cs:45)
HTTP 方法: GET
URL 路径: /api/users/{id}

参数结构:
  Route: {id} (int) - 用户ID
  Header: Authorization - Bearer Token

Burp Suite 请求模板:
\```http
GET /api/users/{{id}} HTTP/1.1
Host: {{host}}
Authorization: Bearer {{token}}
\```
```

### ASP.NET WebForms 路由

```markdown
=== [1] POST /Login.aspx ===
位置: Login.Page_Load (Login.aspx.cs:15)
HTTP 方法: POST
URL 路径: /Login.aspx

参数结构:
  Body: application/x-www-form-urlencoded
    - txtUsername (String) - 用户名
    - txtPassword (String) - 密码
    - __VIEWSTATE (String) - ASP.NET 视图状态
    - __EVENTVALIDATION (String) - 事件验证

Burp Suite 请求模板:
\```http
POST /Login.aspx HTTP/1.1
Host: {{host}}
Content-Type: application/x-www-form-urlencoded

txtUsername={{username}}&txtPassword={{password}}&__VIEWSTATE={{viewstate}}&__EVENTVALIDATION={{eventvalidation}}
\```
```

### WCF Service 路由

```markdown
=== [1] POST /UserService.svc ===
位置: IUserService.GetUser (UserService.cs:20)
绑定: basicHttpBinding
操作: GetUser

参数结构:
  Body: SOAP XML
    - userId (String) - 用户ID

Burp Suite 请求模板:
\```http
POST /UserService.svc HTTP/1.1
Host: {{host}}
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://tempuri.org/IUserService/GetUser"

<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetUser xmlns="http://tempuri.org/">
      <userId>{{userId}}</userId>
    </GetUser>
  </soap:Body>
</soap:Envelope>
\```
```

---

## 禁止的输出格式

| 禁止模式 | 错误示例 | 正确做法 |
|:---------|:---------|:---------|
| 使用"等"省略 | `UserController, OrderController等` | 列出全部 Controller |
| 使用"..."省略 | `method1, method2, ...` | 列出全部方法 |
| 使用"其他"省略 | `以及其他20个方法` | 列出全部20个方法 |
| 只给 WSDL 地址 | `请通过 WSDL 查看可用方法` | 列出所有 SOAP 方法 |

---

## 完成性检查清单

**在标记任务完成前，必须执行以下检查：**

- [ ] 主索引文件已生成
- [ ] README 说明文档已生成
- [ ] 主索引中列出的每个模块都有对应的详情文件
- [ ] 每个详情文件都包含完整的路由信息
- [ ] 所有文件链接可访问
- [ ] 反编译来源已标注（如适用）
