# .NET 代码审计统一反编译策略指南

所有 .NET 审计 Skill 共享此反编译策略，使用 dnSpy.Console.exe 反编译 .NET 程序集。

---

## 0. 前置强约束：dnSpy 全量反编译必须优先完成

> **以下为本策略的最高优先级规则，任何审计流程启动前都必须遵守。违反此规则视为输出不合格。**

### 0.1 执行顺序（强制）

**所有 .NET 代码审计流程中，必须先执行 dnSpy.Console.exe 全量反编译所有 DLL，确认反编译完成后才能开始任何代码审计步骤。**

执行流程：

1. 定位 dnSpy.Console.exe 路径
2. 定位待反编译的 bin 目录
3. 执行全量反编译
4. **验证反编译结果**：确认输出目录中存在 .cs 文件
5. 只有第 4 步验证通过后，才能开始路由映射 / 鉴权审计 / 漏洞检测等任何审计步骤

**如果 dnSpy 工具不可用，必须向用户报告 "dnSpy 工具不可用，无法开始 .NET 代码审计"，不得跳过反编译直接开始审计。**

### 0.2 反编译验证方法

执行全量反编译后，必须验证结果：

```bash
# 确认输出目录中有 .cs 文件
ls {output_path}/decompiled/  # 应能看到多个 .cs 文件或目录
```

**验证标准**：
- 输出目录中必须存在至少一个 .cs 文件
- 如果输出目录为空或不存在 .cs 文件，说明反编译失败
- 反编译失败时必须尝试下面的故障排查，不得直接进入审计

---

## 1. 反编译工具

### 1.1 工具信息

- **工具名称**: dnSpy.Console.exe
- **用途**: 反编译 .NET 程序集（.dll / .exe）为 C# 源码
- **支持格式**: .NET Framework / .NET Core / .NET 5+ 程序集

### 1.2 路径搜索与 fallback 策略

**dnSpy.Console.exe 路径查找优先级（从高到低）：**

| 优先级 | 搜索路径 | 说明 |
|--------|---------|------|
| 1 | 用户显式指定的路径 | 用户提供完整路径时直接使用 |
| 2 | `当前工作目录/dnSpy/dnSpy.Console.exe` | 默认目录 |
| 3 | `源码目录/dnSpy/dnSpy.Console.exe` | 源码同级目录 |
| 4 | `D:\dnSpy\dnSpy.Console.exe` | Windows 常见安装路径 |
| 5 | `C:\dnSpy\dnSpy.Console.exe` | Windows 常见安装路径 |
| 6 | 用户 PATH 中的 `dnSpy.Console.exe` | 全局搜索 |

**搜索策略：** 按上述顺序依次检查，找到第一个存在的可用路径后立即使用。如果全部路径都不存在，向用户报告并停止。

### 1.3 待反编译目录查找优先级

| 优先级 | 搜索路径 | 说明 |
|--------|---------|------|
| 1 | 用户显式指定的路径 | 用户提供完整路径时直接使用 |
| 2 | `源码目录/bin/` | 默认部署目录 |
| 3 | `源码目录/bin`（无斜杠） | Windows 兼容写法 |
| 4 | `源码目录` 下所有 .dll/.exe | 扁平 bin 目录 |

### 1.4 基本命令格式

```bash
# 完整路径写法
"path/to/dnSpy.Console.exe" -o <输出目录> -r <待反编译目录>

# 使用默认路径的简写（工具=当前目录/dnSpy/，输入=当前目录/bin/）
"dnSpy/dnSpy.Console.exe" -o <输出目录> -r bin/
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 工具路径 | dnSpy.Console.exe 所在路径 | 按 1.2 优先级搜索 |
| `-o` | 反编译输出目录 | 无默认值，必须指定 |
| `-r` | 递归反编译指定目录下所有程序集 | `./bin/` |

### 1.5 权限与访问失败处理

**常见权限问题及处理方案：**

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `dnSpy.Console.exe` 不存在 | 工具未安装或路径错误 | 按 1.2 优先级搜索，提示用户 |
| 无法读取 bin 目录 | 权限不足 | 检查文件权限，尝试以管理员身份运行 |
| 无法写入输出目录 | 输出目录无写权限 | 更换输出目录到用户有权限的位置（如 `%TEMP%`） |
| 部分 DLL 反编译失败 | 非 .NET 程序集 | 记录失败 DLL，继续处理其余 DLL，报告中注明 |
| 输出目录已存在旧文件 | 上次反编译缓存 | 清空输出目录后重新反编译 |

**权限不足时的降级策略：**

如果当前工具无法访问某个文件：
1. 尝试使用其他内置工具（Read 等）读取文件内容
2. 如果 Read 等内置工具也无法访问，记录该文件为 "无法访问"
3. 不得因为部分文件无法访问而中断整体审计，继续处理可访问的文件
4. 在最终报告中注明无法访问的文件列表

---

## 2. 何时反编译

### 2.1 必须反编译的场景

| 场景 | 说明 |
|------|------|
| 无源码，只有编译后的程序集 | 部署目录只有 bin/ 下的 .dll/.exe |
| 第三方 DLL 中的关键逻辑 | 自定义权限过滤器、加密库等 |
| 混淆后的程序集 | 需要反编译还原逻辑（混淆程度影响可读性） |
| GAC 中的全局程序集 | 从 GAC 提取并反编译 |

### 2.2 不需要反编译的场景

| 场景 | 说明 |
|------|------|
| 源码已存在且可读取 | 直接分析 .cs 文件 |
| NuGet 标准库 | Microsoft 官方包，通常不包含业务漏洞 |
| 仅需查看 Web.config | XML 配置直接读取 |

---

## 3. 反编译策略

### 3.1 全量反编译（默认，审计前必须执行）

```bash
# 反编译整个 bin 目录（所有 .NET 审计必须执行此步骤）
mkdir -p {output_path}/decompiled
dnSpy.Console.exe -o {output_path}/decompiled -r bin/

# 验证
ls {output_path}/decompiled/
```

### 3.2 策略1: 最小化反编译

仅反编译与审计目标直接相关的程序集：

```bash
# 步骤1: 识别目标程序集
# ASP.NET WebForms: 查找 App_Code 或 bin 下的项目 DLL
# ASP.NET MVC: 查找 Controllers/Models 所在程序集
# Web API: 查找 ApiController 所在程序集

# 步骤2: 仅反编译目标程序集（默认从当前目录的 bin/ 读取）
mkdir -p /output/decompiled/TargetProject
dnSpy/dnSpy.Console.exe -o /output/decompiled/TargetProject -r bin/TargetProject.dll
```

### 3.3 策略2: 分层反编译

```bash
# 第一层: 反编译业务逻辑层（Controller/Handler/Service）
mkdir -p /output/decompiled/business
dnSpy/dnSpy.Console.exe -o /output/decompiled/business -r bin/

# 第二层: 反编译数据访问层（Repository/DAO/DbContext）
# （从第一层结果中识别需要深入分析的 DAL 程序集）
mkdir -p /output/decompiled/dal
dnSpy/dnSpy.Console.exe -o /output/decompiled/dal -r bin/DataAccess.dll

# 第三层: 反编译安全/认证模块
mkdir -p /output/decompiled/security
dnSpy/dnSpy.Console.exe -o /output/decompiled/security -r bin/Security.dll
```

---

## 4. 各审计类型的反编译目标

| 审计类型 | 必须反编译的程序集 | 识别模式 |
|----------|-------------------|----------|
| 路由映射 | Controller/Handler 所在 DLL | `*Controller.dll`, `*Handler.dll`, `*Module.dll` |
| SQL 注入 | DAL/Repository 所在 DLL | `*Dao.dll`, `*Repository.dll`, `*DataAccess.dll` |
| 鉴权审计 | Auth/Filter 所在 DLL | `*Auth.dll`, `*Security.dll`, `*Filter.dll` |
| XXE 注入 | XML 处理所在 DLL | 含 `XmlReader`, `XmlDocument`, `XDocument` 的程序集 |
| 文件上传 | 上传处理所在 DLL | 含 `HttpPostedFile`, `IFormFile` 的程序集 |
| 文件读取 | 文件操作所在 DLL | 含 `File.Read`, `StreamReader` 的程序集 |

---

## 5. 反编译结果的源码定位

反编译后，dnSpy 会按命名空间生成目录结构：

```
output_dir/
└── 项目名/
    └── 命名空间/
        └── 类名.cs
```

示例：
```bash
# 原始 DLL: MyApp.Web.dll
# 包含命名空间: MyApp.Web.Controllers
# 反编译输出:
decompiled/MyApp.Web/MyApp.Web/Controllers/UserController.cs
decompiled/MyApp.Web/MyApp.Web/Controllers/OrderController.cs
decompiled/MyApp.Web/MyApp.Web/Models/UserModel.cs
```

---

## 6. 常见故障与解决方案

| 故障 | 原因 | 解决方案 |
|------|------|----------|
| 反编译输出为空 | 目标不是 .NET 程序集 | 检查文件是否为托管程序集（使用 `file` 命令确认） |
| 代码不可读/乱码 | 程序集被混淆 | 尝试 de4dot 等去混淆工具预处理 |
| 缺少依赖导致报错 | 引用的 DLL 不在目录中 | 确保所有依赖 DLL 在同一目录或 GAC 中 |
| 反编译后编译错误 | 泛型/lambda/async 还原不完美 | 正常现象，关注逻辑而非语法精确性 |
| .NET Core 程序集反编译失败 | 跨平台格式差异 | 确认 dnSpy 版本支持 .NET Core |
| dnSpy.Console.exe 不存在 | 路径未正确设置 | 按 1.2 优先级搜索，提示用户手动指定 |
| 部分文件无法访问 | 权限不足或文件锁定 | 使用降级策略继续，记录未访问文件 |

---

## 7. 反编译结果记录规范

输出时必须标注反编译来源：

```markdown
=== [SQL-001] SQL 注入 - 字符串拼接 ===
风险等级: 高
位置: UserRepository.GetUserById (UserRepository.cs:25)
来源: **反编译 bin/UserRepository.dll**
框架: ADO.NET

漏洞特征:
- 使用字符串拼接构建 SQL
- 参数 id 直接拼接到查询语句

漏洞代码:
\```csharp
string sql = "SELECT * FROM Users WHERE Id = " + id;
SqlCommand cmd = new SqlCommand(sql, conn);
SqlDataReader reader = cmd.ExecuteReader();
\```
```

---

## 8. 性能优化

- **批量反编译**: 使用 `-r` 参数一次反编译整个目录，比逐个文件效率更高
- **缓存利用**: 反编译结果保存到指定目录，后续分析直接读取，避免重复反编译
- **选择性反编译**: 优先反编译目标程序集，避免全量反编译浪费时间
- **共享反编译输出**: 多个审计 skill 共享 `decompiled/` 目录，避免重复工作
