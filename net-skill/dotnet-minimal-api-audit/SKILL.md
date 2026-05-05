---
name: dotnet-minimal-api-audit
version: 2.0.0
description: .NET Minimal API 安全审计 skill。覆盖 ASP.NET Core 6+ Minimal API 的路由注册、Endpoint Filter、Request Delegate、Source Generator、绑定模型、OpenAPI/Swagger 集成。追踪用户可控输入到文件、命令、数据库、反序列化等 sink，输出漏洞证据和修复建议。
description_en: .NET Minimal API security audit skill. Covers ASP.NET Core 6+ Minimal API route registration, endpoint filters, request delegates, source generators, binding models, and OpenAPI/Swagger integration. Traces user input to file, command, database, and deserialization sinks.
author: net-code-audit-team
tags: ["dotnet","minimal-api","asp.net-core","endpoint-filter","source-generator","audit"]
compatibility: ["asp.net-core"]
---

# .NET Minimal API 审计

检查 ASP.NET Core 6+ Minimal API 项目的路由、过滤器、参数绑定和 source generator 引入的攻击面。

## 工作流

1. 搜索 `WebApplication` / `WebApplicationBuilder` 创建点，获取所有 `MapGet`、`MapPost`、`MapPut`、`MapDelete`、`MapPatch`、`MapMethods`、`MapFallback` 注册。
2. 检查 `AddEndpointFilter`、`AddEndpointFilterFactory` 的鉴权和输入校验逻辑。
3. 检查参数绑定来源：`[FromBody]`、`[FromQuery]`、`[FromRoute]`、`[FromHeader]`、`[FromServices]`、`[AsParameters]`、隐式绑定（自动从 query/body/route 绑定）。
4. 检查 Source Generator 生成的代码（如 `RequestDelegateGenerator`），确认生成的委托中是否存在绕过原始校验的路径。
5. 追踪用户可控输入到 sink：SQL、文件、命令、反序列化、SSRF、XML 解析。
6. 检查 `OpenAPI` / `Swagger` 集成是否暴露了内部 schema 或 admin 端点。
7. 输出漏洞或排除理由；默认只给无害验证和修复建议。

## Reference 选择

| 任务 | 读取 |
|---|---|
| Minimal API 路由与过滤器审计 | [MINIMAL_API_ROUTES_AND_FILTERS.md](references/MINIMAL_API_ROUTES_AND_FILTERS.md) |
| Source Generator 安全影响 | [SOURCE_GENERATOR_SECURITY.md](references/SOURCE_GENERATOR_SECURITY.md) |
| OpenAPI / Swagger 暴露 | [OPENAPI_EXPOSURE.md](references/OPENAPI_EXPOSURE.md) |

## 高危 sink 速查

| Sink | 危险条件 |
|---|---|
| `MapPost("/api/{id}")` 中 `id` 直接进入 SQL | 无参数化查询 |
| `AddEndpointFilter` 中跳过鉴权 | 过滤器返回 `next(context)` 前未验证 |
| `[AsParameters]` 绑定复杂对象 | 对象属性包含未校验的文件路径或命令字符串 |
| Source Generator 生成 `RequestDelegate` | 生成代码中绕过了原始输入校验 |
| `OpenApiDocument` 暴露内部类型 | Swagger UI 未启用认证，暴露了 admin/schema |

## 输出要求

- 漏洞编号格式：`{C/H/M/L}-MINAPI-{序号}`。
- 必须说明 endpoint path、HTTP method、参数来源、过滤器状态、source generator 影响、调用链、sink。
- 修复优先建议：使用 Endpoint Filter 做统一鉴权/校验、参数化查询、DTO allowlist、禁用不必要的 Swagger 暴露。

## 自检

- [ ] 已覆盖全部 `Map*` 注册点。
- [ ] 已检查所有 `AddEndpointFilter` / `AddEndpointFilterFactory`。
- [ ] 已确认 Source Generator 生成代码中的安全边界。
- [ ] 已评估 OpenAPI / Swagger 暴露面。
- [ ] 每个 sink 都有输入可控性结论。
