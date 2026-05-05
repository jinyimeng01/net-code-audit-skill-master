# Dapper SQL 注入审计详解

## 目录

- [Dapper 基础概念](#dapper-基础概念)
- [危险模式检测](#危险模式检测)
- [安全模式识别](#安全模式识别)
- [动态 SQL 构建](#动态-sql-构建)
- [常见漏洞场景](#常见漏洞场景)

---

## Dapper 基础概念

### 识别特征

**NuGet 依赖：**
```
Dapper
Dapper.Contrib
Dapper.Extensions
```

**代码特征：**
```csharp
using Dapper;

// 基本查询
var users = connection.Query<User>("SELECT * FROM Users");

// 参数化查询
var user = connection.QueryFirstOrDefault<User>(
    "SELECT * FROM Users WHERE Id = @Id", new { Id = id });
```

### 核心方法

| 方法 | 说明 | 返回类型 |
|------|------|----------|
| `Query<T>` | 查询多行 | `IEnumerable<T>` |
| `QueryFirstOrDefault<T>` | 查询首行 | `T` |
| `QuerySingle<T>` | 查询单行 | `T` |
| `Execute` | 执行非查询 | `int`（影响行数） |
| `ExecuteScalar<T>` | 查询单值 | `T` |
| `QueryMultiple` | 多结果集 | `GridReader` |

---

## 危险模式检测

### 1. 字符串拼接

```csharp
// 高危：直接拼接
string id = Request.Query["id"];
var user = connection.Query<User>(
    "SELECT * FROM Users WHERE Id = " + id);

// 高危：拼接字符串参数
string name = Request.Form["name"];
var users = connection.Query<User>(
    "SELECT * FROM Users WHERE Name = '" + name + "'");

// 高危：String.Format
var users = connection.Query<User>(
    String.Format("SELECT * FROM Users WHERE Id = {0}", id));

// 高危：内插字符串
var users = connection.Query<User>(
    $"SELECT * FROM Users WHERE Id = {id}");
```

### 2. 检测正则

```bash
# 搜索 Dapper 查询中的拼接
grep -rn '\.Query.*+' --include="*.cs"
grep -rn '\.Execute.*+' --include="*.cs"
grep -rn 'FromSqlRaw\|ExecuteSqlRaw' --include="*.cs"
grep -rn '\$".*SELECT\|\$".*INSERT\|\$".*UPDATE\|\$".*DELETE' --include="*.cs"
```

---

## 安全模式识别

### 1. 匿名对象参数（推荐）

```csharp
// 安全：匿名对象参数化
var user = connection.QueryFirstOrDefault<User>(
    "SELECT * FROM Users WHERE Id = @Id", new { Id = id });

// 安全：多参数
var users = connection.Query<User>(
    "SELECT * FROM Users WHERE Name = @Name AND Age > @Age",
    new { Name = name, Age = age });
```

### 2. DynamicParameters

```csharp
// 安全：DynamicParameters
var parameters = new DynamicParameters();
parameters.Add("@Name", name, DbType.String);
parameters.Add("@Age", age, DbType.Int32);
var users = connection.Query<User>(
    "SELECT * FROM Users WHERE Name = @Name AND Age > @Age", parameters);
```

### 3. Dapper Contrib

```csharp
// 安全：Dapper.Contrib 自动参数化
var user = connection.Get<User>(id);
var users = connection.GetAll<User>();
connection.Insert(new User { Name = "test" });
connection.Update(user);
connection.Delete(user);
```

---

## 动态 SQL 构建

### 危险模式

```csharp
// 高危：动态 WHERE 拼接
StringBuilder sql = new StringBuilder("SELECT * FROM Users WHERE 1=1");
if (!string.IsNullOrEmpty(name))
{
    sql.Append(" AND Name = '" + name + "'");  // 注入点
}
if (age.HasValue)
{
    sql.Append(" AND Age = " + age);  // 注入点
}
var users = connection.Query<User>(sql.ToString());
```

### 安全模式

```csharp
// 安全：动态 SQL + 参数化
StringBuilder sql = new StringBuilder("SELECT * FROM Users WHERE 1=1");
var parameters = new DynamicParameters();

if (!string.IsNullOrEmpty(name))
{
    sql.Append(" AND Name = @Name");
    parameters.Add("@Name", name);
}
if (age.HasValue)
{
    sql.Append(" AND Age = @Age");
    parameters.Add("@Age", age.Value);
}
var users = connection.Query<User>(sql.ToString(), parameters);
```

### Dapper SQL Builder

```csharp
// 安全：使用 Dapper.SqlBuilder
var builder = new SqlBuilder();
var template = builder.AddTemplate("SELECT * FROM Users /**where**/");

if (!string.IsNullOrEmpty(name))
{
    builder.Where("Name = @Name", new { Name = name });
}
if (age.HasValue)
{
    builder.Where("Age = @Age", new { Age = age });
}
var users = connection.Query<User>(template.RawSql, template.Parameters);
```

---

## 常见漏洞场景

### 场景 1：ORDER BY 注入

```csharp
// 高危：ORDER BY 拼接
string sort = Request.Query["sort"];
var users = connection.Query<User>(
    $"SELECT * FROM Users ORDER BY {sort}");

// 安全：白名单校验
string sort = Request.Query["sort"];
string[] allowed = { "Id", "Name", "CreatedAt" };
if (!allowed.Contains(sort)) sort = "Id";
var users = connection.Query<User>(
    "SELECT * FROM Users ORDER BY " + sort);
```

### 场景 2：IN 子句

```csharp
// 高危：IN 拼接
string ids = Request.Query["ids"];
var users = connection.Query<User>(
    "SELECT * FROM Users WHERE Id IN (" + ids + ")");

// 安全：Dapper 自动展开数组参数
int[] idArray = ids.Split(',').Select(int.Parse).ToArray();
var users = connection.Query<User>(
    "SELECT * FROM Users WHERE Id IN @Ids", new { Ids = idArray });
```

### 场景 3：LIKE 查询

```csharp
// 高危：LIKE 拼接
string keyword = Request.Query["keyword"];
var users = connection.Query<User>(
    "SELECT * FROM Users WHERE Name LIKE '%" + keyword + "%'");

// 安全：参数化 LIKE
var users = connection.Query<User>(
    "SELECT * FROM Users WHERE Name LIKE @Keyword",
    new { Keyword = "%" + keyword + "%" });
```

### 场景 4：表名动态

```csharp
// 高危：动态表名
string table = Request.Query["table"];
var data = connection.Query($"SELECT * FROM {table}");

// 安全：白名单校验
string table = Request.Query["table"];
if (!ALLOWED_TABLES.Contains(table))
    throw new ArgumentException("Invalid table");
var data = connection.Query($"SELECT * FROM {table}");
```

### 场景 5：存储过程

```csharp
// 高危：拼接存储过程
var result = connection.Query("EXEC sp_GetUser " + userId);

// 安全：参数化存储过程
var result = connection.Query("sp_GetUser",
    new { UserId = userId },
    commandType: CommandType.StoredProcedure);
```

---

## 修复要求

1. **始终使用参数化查询**（匿名对象或 DynamicParameters）
2. **动态标识符使用白名单**（表名、列名、ORDER BY）
3. **IN 子句使用 `@Ids` + 数组参数**
4. **LIKE 使用参数化 + 通配符在参数值中**
5. **存储过程使用 CommandType.StoredProcedure**
