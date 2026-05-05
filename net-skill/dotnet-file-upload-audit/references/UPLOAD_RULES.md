# .NET 文件上传审计规则速查

## 一、上传实现识别

### 1) ASP.NET Core IFormFile

**典型代码特征：**
- `IFormFile file` 参数绑定
- `file.FileName` 作为文件名
- `file.CopyTo(stream)` 或 `file.CopyToAsync(stream)` 写入文件
- 固定上传目录 `Path.Combine(_env.WebRootPath, "uploads")`

**注意要点：**
- `IFormFile` 会校验 Content-Type 为 multipart/form-data
- 示例未见文件名净化、类型白名单或目录隔离
- `file.FileName` 包含客户端原始文件名，可能含路径信息

### 2) ASP.NET HttpPostedFileBase

**典型代码特征：**
- `HttpPostedFileBase file` 参数
- `file.FileName` 作为文件名
- `file.SaveAs(savePath)` 写入文件
- `Server.MapPath("~/uploads")` 作为保存目录

**注意要点：**
- `file.FileName` 在不同浏览器中行为不同（IE 含完整路径，Chrome 仅文件名）
- 示例未见文件名净化、类型白名单或目录隔离

### 3) ASP.NET WebForms FileUpload

**典型代码特征：**
- `<asp:FileUpload ID="FileUpload1" runat="server" />`
- `FileUpload1.HasFile` 检查
- `FileUpload1.FileName` 获取文件名
- `FileUpload1.SaveAs(savePath)` 保存文件
- `Server.MapPath("~/uploads")` 作为保存目录

**注意要点：**
- WebForms FileUpload 控件不校验文件类型
- 示例未见文件名净化、类型白名单或目录隔离

### 4) ASP.NET Core IFormFileCollection

**典型代码特征：**
- `IFormFileCollection files` 或 `Request.Form.Files`
- 多文件上传循环处理
- `file.FileName` + `file.CopyTo()` 模式

---

## 二、常见高危模式

| 模式 | 代码特征 | 风险 |
|:-----|:---------|:-----|
| 原始文件名直写 | `file.FileName` / `Path.GetFileName(file.FileName)` | 文件名可控、路径穿越 |
| Web 根目录写入 | `wwwroot/uploads/` / `Server.MapPath("~/uploads")` | 可执行文件上传 |
| 无类型校验 | 无扩展名或 Content-Type 白名单 | 任意文件上传 |
| 无路径规范化 | 直接拼接 `Path.Combine(dir, fileName)` | 路径穿越/文件覆盖 |
| 无重命名 | 不生成随机名 | 文件覆盖/可预测路径 |
| Content-Type 仅信任 | `file.ContentType` 白名单 | 可伪造 Content-Type |

---

## 三、要求的安全校验点

| 校验点 | 建议 |
|:-------|:-----|
| 文件名 | `Path.GetFileName()` 去除路径 + 生成随机名 |
| 目录限制 | 固定基础目录 + `Path.GetFullPath()` 校验 |
| 类型校验 | 扩展名白名单 + 文件魔数校验 |
| 上传目录 | 非 Web 根目录，或配置静态文件中间件限制执行 |
| 重命名 | 使用 `Guid.NewGuid()` 或哈希名 |
| 大小限制 | `requestLimits maxAllowedContentLength` + `[RequestSizeLimit]` |

---

## 四、.NET 特有注意事项

### 1. IIS 执行权限

- 确保上传目录没有执行权限（不在 `handlerMapping` 中配置脚本映射）
- ASP.NET Core: 确保 `UseStaticFiles` 不配置上传目录的可执行 MIME 类型

### 2. web.config 上传限制

```xml
<system.web>
    <httpRuntime maxRequestLength="4096" /> <!-- KB -->
</system.web>
<system.webServer>
    <security>
        <requestFiltering>
            <requestLimits maxAllowedContentLength="4194304" /> <!-- Bytes -->
        </requestLimits>
    </security>
</system.webServer>
```

### 3. ASP.NET Core 请求大小限制

```csharp
[RequestSizeLimit(5 * 1024 * 1024)]  // 5MB
[RequestFormLimits(MultipartBodyLengthLimit = 5 * 1024 * 1024)]
public IActionResult Upload(IFormFile file)
```

### 4. 文件名安全处理

```csharp
// 危险：直接使用客户端文件名
string fileName = file.FileName;

// 安全：去除路径 + 生成随机名
string extension = Path.GetExtension(file.FileName);
string fileName = Guid.NewGuid().ToString() + extension;
```

---

## 五、快速检查项

- 是否使用 `file.FileName` 作为最终文件名？
- 上传目录是否在 Web 可访问路径下？
- 是否缺少扩展名/Content-Type 白名单？
- 是否存在路径规范化与目录限制？
- 是否存在文件覆盖风险（固定文件名/不重命名）？
- 是否校验文件魔数（而非仅信任 Content-Type）？
