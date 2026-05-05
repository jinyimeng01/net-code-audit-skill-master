---
name: dotnet-audit-pipeline
version: 2.0.0
description: .NET Web 全链路攻防代码审计流水线。使用 agent team 编排多个审计 skill，自动完成 dnSpy 全量反编译、攻击面索引、路由提取、鉴权审计、组件漏洞、高危路由分级、调用链追踪、SQL/XXE/文件/反序列化/命令执行/SSRF/配置密钥/Web 风险专项检测、质量校验和唯一最终报告 quality_report.md。适用于授权源码审计、红队实验室验证、防守加固复核、只有 bin/DLL 的 .NET 项目。
description_en: .NET full-stack offensive security audit pipeline. Orchestrates agent teams for decompilation, surface indexing, route/auth/vulnerability scanning, call-chain tracing, and specialized deep audits (SQL, XXE, file, deserialization, command exec, SSRF, secrets, web risks), producing a unified quality_report.md.
author: net-code-audit-team
tags: ['dotnet', 'pipeline', 'security', 'audit', 'agent-team']
compatibility: ['asp.net', 'asp.net-core', 'wcf', 'iis']
---

# .NET 全链路攻防审计流水线

本流水线是 [dotnet-offsec-audit](../dotnet-offsec-audit/SKILL.md) 的执行编排层。默认在授权环境中运行，危险利用链必须遵守 [REDTEAM_LAB_BOUNDARY.md](../shared/REDTEAM_LAB_BOUNDARY.md)。

## 输入

- `source_path`: 源码、发布目录或 bin 目录。
- `output_path`: 默认 `{source_path}_audit`。
- `mode`: `redteam-lab` / `defense-hardening` / `triage-only`。
- `dnspy_path`: 可选。

## 阶段总览

```text
阶段0: 授权边界与 dnSpy 全量反编译
  -> 验证 decompiled/ 中存在 .cs 或记录失败原因

阶段1: 攻击面索引与基础画像
  -> dotnet-offsec-audit/scripts/collect_dotnet_surface.py
  -> surface/surface_index.json + surface/attack_surface_matrix.md

阶段2: 基础审计并行
  -> dotnet-route-mapper: 全量路由和参数
  -> dotnet-auth-audit: 鉴权框架和路由鉴权映射
  -> dotnet-vuln-scanner: NuGet/DLL 组件漏洞

阶段3: 交叉筛选与优先级
  -> 未鉴权/弱鉴权路由
  -> 高危 sink 路由
  -> 组件漏洞触发入口
  -> 配置密钥放大链

阶段4: 调用链追踪
  -> dotnet-route-tracer 分批追踪入口到 sink

阶段5: 专项深度审计
  -> SQL / XXE / 文件读取 / 文件上传
  -> 反序列化 / 命令执行 / SSRF / 配置密钥 / Web 风险

阶段6: 质量校验与唯一最终报告
  -> quality_report.md
```

## 阶段0：反编译强约束

当存在 `.dll/.exe` 或源码不完整时，按 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md) 先反编译。

```bash
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r {bin_or_target_dir}
```

验证要求：

- 成功：`decompiled/` 中存在 `.cs` 文件。
- 部分失败：记录失败 DLL，继续审计已反编译与源码部分。
- 工具缺失：报告阻塞项，不得伪造反编译结论。

## 阶段1：攻击面索引

```bash
python dotnet-offsec-audit/scripts/collect_dotnet_surface.py {source_path} -o {output_path}/surface
```

输出：

- `surface_index.json`: 机器可读的 sink 和证据索引。
- `attack_surface_matrix.md`: 人工复核矩阵。
- 每条 finding 必须包含 `recommended_skill`、`confidence`、`evidence_kind`，并兼容旧字段 `category/rule_id/severity_hint/file/line/snippet`。

用 [DOTNET_ATTACK_SURFACE_TAXONOMY.md](../shared/DOTNET_ATTACK_SURFACE_TAXONOMY.md) 映射后续专项。

## 阶段2：基础审计并行

| Agent | Skill | 输出 |
|---|---|---|
| agent-1-route-mapper | [dotnet-route-mapper](../dotnet-route-mapper/SKILL.md) | 全量路由、参数、Burp 模板 |
| agent-2-auth-audit | [dotnet-auth-audit](../dotnet-auth-audit/SKILL.md) | 鉴权框架、路由鉴权状态、越权线索 |
| agent-3-vuln-scanner | [dotnet-vuln-scanner](../dotnet-vuln-scanner/SKILL.md) | 组件漏洞和触发条件 |

全部基础输出必须可互相引用：路由 ID、入口方法、文件位置、鉴权状态保持一致。

## 阶段3：交叉筛选

建立 `priority_targets.md`：

| 优先级 | 条件 |
|---|---|
| P0 | 未鉴权入口 + RCE/反序列化/命令执行/file-write/machineKey |
| P1 | 未鉴权入口 + SQL/XXE/SSRF/文件读取/敏感配置 |
| P2 | 认证入口 + 越权/IDOR/业务状态绕过/组件触发 |
| P3 | 仅内部可达或证据不足的潜在风险 |

## 阶段4：调用链追踪

对 P0/P1 全量追踪，对 P2 按代表性和业务影响追踪。每条链必须记录：

- HTTP/WCF/队列/文件入口。
- 参数名变化。
- 过滤、转换、拼接、反序列化、URL 解析、路径规范化。
- 最终 sink 与执行条件。
- 鉴权状态和证据标签。

## 阶段5：专项深度审计

| Agent | Skill | 触发条件 |
|---|---|---|
| agent-6a-sql | [dotnet-sql-audit](../dotnet-sql-audit/SKILL.md) | `SqlCommand`, `FromSqlRaw`, Dapper, HQL, 动态 SQL |
| agent-6b-xxe | [dotnet-xxe-audit](../dotnet-xxe-audit/SKILL.md) | `XmlDocument`, `XmlReader`, SOAP, OOXML/SVG, XSLT |
| agent-6c-upload | [dotnet-file-upload-audit](../dotnet-file-upload-audit/SKILL.md) | `HttpPostedFile`, `IFormFile`, `SaveAs`, `CopyToAsync` |
| agent-6d-fileread | [dotnet-file-read-audit](../dotnet-file-read-audit/SKILL.md) | `File.ReadAllText`, `FileStream`, `Response.WriteFile`, `PhysicalFile` |
| agent-6e-deser | [dotnet-deserialization-audit](../dotnet-deserialization-audit/SKILL.md) | `BinaryFormatter`, `TypeNameHandling`, `LosFormatter`, Remoting, `ReadObject` |
| agent-6f-cmd | [dotnet-command-exec-audit](../dotnet-command-exec-audit/SKILL.md) | `Process.Start`, PowerShell, CodeDom/Roslyn, XAML, `Assembly.Load` |
| agent-6g-ssrf | [dotnet-ssrf-audit](../dotnet-ssrf-audit/SKILL.md) | `HttpClient`, `WebRequest`, webhook, remote import, metadata |
| agent-6h-config | [dotnet-config-secrets-audit](../dotnet-config-secrets-audit/SKILL.md) | `machineKey`, connectionStrings, JWT/OAuth/SAML secret, debug/ELMAH/Swagger |
| agent-6i-web | [dotnet-web-risk-audit](../dotnet-web-risk-audit/SKILL.md) | XSS, CSRF, CORS, Open Redirect, Host Header, IDOR/BOLA/BFLA |

专项输出统一放入 `{output_path}/specialized/{category}/`，最终只汇总为 `quality_report.md`。

## 阶段6：最终报告

最终交付文件只有 `{output_path}/quality_report.md`，结构参考 [REPORT_TEMPLATE.md](../dotnet-offsec-audit/references/REPORT_TEMPLATE.md) 和 [DOTNET_OUTPUT_STANDARD.md](../shared/DOTNET_OUTPUT_STANDARD.md)。

强制要求：

- 每个确认漏洞都有入口、调用链、sink、代码证据、证据标签、风险等级、修复建议。
- 每个高危问题都有无害验证或说明为何无法安全验证。
- 反编译结果必须标注来源 DLL。
- 不保留【填写】、`TODO`、`...` 或省略式输出。
- 不在最终报告中泄露完整密钥、token、连接串。

## 质量门

- `surface_index.json` 覆盖新增 9 大专项分类。
- `surface_index.json` 字段完整，Critical/High 命中均被 agent-4b 汇入 `specialized_surface_targets.md`。
- route/auth/component 三类基础报告已完成。
- P0/P1 目标追踪覆盖率为 100%。
- P2 目标有明确抽样策略和未覆盖风险说明。
- 最终报告风险等级符合 [SEVERITY_RATING.md](../shared/SEVERITY_RATING.md)。
