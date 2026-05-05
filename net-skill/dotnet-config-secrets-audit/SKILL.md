---
name: dotnet-config-secrets-audit
version: 2.0.0
description: .NET 配置密钥与部署暴露审计 skill。覆盖 machineKey、connectionStrings、JWT/OAuth/SAML secret、证书私钥、IIS 配置暴露、Swagger UI、ELMAH、Hangfire、Debug 模式。输出密钥影响分析、脱敏展示和轮换建议。
description_en: .NET configuration secrets & deployment exposure audit skill. Covers machineKey, connectionStrings, JWT/OAuth/SAML secrets, certificate private keys, IIS misconfigurations, Swagger UI, ELMAH, Hangfire, Debug mode.
author: net-code-audit-team
tags: ['dotnet', 'secrets', 'machinekey', 'jwt', 'config', 'exposure']
compatibility: ['asp.net', 'asp.net-core', 'iis']
---

# .NET 配置与密钥审计

查找能放大漏洞影响的配置、密钥和部署暴露。详细清单参考 [CONFIG_SECRETS_CHECKLIST.md](references/CONFIG_SECRETS_CHECKLIST.md)，认证影响参考 [MACHINEKEY_TOKEN_IMPACT.md](references/MACHINEKEY_TOKEN_IMPACT.md)，IIS/发布暴露参考 [DEPLOYMENT_EXPOSURE.md](references/DEPLOYMENT_EXPOSURE.md)。

## 工作流

1. 枚举配置文件：`web.config`、`app.config`、`appsettings*.json`、`*.pubxml`、`launchSettings.json`、IIS `applicationHost.config`、Docker/Kubernetes secret 引用。
2. 搜索敏感项：`machineKey`、`connectionStrings`、`Jwt:Key`、`ClientSecret`、`SigningKey`、`Certificate`、`Password`、`AccessKey`。
3. 检查危险开关：`debug=true`、`customErrors=Off`、`trace enabled`、Swagger/ELMAH/Hangfire dashboard 生产暴露。
4. 关联影响：machineKey -> ViewState/FormsAuth；JWT key -> token forgery；连接串 -> 数据库读写；SAML cert -> SSO 绕过。
5. 输出泄露路径、权限边界、轮换建议和最小权限建议。
6. 对 dashboard、Swagger、ELMAH、备份包、IIS handler/module 暴露读取部署专题。

## 输出要求

- 漏洞编号格式：`{C/H/M/L}-CONF-{序号}`。
- 不在报告中完整粘贴真实密钥；只展示前后 4 位、哈希或占位说明。
- 必须说明密钥用途、可达泄露路径、是否仍在使用、修复/轮换步骤。
- 对 `machineKey` 必须关联 ViewState MAC、Forms Authentication、反序列化风险。

## 自检

- 没有把测试样例密钥误判为生产密钥而不说明上下文。
- 每个泄露项都有“可利用影响”或“仅配置卫生问题”的结论。
