---
name: dotnet-file-read-audit
version: 2.0.0
description: .NET 文件读取与路径穿越审计 skill。覆盖 File.ReadAllText、FileStream、StreamReader、Response.WriteFile、PhysicalFile、Server.MapPath、Path.Combine 等 sink。追踪用户可控输入到文件操作路径，输出路径穿越证据和修复建议。
description_en: .NET file read & path traversal audit skill. Covers File.ReadAllText, FileStream, StreamReader, Response.WriteFile, PhysicalFile, Server.MapPath, Path.Combine. Traces user input to file-operation sinks.
author: net-code-audit-team
tags: ['dotnet', 'file-read', 'path-traversal', 'lfi', 'information-disclosure']
compatibility: ['asp.net', 'asp.net-core', 'iis']
---

# .NET 任意文件读取漏洞审计工具

检查 .NET Web 项目源码或反编译结果，识别文件读取操作，检测路径穿越漏洞。

## 核心要求

**此技能必须完整检查所有文件读取相关代码，不允许省略。**

- 必须识别所有文件读取入口点
- 必须追踪文件路径参数来源
- 必须检测路径穿越漏洞
- 必须检查路径校验逻辑
- 禁止省略任何文件读取操作

---

## 漏洞分级标准

**详见 [SEVERITY_RATING.md](../shared/SEVERITY_RATING.md)**

- 漏洞编号格式: `{C/H/M/L}-FILE-{序号}`

---

## 反编译支持（CRITICAL）

**当源码不可用时，必须使用 dnSpy.Console.exe 反编译。**

```bash
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r bin/
```

详见 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md)

---

## 文件读取方法识别

### 常见文件读取 API

| 方法 | 命名空间 | 危险等级 |
|------|---------|---------|
| `File.ReadAllText(path)` | `System.IO` | 高 |
| `File.ReadAllBytes(path)` | `System.IO` | 高 |
| `File.ReadAllLines(path)` | `System.IO` | 高 |
| `File.OpenRead(path)` | `System.IO` | 高 |
| `new FileStream(path, ...)` | `System.IO` | 高 |
| `new StreamReader(path)` | `System.IO` | 高 |
| `Response.WriteFile(path)` | `System.Web` | 高 |
| `FileResult(path)` / `PhysicalFileResult(path)` | `Microsoft.AspNetCore.Mvc` | 高 |

### 路径穿越检测规则

| 危险模式 | 安全模式 |
|----------|----------|
| 直接使用用户输入路径 | 白名单目录限制 |
| `Path.Combine(baseDir, userInput)` | `Path.GetFullPath()` + 前缀校验 |
| 未过滤 `../` | 过滤 `..`, 空字节, URL 编码 |
| `Server.MapPath(input)` | 限制到应用目录内 |

### 路径校验绕过

| 绕过方式 | 示例 | 防御 |
|----------|------|------|
| `../` 穿越 | `../../etc/passwd` | 规范化后校验前缀 |
| URL 编码 | `%2e%2e%2f` | 解码后校验 |
| 双编码 | `%252e%252e%252f` | 多次解码 |
| 空字节截断 | `file.txt%00.exe` | 过滤空字节 |
| 大小写混合 | `..%5C` | 大小写不敏感处理 |

---

## 技能协作流程

**dotnet-file-read-audit 应在 dotnet-route-mapper 之后执行。**

需要深度追踪时调用 dotnet-route-tracer。

---

## 输出格式

**严格按照 [references/OUTPUT_TEMPLATE.md](references/OUTPUT_TEMPLATE.md) 中的填充式模板生成输出文件。**

- 文件名格式: `{project_name}_file_read_audit_{YYYYMMDD_HHMMSS}.md`
- 通用规范参考: [shared/DOTNET_OUTPUT_STANDARD.md](../shared/DOTNET_OUTPUT_STANDARD.md)

---

## 验证检查清单

- [ ] 所有文件读取入口已识别
- [ ] 文件路径参数来源已追踪
- [ ] 路径穿越漏洞已检测
- [ ] 路径校验逻辑已分析
- [ ] 反编译来源已标注（如适用）
