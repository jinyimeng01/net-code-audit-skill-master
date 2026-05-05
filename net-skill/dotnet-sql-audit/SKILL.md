---
name: dotnet-sql-audit
version: 2.0.0
description: .NET SQL 注入审计 skill。覆盖 ADO.NET SqlCommand、Entity Framework FromSqlRaw/ExecuteSqlRaw、Dapper Query、NHibernate HQL、动态 SQL 拼接。追踪用户可控输入到数据库查询 sink，输出注入证据和修复建议。
description_en: .NET SQL injection audit skill. Covers ADO.NET SqlCommand, Entity Framework FromSqlRaw/ExecuteSqlRaw, Dapper Query, NHibernate HQL, dynamic SQL concatenation. Traces user input to database query sinks.
author: net-code-audit-team
tags: ['dotnet', 'sql-injection', 'sqli', 'ado.net', 'entity-framework', 'dapper']
compatibility: ['asp.net', 'asp.net-core', 'wcf']
---

# .NET SQL 注入漏洞审计工具

扫描 .NET Web 项目源码或反编译结果，定位所有 SQL 执行入口，检测 SQL 注入漏洞。

> **审计边界（本技能仅检测以下内容，不得超出此范围）：**
> - SQL 注入漏洞（参数拼接、动态 SQL、ORDER BY 注入等）
> - 参数化查询缺失
> - 不包括：代码质量问题、架构安全问题、其他漏洞类型

---

## 漏洞分级标准

**详见 [SEVERITY_RATING.md](../shared/SEVERITY_RATING.md)**

- 漏洞编号格式: `{C/H/M/L}-SQL-{序号}`
- 严重等级 = f(可达性 R, 影响范围 I, 利用复杂度 C)
- Score = R x 0.40 + I x 0.35 + C x 0.25，映射 CVSS 3.1

---

## 核心要求

**此技能必须完整分析所有 SQL 相关代码，不允许省略。**

- 必须识别所有 SQL 执行入口点（ADO.NET/EF/Dapper/NHibernate）
- 必须分析每个 SQL 操作的参数化情况
- 必须检测所有潜在的 SQL 注入模式
- 必须为每个风险点提供验证 PoC
- 禁止省略任何 SQL 操作
- 禁止跳过反编译步骤

### 禁止省略规则（强制）

| 禁止写法 | 正确做法 |
|:---------|:---------|
| `{...省略...}` | 完整列出所有条目 |
| `... (其他N个)` | 完整列出所有条目 |
| `等等` / `etc.` | 完整列出所有条目 |

---

## 技能协作流程（CRITICAL）

**dotnet-sql-audit 应在 dotnet-route-mapper 之后执行，基于已梳理的路由信息进行审计。**

```
[步骤1] dotnet-route-mapper
    │ 输出: 所有 HTTP 路由列表 + 参数定义
    ↓
[步骤2] dotnet-sql-audit（本技能）
    │ 输入: dotnet-route-mapper 的输出
    │ 执行: 快速扫描 → 参数-SQL 映射 → 深入分析
    ├─── 需要深入追踪 ───→ dotnet-route-tracer
    ↓
[步骤3] 输出综合审计报告
```

### 输入依赖

**如果 route_mapper 输出不存在，必须先运行 dotnet-route-mapper。**

---

## 反编译支持（CRITICAL）

**当源码不可用时，必须使用 dnSpy.Console.exe 反编译 SQL 相关程序集。**

详见 [DOTNET_DECOMPILE_STRATEGY.md](../shared/DOTNET_DECOMPILE_STRATEGY.md)

```bash
# 反编译数据访问层
mkdir -p {output_path}/decompiled
dnSpy/dnSpy.Console.exe -o {output_path}/decompiled -r bin/
```

### 必须反编译的目标

| 类型 | 匹配模式 | 目的 |
|------|----------|------|
| Repository/DAL | `*Repository.dll`, `*Dao.dll`, `*DataAccess.dll` | 提取 SQL 执行逻辑 |
| Service | `*Service.dll`, `*ServiceImpl.dll` | 追踪 SQL 调用链 |
| 工具类 | `*SqlHelper*.dll`, `*DbHelper*.dll` | 提取通用 SQL 方法 |
| Entity/Model | `*Entity.dll`, `*Model.dll` | EF 映射分析 |

---

## SQL 框架识别

| 框架 | 识别特征 | 配置文件 | 参考资料 |
|------|----------|----------|----------|
| ADO.NET | `SqlCommand`, `SqlConnection`, `SqlDataReader` | `web.config` 连接字符串 | [ADONET.md](references/ADONET.md) |
| Entity Framework | `DbContext`, `DbSet`, LINQ to Entities | `App.config`/`web.config` EF 配置 | [EF.md](references/EF.md) |
| Dapper | `connection.Query<>`, `connection.Execute<>` | NuGet 包引用 | [DAPPER.md](references/DAPPER.md) |
| NHibernate | `ISession`, `ICriteria`, `HQL` | `hibernate.cfg.xml` | [NHIBERNATE.md](references/NHIBERNATE.md) |

---

## SQL 注入检测规则速查

### ADO.NET 危险 vs 安全

| 类型 | 危险模式 | 安全模式 |
|------|----------|----------|
| 查询 | `cmd.CommandText = "..."+var` | `cmd.Parameters.AddWithValue("@id", var)` |
| 拼接 | `+`, `StringBuilder`, `string.Format` | `@param` 参数化 |
| **ORDER BY** | `"ORDER BY " + sortBy` | **白名单校验** |
| 存储过程 | 拼接存储过程名 | `CommandType.StoredProcedure` + 参数 |

### Entity Framework 危险 vs 安全

| 类型 | 危险模式 | 安全模式 |
|------|----------|----------|
| 原始 SQL | `context.Database.SqlQuery<>("..."+var)` | `context.Database.SqlQuery<>("...WHERE Id=@p0", var)` |
| FromSqlRaw | `FromSqlRaw("..."+var)` | `FromSqlInterpolated($"...{var}")` |
| **排序** | `.OrderBy(sortBy)` 动态拼接 | **白名单校验** |
| LINQ | 安全（参数化） | LINQ 默认参数化 |

### Dapper 危险 vs 安全

| 类型 | 危险模式 | 安全模式 |
|------|----------|----------|
| 参数 | 直接拼接字符串 | `connection.Query<T>(sql, new { Id = id })` |
| **ORDER BY** | `$"ORDER BY {sortBy}"` | **白名单校验后使用** |

---

## 执行条件分析（CRITICAL - 避免误报）

**发现 SQL 拼接代码后，必须分析该代码是否真的会被执行！**

### 1. 代码路径可达性

| 检查项 | 说明 | 影响 |
|--------|------|------|
| 提前 return | `return "";`, `return null` | 代码不执行 |
| 异常抛出 | `throw new Exception()` | 代码不执行 |
| 条件不满足 | 死代码 | 代码不执行 |
| 环境限定 | 仅特定数据库/配置下执行 | 需确认环境 |

### 2. 结论分级

| 状态 | 含义 | 后续操作 |
|------|------|----------|
| 待验证 | 代码存在 SQL 拼接，但执行条件未确认 | 需确认目标环境 |
| 已确认可利用 | 已验证代码路径在目标环境下会执行 | 进行漏洞利用测试 |
| 不可利用 | 代码存在但在目标环境下不执行 | 标注原因，降低优先级 |
| 环境依赖 | 漏洞存在但仅在特定环境下可利用 | 标注环境条件 |

---

## 数据流追踪

当发现以下情况时，**必须调用 dotnet-route-tracer 技能进行深度追踪**：

| 场景 | 操作 |
|------|------|
| 参数经过多层传递 | 调用 dotnet-route-tracer |
| 参数类型转换 | 调用 dotnet-route-tracer |
| 基类 SQL 执行 | 调用 dotnet-route-tracer |
| 执行条件不明确 | 调用 dotnet-route-tracer |

---

## 输出格式

**严格按照 [references/OUTPUT_TEMPLATE.md](references/OUTPUT_TEMPLATE.md) 中的填充式模板生成输出文件。**

- 文件名格式: `{project_name}_sql_audit_{YYYYMMDD_HHMMSS}.md`
- 不得修改模板结构、不得增删章节、不得调整顺序
- 所有【填写】占位符必须替换为实际内容
- 通用规范参考: [shared/DOTNET_OUTPUT_STANDARD.md](../shared/DOTNET_OUTPUT_STANDARD.md)

---

## 验证检查清单

### 代码分析检查
- [ ] 所有 Repository/DAL 类已分析
- [ ] 每个 SQL 操作都有参数化状态标注

### 执行条件检查
- [ ] 分析了代码路径可达性
- [ ] 标注了每个漏洞的可利用性状态

### 漏洞检测检查
- [ ] 所有 ADO.NET 拼接模式已检测
- [ ] 所有 EF 原始 SQL 拼接已检测
- [ ] 所有 Dapper 字符串拼接已检测

### 报告完整性检查
- [ ] 综合审计报告已生成，且通过 OUTPUT_TEMPLATE.md 末尾的自检清单
