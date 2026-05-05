# .NET 命令执行与动态代码 Sink

## 直接命令执行

| API | 关键字段 | 审计点 |
|---|---|---|
| `Process.Start(string)` | 可执行文件或 URL | 输入是否控制文件、URL scheme、空格与参数 |
| `Process.Start(ProcessStartInfo)` | `FileName`, `Arguments`, `UseShellExecute`, `WorkingDirectory` | 参数拼接、shell 包装、工作目录污染 |
| `cmd.exe /c` | 命令字符串 | shell metacharacter、环境变量、编码 |
| `powershell` / `pwsh` | `-Command`, `-EncodedCommand`, script path | 用户输入是否进入脚本或参数 |
| COM / ShellExecute | ProgID、URL handler | 文件关联和协议处理 |

## 动态代码执行

| API | 风险 |
|---|---|
| `CodeDomProvider.CompileAssemblyFromSource` | 外部源码编译执行 |
| `Microsoft.CodeAnalysis.CSharp.Scripting.CSharpScript` | 表达式/脚本执行 |
| `Assembly.Load`, `LoadFrom`, `LoadFile` | 外部程序集或路径加载 |
| `Activator.CreateInstance`, `Type.GetType` | 类型名控制导致危险类型实例化 |
| `MethodInfo.Invoke`, `InvokeMember` | 方法名/参数控制 |
| `XamlReader.Parse` | XAML 对象图触发方法/属性链 |
| `XslCompiledTransform` | XSLT 脚本、扩展对象和外部资源 |
| `MSBuild`, `dotnet`, `csc`, `InstallUtil` 包装调用 | 构建脚本或项目文件被用户影响 |

## 参数注入

不是所有风险都表现为 `cmd.exe`。固定工具也可能因参数可控导致高危影响。

- 压缩/解压：路径穿越、覆盖文件、命令选项注入。
- 图片/Office/PDF 转换：读取远程资源、写入任意路径、模板执行。
- Git/SVN/工具链：URL、hook、配置文件、credential helper。
- 数据库/备份工具：导出路径、连接串、脚本参数。

## Windows/IIS 执行上下文

- 记录进程身份：ApplicationPoolIdentity、NetworkService、LocalSystem、自定义域账号。
- 记录当前目录和写权限：站点目录、`App_Data`、`Temp`、上传目录。
- 检查 32/64 位、WOW64、PowerShell 版本、执行策略只作为辅助信息，不当作防护。
- IIS 下命令输出通常不可直接回显，应使用日志、固定临时文件或 callback 做无害验证。

## 安全实现

- 固定可执行文件，参数使用结构化 allowlist。
- 避免 `cmd.exe /c` 和 shell 包装；必要时逐参数构造。
- 使用随机文件名和隔离临时目录。
- 动态插件必须签名校验、固定目录、最小权限和审计日志。
- 禁止从用户输入、上传文件、数据库可写字段直接加载源码、XAML、XSLT、程序集。
