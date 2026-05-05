# ViewState 与 machineKey 审计

## 相关机制

| 项 | 作用 |
|---|---|
| `__VIEWSTATE` | WebForms 页面状态，底层涉及 LosFormatter/ObjectStateFormatter |
| `__EVENTVALIDATION` | 事件参数校验 |
| `enableViewStateMac` | ViewState 完整性保护 |
| `ViewStateUserKey` | 将 ViewState 绑定到用户/会话，降低重放 |
| `machineKey` | FormsAuth、ViewState、反序列化链放大的关键密钥 |

## 高危配置

```xml
<pages enableViewStateMac="false" />
<pages viewStateEncryptionMode="Never" />
<machineKey validationKey="..." decryptionKey="..." />
```

## 审计步骤

1. 在 `web.config`、`machine.config`、发布包、备份文件中定位 `machineKey`。
2. 检查 `enableViewStateMac`、`viewStateEncryptionMode`、`enableEventValidation`。
3. 检查页面或基类是否设置 `Page.ViewStateUserKey`。
4. 检查是否有自定义 `LosFormatter.Deserialize` 或 `ObjectStateFormatter.Deserialize`。
5. 结合文件读取、配置泄露、备份文件下载判断 machineKey 是否可能泄露。

## 影响关联

- machineKey 泄露 + WebForms ViewState：可能伪造页面状态，风险取决于 .NET 版本、页面控件、gadget 可用性。
- machineKey 泄露 + FormsAuth：可能伪造认证票据。
- machineKey 弱随机或复用：多站点横向影响。

## 安全验证

- 默认不在报告中生成可投递 ViewState payload。
- 可验证配置状态、密钥泄露路径、MAC 是否启用、是否绑定用户。
- 授权实验室中可使用无害命令或固定回显证明链路，不对生产系统执行。

## 修复

- 开启 `enableViewStateMac` 和 `enableEventValidation`。
- 使用强随机 `machineKey`，泄露后立即轮换。
- 敏感页面设置 `ViewStateUserKey`。
- 禁止下载 `web.config`、备份文件、发布配置。
- 移除显式 `LosFormatter/ObjectStateFormatter` 外部输入反序列化。
