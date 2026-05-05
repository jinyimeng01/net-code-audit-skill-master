---
name: dotnet-web-risk-audit
version: 2.0.0
description: .NET Web 综合风险审计 skill。覆盖 Razor/WebForms XSS、CSRF/SameSite、CORS Origin、Host Header 攻击、Open Redirect、IDOR/BOLA/BFLA、缓存欺骗、HTTP Request Smuggling。输出漏洞证据和修复建议。
description_en: .NET comprehensive web risk audit skill. Covers Razor/WebForms XSS, CSRF/SameSite, CORS Origin, Host Header attacks, Open Redirect, IDOR/BOLA/BFLA, cache deception, HTTP request smuggling.
author: net-code-audit-team
tags: ['dotnet', 'xss', 'csrf', 'cors', 'open-redirect', 'idor', 'web-risk']
compatibility: ['asp.net', 'asp.net-core', 'iis']
---

# .NET Web 综合风险审计

覆盖核心 sink 之外的 Web 与业务风险。详细规则参考 [WEB_RISK_PATTERNS.md](references/WEB_RISK_PATTERNS.md)，对象级权限参考 [BUSINESS_AUTHORIZATION.md](references/BUSINESS_AUTHORIZATION.md)，浏览器和代理边界参考 [BROWSER_AND_PROXY_BOUNDARIES.md](references/BROWSER_AND_PROXY_BOUNDARIES.md)。

## 工作流

1. 以 route mapper 的全量接口和 auth mapping 为基线，不只抽查高危接口。
2. 检查浏览器信任边界：XSS、CSRF、CORS、Clickjacking、安全响应头。
3. 检查服务端路由与代理边界：Open Redirect、Host Header、Forwarded Headers、缓存、IIS 短文件名和 handler 映射。
4. 检查 API/业务授权：IDOR、BOLA、BFLA、隐藏字段、批量赋值、租户隔离、角色边界、状态机绕过。
5. 需要时调用 route tracer 证明对象归属校验或状态校验缺失。
6. 对 CORS/CSRF/Host/Open Redirect 等浏览器或代理边界问题，读取边界专题。

## .NET 特有关注点

- Razor 默认编码被 `Html.Raw`、`MvcHtmlString`、`IHtmlContent`、自定义 TagHelper 绕过。
- WebForms 关注 `ValidateRequest=false`、`RequestValidationMode`、控件事件和 ViewState。
- ASP.NET Core CORS 关注 `AllowAnyOrigin` + credentials、动态 origin 反射。
- CSRF 关注 MVC/Core 表单、JSON API、SameSite=None、AntiforgeryToken 缺失。
- Host Header 关注 `Request.Url`、`Request.Host`、密码重置链接、OAuth redirect 构造。

## 输出要求

- 漏洞编号格式：`{C/H/M/L}-WEB-{序号}`。
- 每个业务授权问题必须给出两个主体或两个对象的验证思路，不只说“可能越权”。
- 默认 PoC 使用参数替换、状态差异或响应差异，不提供绕过生产风控的大规模枚举脚本。

## 自检

- 已区分浏览器侧漏洞、代理/部署漏洞、业务授权漏洞。
- 每个问题都关联具体路由和鉴权状态。
