# .NET 配置密钥检查清单

## 文件范围

- `web.config`, `app.config`, `machine.config`
- `appsettings.json`, `appsettings.*.json`, `secrets.json`
- `launchSettings.json`, `*.pubxml`, `*.publishsettings`
- `applicationHost.config`, IIS rewrite/module config
- `.deps.json`, `.runtimeconfig.json`, 发布包残留
- 日志、备份、`.bak`, `.old`, `.config~`, `.zip`, `.7z`

## 高价值项

| 项 | 影响 |
|---|---|
| `machineKey` | ViewState、FormsAuth、反序列化链放大 |
| `connectionStrings` | 数据库访问和横向影响 |
| JWT signing key | token 伪造或权限提升 |
| OAuth/OIDC client secret | 第三方登录绑定/回调风险 |
| SAML certificate/private key | SSO assertion 风险 |
| SMTP/FTP/S3/Azure/AWS secret | 外部资源访问 |
| `debug=true` / `customErrors=Off` | 信息泄露 |
| ELMAH/Swagger/Hangfire dashboard | 管理面暴露 |

## 审计步骤

1. 先定位配置源：文件、环境变量、KeyVault、K8s Secret、IIS app settings。
2. 判断是否为生产配置，不把本地开发样例直接定高危。
3. 关联使用点：密钥是否仍被认证、签名、数据库、云 SDK 使用。
4. 检查泄露路径：文件下载、路径穿越、备份包、源码仓库、日志、异常页面。
5. 报告中脱敏展示，不粘贴完整密钥。

## 脱敏规则

- 报告只展示 `abcd****wxyz`、哈希或配置项名。
- 不复制完整生产密钥、连接串、token。
- 修复建议必须包含轮换、权限最小化、配置源迁移和日志清理。
