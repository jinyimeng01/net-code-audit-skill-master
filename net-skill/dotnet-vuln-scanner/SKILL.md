---
name: dotnet-vuln-scanner
version: 2.0.0
description: .NET 组件漏洞扫描 skill。覆盖 NuGet 包、DLL 引用、配置文件中的依赖版本与 CVE/GHSA 触发条件。输出组件漏洞清单、可利用性评估和修复版本建议。
description_en: .NET component vulnerability scanner. Covers NuGet packages, DLL references, dependency versions in config files, and CVE/GHSA trigger conditions. Outputs component vulnerability inventory, exploitability assessment, and remediation versions.
author: net-code-audit-team
tags: ['dotnet', 'dependency', 'cve', 'nuget', 'vulnerability-scanning']
compatibility: ['asp.net', 'asp.net-core', 'wcf', 'iis']
---

# .NET 组件漏洞扫描器

扫描 .NET 项目依赖中的已知漏洞，按模块分组输出，并由 AI 生成漏洞触发点检查结果。

## 工作流程

### 1. 确定扫描目标

支持的输入类型：
- `packages.config` - NuGet 包配置（.NET Framework）
- `*.csproj` - 项目文件（含 PackageReference）
- `*.dll` / `*.exe` - 从程序集元数据提取依赖信息
- 目录 - 递归扫描上述所有文件，自动按模块分组

### 2. 处理 DLL/EXE 文件（需要反编译时）

当目标是编译后的程序集且无法直接提取依赖信息时，使用 dnSpy.Console.exe 反编译：

```bash
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r bin/
```

详见 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md)

### 3. 执行漏洞扫描

运行扫描脚本，报告自动保存到 `{项目名}_audit/vuln_report/` 目录：

```bash
python3 scripts/scan_dotnet_dependencies.py <目标路径> \
  --rules references/dotnet-vulnerability.yaml \
  --no-deps
```

参数说明：
- `<目标路径>`: packages.config、csproj、dll 文件或目录
- `--rules/-r`: 漏洞规则文件路径（使用内置规则）
- `--format/-f`: 输出格式 (markdown/json)
- `--output/-o`: 指定输出路径（不指定则自动生成）
- `--depth/-d`: 模块分组深度（默认: 2）
- `--no-deps`: 不显示依赖列表（简化输出）
- `--no-save`: 仅输出到终端，不保存文件

### 4. AI 漏洞触发点分析（重要）

扫描完成后，**必须**基于扫描结果，按照 `references/OUTPUT_TEMPLATE.md` 模板填充完整报告。

#### 分析步骤

1. 读取 Python 脚本生成的扫描结果
2. **识别项目运行环境**：
   - 检查项目使用的框架：ASP.NET WebForms / ASP.NET MVC / ASP.NET Web API / ASP.NET Core
   - 检查服务器类型：IIS / Kestrel / HTTP.sys
   - 查找配置文件：`web.config`、`app.config`、`appsettings.json`、`Program.cs`
3. **提取路由和入口点**：
   - 结合 dotnet-route-mapper 技能获取完整路由信息
4. 提取检测到的**唯一漏洞组件**列表（去重）
5. **按模板填充报告**

---

## 漏洞规则覆盖

规则文件 `references/dotnet-vulnerability.yaml` 包含规则，覆盖：

| 组件类别 | 主要漏洞 |
|---------|---------|
| Newtonsoft.Json | 反序列化 RCE |
| Log4net | CVE-2018-1285 等 |
| NLog | 配置注入等 |
| Bouncy Castle | 加密实现缺陷 |
| System.Text.Json | 拒绝服务 |
| IdentityModel / IdentityServer | Token 验证绕过 |
| Elmah | 日志文件泄露 |
| DotNetNuke | 多个 RCE |
| Orchard Core | 权限绕过 |
| Telerik UI | 远程代码执行 |

---

## 输出格式

**严格按照 [references/OUTPUT_TEMPLATE.md](references/OUTPUT_TEMPLATE.md) 中的填充式模板生成输出文件。**

- 文件名格式: `{project_name}_vuln_report_{YYYYMMDD_HHMMSS}.md`
- 输出为单个文件
- 通用规范参考: [shared/DOTNET_OUTPUT_STANDARD.md](../shared/DOTNET_OUTPUT_STANDARD.md)
