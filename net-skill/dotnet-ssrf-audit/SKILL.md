---
name: dotnet-ssrf-audit
version: 2.0.0
description: .NET SSRF 与出站请求审计 skill。覆盖 HttpClient、WebRequest、WebClient、AllowAutoRedirect、Uri/Dns/IPAddress 解析差异、metadata 端点、代理头 X-Original-URL / X-Rewrite-URL、导入远程资源链。追踪用户可控输入到出站请求 sink，输出 SSRF 证据和修复建议。
description_en: .NET SSRF & outbound request audit skill. Covers HttpClient, WebRequest, WebClient, AllowAutoRedirect, URI/DNS/IPAddress parsing differences, metadata endpoints, proxy headers (X-Original-URL, X-Rewrite-URL), and remote import chains.
author: net-code-audit-team
tags: ['dotnet', 'ssrf', 'outbound-request', 'dns-rebinding', 'url-parser']
compatibility: ['asp.net', 'asp.net-core', 'wcf', 'iis']
---

# .NET SSRF 审计

检查外部输入是否影响服务端出站请求目标。基础模式参考 [SSRF_PATTERNS.md](references/SSRF_PATTERNS.md)，URL 绕过和重定向参考 [URL_PARSER_AND_REDIRECTS.md](references/URL_PARSER_AND_REDIRECTS.md)，导入链和 metadata 风险参考 [IMPORT_AND_METADATA_CHAINS.md](references/IMPORT_AND_METADATA_CHAINS.md)。

## 工作流

1. 搜索出站请求 sink：`HttpClient`、`WebClient`、`WebRequest.Create`、`HttpWebRequest`、`DownloadString`、`DownloadFile`、`GetAsync`、`PostAsync`、`GrpcChannel.ForAddress`。
2. 识别输入来源：URL 参数、webhook 配置、头像/图片抓取、导入远程 XML/SVG/Office、PDF 生成、SAML/OIDC metadata、WCF endpoint 配置。
3. 分析 URL 解析和校验顺序：decode、normalize、DNS resolve、重定向、代理、IPv6、userinfo、IDN/punycode、短地址。
4. 判断影响：内网探测、云元数据、敏感服务访问、响应回显、盲 SSRF callback、二次文件写入。
5. 调用 route tracer 证明入口到出站 sink 可达。
6. 对 webhook、导入、预览、metadata 类场景分别读取专题 reference。

## 危险特征

- 白名单校验在 URL decode 或重定向前执行。
- 允许 `http://127.0.0.1`、`localhost`、私有网段、link-local、IPv6 等价地址。
- `AllowAutoRedirect=true` 且不重新校验 Location。
- 只检查字符串前缀或后缀，不使用 `Uri` 解析和主机/IP 归一化。
- 代理信任 `X-Forwarded-*` 或配置可被用户影响。

## 输出要求

- 漏洞编号格式：`{C/H/M/L}-SSRF-{序号}`。
- 必须记录 URL 参数来源、校验逻辑、DNS/重定向处理、是否回显响应、出网限制。
- 默认验证使用授权 callback 域名或本地 mock 地址，不提供攻击真实云元数据的默认请求。
- 修复建议包含：固定目的地、allowlist after resolve、禁止私网/metadata、关闭或重校验重定向、出网 ACL。

## 自检

- 已区分直接 SSRF、盲 SSRF、重定向 SSRF、XXE-to-SSRF、文件导入-to-SSRF。
