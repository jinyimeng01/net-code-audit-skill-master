# 导入链与 Metadata 风险

## 非显眼 SSRF 入口

- SVG/OOXML/PDF/HTML 导入和预览。
- XML/SOAP 外部实体。
- SAML/OIDC metadata URL。
- webhook 测试按钮。
- 图片抓取、头像同步、URL preview。
- RSS/Atom feed。
- WCF endpoint 或动态 service URL。

## 链式风险

| 链 | 影响 |
|---|---|
| SSRF -> metadata | 云凭据、实例身份、临时 token |
| SSRF -> 内网管理面 | Redis、Solr、Elasticsearch、Jenkins、IIS admin |
| SSRF -> 文件保存 | 下载恶意内容到可访问目录 |
| SSRF -> XXE/XML parser | 二次解析造成文件读取或内网探测 |
| Open Redirect -> SSRF | 第一跳可信，后续跳到内网 |

## .NET 检查点

- `HttpClient` 是否复用全局 handler。
- `MaxResponseContentBufferSize`、流式下载、保存路径。
- 代理是否允许访问内网。
- 是否记录完整 URL 到日志造成敏感信息泄露。
- 是否将响应传给 `XmlDocument.LoadXml`、`JsonConvert.DeserializeObject`、模板引擎。
