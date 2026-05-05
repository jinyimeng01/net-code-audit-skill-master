---
name: dotnet-route-tracer
version: 2.0.0
description: .NET 调用链追踪 skill。从 Controller/Page/Handler/WCF Operation 入口追踪到 SQL、文件、XML、命令、HTTP 请求等 sink。输出参数传播路径、可达性结论和代码证据。
description_en: .NET call-chain tracing skill. Traces from Controller/Page/Handler/WCF entry points to SQL, file, XML, command, and HTTP request sinks. Outputs parameter propagation paths, reachability conclusions, and code evidence.
author: net-code-audit-team
tags: ['dotnet', 'taint-analysis', 'call-chain', 'reachability']
compatibility: ['asp.net', 'asp.net-core', 'wcf']
---

# .NET 调用链追踪工具

追踪指定 .NET Web 路由的完整调用链，分析参数从 HTTP 入口到最终 Sink 的传递过程。

## 核心要求

**此技能必须完整追踪参数从入口到 Sink 的完整路径，不允许省略任何中间调用。**

- 必须追踪每一层方法调用
- 必须标注参数在每层的变量名变化
- 必须标注参数是否被修改/过滤/拼接
- 必须标注最终是否到达危险 Sink
- 禁止省略中间调用层

---

## 漏洞分级标准

**详见 [SEVERITY_RATING.md](../shared/SEVERITY_RATING.md)**

---

## 反编译支持（CRITICAL）

**当源码不可用时，必须使用 dnSpy.Console.exe 反编译相关程序集。**

详见 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md)

```bash
# 反编译目标程序集以追踪调用链
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r bin/
```

---

## 工作流程

### 1. 确定追踪目标

从 dotnet-route-mapper 的输出或用户指定获取待追踪的路由信息：

| 信息 | 来源 | 用途 |
|------|------|------|
| 路由路径 | route-mapper | 定位入口方法 |
| HTTP 方法 | route-mapper | 确定入口类型 |
| 参数列表 | route-mapper | 确定追踪起点 |
| Controller 类 | route-mapper | 定位代码位置 |

### 2. 逐层追踪

```
HTTP 入口: Controller.Action(param)
    ↓ 调用
L1: Service.Method(param)
    ↓ 调用
L2: Repository.Query(param)
    ↓ 调用
L3: SqlCommand.ExecuteNonQuery(sql)  ← Sink
```

**每层必须记录：**

| 信息 | 说明 |
|------|------|
| 类名.方法名 | 当前层的方法 |
| 参数名 | 当前层接收的参数名（关注变化） |
| 参数处理 | 是否拼接/过滤/转换/传递 |
| 调用下一层 | 传递给下一层的参数 |
| 代码位置 | 文件名:行号 |

### 3. 参数可控性分析

| 状态 | 含义 | 标注 |
|------|------|------|
| 被使用 | 参数直接或间接到达 Sink | 被使用（描述使用方式） |
| 未使用 | 参数被硬编码覆盖或未传递 | 未使用（描述覆盖原因） |
| 部分使用 | 参数部分字段被使用 | 部分使用（描述哪些字段） |

### 4. 分支条件追踪

当调用链中存在条件分支时，分析各分支：

```csharp
if (isAdmin) {
    // 分支A: 无需鉴权，参数直接进入 SQL
} else {
    // 分支B: 参数被过滤后使用
}
```

**必须标注：**
- 分支条件
- 各分支的参数处理方式
- 默认执行哪个分支

### 5. 生成输出

**严格按照 references/ 目录中的填充式模板生成输出文件。**

| 文件类型 | 模板 | 命名格式 |
|---------|------|---------|
| 完整追踪报告 | [OUTPUT_TEMPLATE_FULL.md](references/OUTPUT_TEMPLATE_FULL.md) | `route_tracer/{route_name}/{project_name}_trace_{route_id}_{YYYYMMDD}.md` |
| 简化追踪报告 | [OUTPUT_TEMPLATE_SIMPLE.md](references/OUTPUT_TEMPLATE_SIMPLE.md) | `route_tracer/{route_name}/{project_name}_trace_{route_id}_simple_{YYYYMMDD}.md` |
| 多方法索引 | [OUTPUT_TEMPLATE_INDEX.md](references/OUTPUT_TEMPLATE_INDEX.md) | `route_tracer/{route_name}/{project_name}_trace_all_methods_{YYYYMMDD}.md` |

---

## 验证检查清单

- [ ] 调用链已从入口追踪到最终 Sink
- [ ] 每层调用的参数名变化已记录
- [ ] 参数可控性分析已完成
- [ ] 分支条件已分析
- [ ] 反编译来源已标注（如适用）
