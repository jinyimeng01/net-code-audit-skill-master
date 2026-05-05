# 部署暴露与 IIS 风险

## 常见暴露

- Swagger/OpenAPI 在生产无鉴权。
- ELMAH、Glimpse、MiniProfiler、Hangfire dashboard 暴露。
- `trace.axd`、错误详情、`customErrors=Off`。
- 目录浏览、备份包、发布配置、源码压缩包。
- IIS handler/module 映射导致静态下载 `.config`、`.cs`、`.bak`。

## IIS / ASP.NET 特性

| 项 | 审计点 |
|---|---|
| requestFiltering | 是否阻止危险扩展、双扩展、隐藏段 |
| handlers | 是否存在过宽 wildcard handler |
| modules | 自定义鉴权/重写模块顺序 |
| URL Rewrite | 是否可绕过鉴权路径判断 |
| X-Original-URL / X-Rewrite-URL | IIS/代理重写绕过 |
| 短文件名枚举 | 是否启用 8.3 short names |

## 输出要求

- 说明暴露路径和访问鉴权。
- 说明泄露内容的实际影响。
- 对 dashboard 类风险给出访问控制和生产禁用建议。
