# quality_report.md 模板

# {项目名称} 最终 .NET 攻防代码审计报告

## 1. 审计概况

- 源码/发布包路径：{填写}
- 审计模式：{redteam-lab / defense-hardening / triage-only}
- 授权边界：{填写授权范围、测试账号、禁止范围}
- 框架识别：{ASP.NET Framework / WebForms / MVC / Web API / ASP.NET Core / WCF / Worker / 混合}
- 反编译范围：{源码 / decompiled 路径 / 失败程序集}
- 原始资料追溯：{是否引用 raw 归档；列出引用的 raw index 路径}

## 2. 攻击面总览

| 分类 | 数量 | 最高等级 | 推荐专项 | 代表证据 |
|:-----|----:|:---------|:---------|:---------|
| route/auth | {填写} | {填写} | dotnet-route-mapper / dotnet-auth-audit | {文件:行号} |
| sql | {填写} | {填写} | dotnet-sql-audit | {文件:行号} |
| xxe | {填写} | {填写} | dotnet-xxe-audit | {文件:行号} |
| file-upload | {填写} | {填写} | dotnet-file-upload-audit | {文件:行号} |
| file-read | {填写} | {填写} | dotnet-file-read-audit | {文件:行号} |
| deserialization | {填写} | {填写} | dotnet-deserialization-audit | {文件:行号} |
| command-exec | {填写} | {填写} | dotnet-command-exec-audit | {文件:行号} |
| ssrf | {填写} | {填写} | dotnet-ssrf-audit | {文件:行号} |
| config-secret | {填写} | {填写} | dotnet-config-secrets-audit | {脱敏文件:行号} |
| web-risk | {填写} | {填写} | dotnet-web-risk-audit | {文件:行号} |

## 3. 路由、鉴权与优先级

| 优先级 | 路由/入口 | 方法/协议 | 鉴权状态 | 参数来源 | 推荐专项 | 追踪状态 |
|:-------|:----------|:----------|:---------|:---------|:---------|:---------|
| P0 | {填写} | {填写} | {填写} | {填写} | {填写} | {已追踪/未追踪原因} |

要求：全量列出 P0/P1；P2 如未全量追踪，必须写明抽样策略和残余风险。

## 4. 漏洞详情

### {编号} {标题}

- 等级：{Critical/High/Medium/Low/Info}
- 分类：{sql/xxe/file-upload/file-read/deserialization/command-exec/ssrf/config-secret/web-risk/auth/component}
- 证据标签：{confirmed/reachable/static-only/config-only/dependency-only/needs-runtime}
- 入口：{路由、WCF 方法、队列、计划任务、文件导入点或配置文件}
- 鉴权状态：{无鉴权/有鉴权/可绕过/内部入口/未知}
- 调用链：{入口 -> 方法 -> sink，含文件:行号}
- Sink：{API、formatter、命令执行点、URL 请求点、配置项}
- 代码证据：{最小必要片段，避免泄露完整密钥}
- 可利用前置条件：{输入控制、配置、组件版本、网络、权限、运行身份}
- 无害验证：{响应差异、错误回显、日志、DNS/HTTP callback、只读确认或说明无法安全验证}
- 授权实验室验证建议：{隔离环境、测试账号、测试数据、回滚方式；不写可直接用于未授权目标的投递包}
- 影响：{数据、身份、执行上下文、内网访问、业务影响}
- 修复建议：{代码修复、配置修复、依赖升级、密钥轮换、监控}
- 复测方法：{无害复测步骤}

## 5. 反序列化专题覆盖

| Formatter/机制 | 是否出现 | 证据 | 类型控制点 | 修复建议 |
|:---------------|:---------|:-----|:-----------|:---------|
| XmlSerializer | {是/否} | {文件:行号} | {填写} | {填写} |
| Json.NET TypeNameHandling | {是/否} | {文件:行号} | {填写} | {填写} |
| Fastjson/.NET 变体 | {是/否} | {文件:行号} | {填写} | {填写} |
| JavaScriptSerializer | {是/否} | {文件:行号} | {填写} | {填写} |
| .NET Remoting | {是/否} | {文件:行号} | {填写} | {填写} |
| DataContractSerializer | {是/否} | {文件:行号} | {填写} | {填写} |
| NetDataContractSerializer | {是/否} | {文件:行号} | {填写} | {填写} |
| SoapFormatter | {是/否} | {文件:行号} | {填写} | {填写} |
| BinaryFormatter | {是/否} | {文件:行号} | {填写} | {填写} |
| ObjectStateFormatter | {是/否} | {文件:行号} | {填写} | {填写} |
| LosFormatter/ViewState | {是/否} | {文件:行号} | {machineKey/ViewStateUserKey/MAC} | {填写} |

## 6. 配置、密钥与部署暴露

| 类型 | 证据 | 脱敏状态 | 影响 | 处置 |
|:-----|:-----|:---------|:-----|:-----|
| machineKey | {脱敏文件:行号} | {已脱敏} | ViewState/FormsAuth 影响 | 轮换并统一配置 |
| connectionStrings | {脱敏文件:行号} | {已脱敏} | 数据库访问 | 轮换、最小权限 |
| JWT/OAuth/SAML secret | {脱敏文件:行号} | {已脱敏} | token/SSO 身份边界 | 轮换、受众/签名校验 |
| Swagger/ELMAH/Hangfire/debug | {文件:行号} | {不适用} | 管理/调试面暴露 | 鉴权、关闭生产暴露 |

## 7. 链路放大与组合风险

| 链路 | 上游入口 | 中间条件 | 下游 sink | 综合影响 | 建议 |
|:-----|:---------|:---------|:----------|:---------|:-----|
| 上传 -> XML/反序列化 | {填写} | {填写} | {填写} | {填写} | {填写} |
| SSRF -> metadata/内网服务 | {填写} | {redirect/DNS/header/proxy} | {填写} | {填写} | {填写} |
| 密钥泄露 -> 身份伪造风险 | {填写} | {machineKey/token/SSO} | {填写} | {填写} | {填写} |

## 8. 修复优先级

| 优先级 | 问题 | 责任模块 | 建议完成时间 | 验收标准 |
|:-------|:-----|:---------|:-------------|:---------|
| P0 | {填写} | {填写} | {填写} | {无害复测通过} |

## 9. 质量与覆盖率

| 校验项 | 实际值 | 阈值 | 状态 |
|:-------|:-------|:-----|:-----|
| 路由覆盖率 | {填写}% | 80% | {通过/不通过} |
| 高危路由追踪率 | {填写}% | 90% | {通过/不通过} |
| 漏洞审计覆盖率 | {填写}% | 90% | {通过/不通过} |
| surface_index 字段完整性 | {填写}% | 100% | {通过/不通过} |
| raw 来源头完整性 | {填写}% | 100% | {通过/不通过} |
| 密钥脱敏检查 | {通过/不通过} | 必须通过 | {通过/不通过} |
| 安全输出检查 | {通过/不通过} | 必须通过 | {通过/不通过} |

## 10. 审计结论

- 确认漏洞：{填写数量和最高风险}
- 潜在风险：{填写数量和需运行时确认项}
- 未发现项：{按专项列出}
- 无法判断项：{说明缺少源码、运行环境、配置或权限}
- 后续建议：{修复、复测、监控、密钥轮换、依赖升级}
