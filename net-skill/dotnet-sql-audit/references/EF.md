# Entity Framework SQL 注入审计详解

## 目录

- [EF 基础概念](#ef-基础概念)
- [FromSqlRaw/FromSqlInterpolated](#fromsqlrawfromsqlinterpolated)
- [SqlQuery 危险模式](#sqlquery-危险模式)
- [LINQ 安全性](#linq-安全性)
- [动态排序漏洞](#动态排序漏洞)
- [常见漏洞场景](#常见漏洞场景)

---

## EF 基础概念

### 识别特征

**NuGet 依赖：**
```
Microsoft.EntityFrameworkCore
Microsoft.EntityFrameworkCore.SqlServer
System.Data.Entity (EF6)
```

**代码特征：**
```csharp
// EF Core
public class AppDbContext : DbContext
{
    public DbSet<User> Users { get; set; }
}

// EF6
public class AppDbContext : DbContext
{
    public IDbSet<User> Users { get; set; }
}
```

### 查询方式

| 方式 | 说明 | 是否可注入 |
|------|------|-----------|
| LINQ 查询 | 类型安全查询 | 否（安全） |
| FromSqlRaw | 原始 SQL | 取决于是否参数化 |
| FromSqlInterpolated | 插值 SQL | 安全（自动参数化） |
| ExecuteSqlRaw | 执行原始 SQL | 取决于是否参数化 |
| SqlQuery (EF6) | 原始 SQL 查询 | 取决于是否参数化 |

---

## FromSqlRaw/FromSqlInterpolated

### 危险模式（FromSqlRaw 拼接）

```csharp
// 高危：FromSqlRaw 字符串拼接
string name = Request.Query["name"];
var users = _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Name = '" + name + "'")
    .ToList();

// 高危：String.Format
var users = _context.Users
    .FromSqlRaw(String.Format("SELECT * FROM Users WHERE Id = {0}", id))
    .ToList();

// 高危：内插字符串
var users = _context.Users
    .FromSqlRaw($"SELECT * FROM Users WHERE Id = {id}")
    .ToList();
```

### 安全模式

```csharp
// 安全：FromSqlRaw + 参数化
var users = _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Name = {0}", name)
    .ToList();

// 安全：FromSqlRaw + SqlParameter
var param = new SqlParameter("@Name", name);
var users = _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Name = @Name", param)
    .ToList();

// 安全：FromSqlInterpolated（自动参数化）
var users = _context.Users
    .FromSqlInterpolated($"SELECT * FROM Users WHERE Name = {name}")
    .ToList();
```

**关键区别：**
- `FromSqlRaw($"...{var}")` — **危险**，C# 内插字符串在方法调用前已拼接
- `FromSqlInterpolated($"...{var}")` — **安全**，参数作为 FormattableString 传递

---

## SqlQuery 危险模式

### EF6 SqlQuery

```csharp
// 高危：SqlQuery 字符串拼接
string keyword = Request.QueryString["keyword"];
var users = _context.Database.SqlQuery<User>(
    "SELECT * FROM Users WHERE Name LIKE '%" + keyword + "%'").ToList();

// 安全：SqlQuery 参数化
var param = new SqlParameter("@Keyword", "%" + keyword + "%");
var users = _context.Database.SqlQuery<User>(
    "SELECT * FROM Users WHERE Name LIKE @Keyword", param).ToList();
```

### EF Core ExecuteSqlRaw

```csharp
// 高危：ExecuteSqlRaw 拼接
string id = Request.Query["id"];
_context.Database.ExecuteSqlRaw("DELETE FROM Users WHERE Id = " + id);

// 安全：ExecuteSqlRaw 参数化
_context.Database.ExecuteSqlRaw("DELETE FROM Users WHERE Id = {0}", id);

// 安全：ExecuteSqlInterpolated
_context.Database.ExecuteSqlInterpolated($"DELETE FROM Users WHERE Id = {id}");
```

---

## LINQ 安全性

### 安全的 LINQ 查询

```csharp
// 安全：LINQ 查询自动参数化
var users = _context.Users
    .Where(u => u.Name == name)
    .ToList();

// 安全：LINQ 动态查询
var query = _context.Users.AsQueryable();
if (!string.IsNullOrEmpty(name))
{
    query = query.Where(u => u.Name.Contains(name));
}
var result = query.ToList();
```

### 危险的 LINQ 动态查询

```csharp
// 高危：使用原始 SQL 片段
var users = _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE " + whereClause)
    .ToList();

// 高危：EF.Property 动态排序拼接
var query = _context.Users.OrderBy(u => EF.Property<object>(u, sortColumn));
// sortColumn 若来自用户输入，可能被利用
```

### 注意：LINQ to Entities vs LINQ to Objects

```csharp
// 安全：LINQ to Entities（数据库端执行）
var users = _context.Users.Where(u => u.Name == input).ToList();

// 需注意：LINQ to Objects（内存端执行，可能信息泄露）
var users = _context.Users.ToList().Where(u => u.Name == input);
```

---

## 动态排序漏洞

### 高危模式

```csharp
// 高危：ORDER BY 拼接
string sortBy = Request.Query["sortBy"];
string sql = "SELECT * FROM Users ORDER BY " + sortBy;
var users = _context.Users.FromSqlRaw(sql).ToList();

// 高危：使用 System.Linq.Dynamic.Core
string orderBy = Request.Query["orderBy"];
var users = _context.Users.OrderBy(orderBy).ToList();
// orderBy = "Id; DROP TABLE Users--" 可能导致注入
```

### 安全方式

```csharp
// 安全：白名单校验
string sortBy = Request.Query["sortBy"];
var allowedColumns = new Dictionary<string, Expression<Func<User, object>>>
{
    ["name"] = u => u.Name,
    ["id"] = u => u.Id,
    ["created"] = u => u.CreatedAt
};

var query = _context.Users.AsQueryable();
if (allowedColumns.TryGetValue(sortBy, out var sortExpr))
{
    query = query.OrderBy(sortExpr);
}
var users = query.ToList();
```

---

## 常见漏洞场景

### 场景 1：动态条件构建

```csharp
// 高危：动态 WHERE 拼接
public List<User> Search(string name, int? age)
{
    StringBuilder sql = new StringBuilder("SELECT * FROM Users WHERE 1=1");
    if (name != null)
    {
        sql.Append(" AND Name = '" + name + "'");  // 注入点
    }
    if (age.HasValue)
    {
        sql.Append(" AND Age = " + age);  // 注入点
    }
    return _context.Users.FromSqlRaw(sql.ToString()).ToList();
}

// 安全：使用 LINQ 动态查询
public List<User> Search(string name, int? age)
{
    var query = _context.Users.AsQueryable();
    if (name != null)
    {
        query = query.Where(u => u.Name == name);
    }
    if (age.HasValue)
    {
        query = query.Where(u => u.Age == age.Value);
    }
    return query.ToList();
}
```

### 场景 2：存储过程调用

```csharp
// 高危：拼接存储过程
_context.Database.ExecuteSqlRaw("EXEC sp_DeleteUser " + userId);

// 安全：参数化存储过程
_context.Database.ExecuteSqlRaw("EXEC sp_DeleteUser @UserId",
    new SqlParameter("@UserId", userId));
```

### 场景 3：LIKE 查询

```csharp
// 高危：LIKE 拼接
var users = _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Name LIKE '%" + keyword + "%'")
    .ToList();

// 安全：参数化 LIKE
var param = new SqlParameter("@Keyword", "%" + keyword + "%");
var users = _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Name LIKE @Keyword", param)
    .ToList();
```

### 场景 4：IN 子句

```csharp
// 高危：IN 拼接
string ids = Request.Query["ids"];
var users = _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Id IN (" + ids + ")")
    .ToList();

// 安全：使用 LINQ Contains
int[] idArray = ids.Split(',').Select(int.Parse).ToArray();
var users = _context.Users
    .Where(u => idArray.Contains(u.Id))
    .ToList();
```

---

## 检查清单

### FromSqlRaw/ExecuteSqlRaw 检查

- [ ] 搜索所有 `FromSqlRaw` 调用
- [ ] 搜索所有 `ExecuteSqlRaw` 调用
- [ ] 检查 SQL 字符串是否有拼接
- [ ] 确认使用参数化（`{0}` 占位符或 SqlParameter）
- [ ] ORDER BY 是否有白名单校验

### EF6 特有检查

- [ ] 搜索 `SqlQuery` 调用
- [ ] 搜索 `ExecuteSqlCommand` 调用
- [ ] 检查 Entity SQL 拼接

### LINQ 检查

- [ ] 是否使用了 `System.Linq.Dynamic` 且输入未过滤
- [ ] 是否有 `ToList()` 后再过滤导致全表加载
