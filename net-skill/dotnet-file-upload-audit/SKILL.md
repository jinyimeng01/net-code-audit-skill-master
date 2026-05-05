---
name: dotnet-file-upload-audit
version: 2.0.0
description: .NET 文件上传审计 skill。覆盖 HttpPostedFile、IFormFile、SaveAs、CopyToAsync、RadAsyncUpload、路径校验、扩展名校验、MIME 类型校验。追踪用户可控文件到存储路径，输出上传绕过证据和修复建议。
description_en: .NET file upload audit skill. Covers HttpPostedFile, IFormFile, SaveAs, CopyToAsync, RadAsyncUpload, path/extension/MIME validation. Traces user-controlled files to storage sinks.
author: net-code-audit-team
tags: ['dotnet', 'file-upload', 'rce', 'web-shell', 'mime-bypass']
compatibility: ['asp.net', 'asp.net-core', 'iis']
---

# .NET 文件上传漏洞审计工具

检查 .NET Web 项目源码或反编译结果，识别文件上传功能实现，检测文件上传安全漏洞。

## 核心要求

**此技能必须完整检查所有文件上传相关代码，不允许省略。**

- 必须识别所有文件上传入口点
- 必须检查每个上传点的文件类型校验
- 必须检测路径穿越和文件名注入
- 必须审计上传文件存储位置
- 禁止省略任何文件上传操作

---

## 漏洞分级标准

**详见 [SEVERITY_RATING.md](../shared/SEVERITY_RATING.md)**

- 漏洞编号格式: `{C/H/M/L}-UPLOAD-{序号}`

---

## 反编译支持（CRITICAL）

**当源码不可用时，必须使用 dnSpy.Console.exe 反编译。**

```bash
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r bin/
```

详见 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md)

---

## 文件上传方式识别

### ASP.NET (Framework)

| 方式 | 识别特征 | 危险点 |
|------|---------|--------|
| HttpPostedFile | `Request.Files[]`, `file.SaveAs()` | 文件名、类型、存储路径 |
| FileUpload 控件 | `<asp:FileUpload>`, `FileUpload.SaveAs()` | 同上 |
| Telerik/DevExpress | `RadAsyncUpload`, `ASPxUploadControl` | 第三方控件漏洞 |

### ASP.NET Core

| 方式 | 识别特征 | 危险点 |
|------|---------|--------|
| IFormFile | `IFormFile`, `CopyToAsync()` | 文件名、类型、存储路径 |
| IFormFileCollection | `Request.Form.Files` | 同上 |
| Request.Body | `Request.Body`, `StreamReader` | 无文件名校验 |

---

## 检测规则速查

### 文件类型校验

| 校验方式 | 安全性 | 说明 |
|----------|--------|------|
| 仅检查扩展名 | **不安全** | 可通过双扩展名绕过（`shell.aspx.jpg`） |
| 检查 Content-Type | **不安全** | 可伪造 |
| 检查文件头/Magic Bytes | **较安全** | 难伪造但可嵌入恶意代码 |
| 白名单校验 | **安全** | 仅允许已知安全类型 |
| 无校验 | **极危险** | 直接保存 |

### 路径穿越检测

| 危险模式 | 安全模式 |
|----------|----------|
| `Path.Combine(uploadDir, file.FileName)` | `Path.GetFileName(file.FileName)` 去除路径 |
| `Server.MapPath(input)` | 白名单路径 |
| 直接使用用户输入的路径 | 限制到安全目录 |

### 文件名注入检测

| 危险模式 | 安全模式 |
|----------|----------|
| 使用原始文件名 `file.FileName` | 生成随机文件名 `Guid.NewGuid().ToString()` |
| 未过滤特殊字符 | 过滤 `..`, `/`, `\`, 空字节 |

---

## 技能协作流程

**dotnet-file-upload-audit 应在 dotnet-route-mapper 之后执行。**

需要深度追踪时调用 dotnet-route-tracer。

---

## 输出格式

**严格按照 [references/OUTPUT_TEMPLATE.md](references/OUTPUT_TEMPLATE.md) 中的填充式模板生成输出文件。**

- 文件名格式: `{project_name}_file_upload_audit_{YYYYMMDD_HHMMSS}.md`
- 通用规范参考: [shared/DOTNET_OUTPUT_STANDARD.md](../shared/DOTNET_OUTPUT_STANDARD.md)

---

## 验证检查清单

- [ ] 所有文件上传入口已识别
- [ ] 每个上传点的文件类型校验已检查
- [ ] 路径穿越已检测
- [ ] 文件名注入已检测
- [ ] 上传文件存储位置安全性已评估
- [ ] 反编译来源已标注（如适用）
