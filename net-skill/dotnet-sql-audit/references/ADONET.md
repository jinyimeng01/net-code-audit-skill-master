# ADO.NET SQL 注入审计详解

## 目录

- [ADO.NET 基础概念](#adonet-基础概念)
- [危险模式检测](#危险模式检测)
- [安全模式识别](#安全模式识别)
- [存储过程调用](#存储过程调用)
- [ORDER BY 注入](#order-by-注入)
- [常见漏洞场景](#常见漏洞场景)

---

## ADO.NET 基础概念

### 核心类

| 类 | 作用 | 参数化支持 |
|---|------|-----------|
| `SqlCommand` | 执行 SQL 命令 | 支持（SqlParameter） |
| `SqlConnection` | 数据库连接 | - |
| `SqlDataReader` | 读取结果集 | - |
| `OleDbCommand` | OLE DB 命令 | 支持（OleDbParameter） |
| `OracleCommand` | Oracle 命令 | 支持（OracleParameter） |

### 识别特征

```csharp
using System.Data;
using System.Data.SqlClient;
using System.Data.Common;
```

---

## 危险模式检测

### 1. 字符串拼接（+ 号）

```csharp
// 高危：直接拼接用户输入
string id = Request.QueryString["id"];
string sql = "SELECT * FROM Users WHERE Id = " + id;
SqlCommand cmd = new SqlCommand(sql, conn);
SqlDataReader reader = cmd.ExecuteReader();

// 高危：拼接字符串参数
string name = Request.Form["name"];
string sql = "SELECT * FROM Users WHERE Name = '" + name + "'";
```

**检测正则：**
```regex
(executeReader|ExecuteReader|ExecuteNonQuery|ExecuteScalar)\s*\(\s*[^)]*\+
```

### 2. StringBuilder 拼接

```csharp
// 高危：使用 StringBuilder 构建 SQL
StringBuilder sb = new StringBuilder();
sb.Append("SELECT * FROM Users WHERE Name = '");
sb.Append(name);
sb.Append("'");
SqlCommand cmd = new SqlCommand(sb.ToString(), conn);
```

### 3. String.Format 拼接

```csharp
// 高危：使用 String.Format
string sql = String.Format("SELECT * FROM Users WHERE Id = {0}", id);
SqlCommand cmd = new SqlCommand(sql, conn);

// 高危：使用内插字符串
string sql = $"SELECT * FROM Users WHERE Id = {id}";
```

### 4. 字符串插值 ($"")

```csharp
// 高危：C# 6.0 字符串插值
string sql = $"DELETE FROM Users WHERE Id = {userId}";
SqlCommand cmd = new SqlCommand(sql, conn);
```

---

## 安全模式识别

### 1. SqlCommand + SqlParameter

```csharp
// 安全：使用参数化查询
string sql = "SELECT * FROM Users WHERE Id = @Id";
SqlCommand cmd = new SqlCommand(sql, conn);
cmd.Parameters.AddWithValue("@Id", userId);
SqlDataReader reader = cmd.ExecuteReader();

// 安全：多参数绑定
string sql = "SELECT * FROM Users WHERE Name = @Name AND Age = @Age";
SqlCommand cmd = new SqlCommand(sql, conn);
cmd.Parameters.AddWithValue("@Name", name);
cmd.Parameters.AddWithValue("@Age", age);
```

### 2. SqlParameter 类型方法

| 方法 | 数据类型 |
|------|----------|
| `AddWithValue("@param", value)` | 自动推断类型 |
| `Parameters.Add("@param", SqlDbType.Int)` | 指定类型 |
| `Parameters.Add("@param", SqlDbType.NVarChar, 100)` | 指定类型和长度 |

### 3. 完整安全示例

```csharp
string sql = "INSERT INTO Users (Name, Email, Age) VALUES (@Name, @Email, @Age)";
SqlCommand cmd = new SqlCommand(sql, conn);
cmd.Parameters.Add("@Name", SqlDbType.NVarChar, 100).Value = name;
cmd.Parameters.Add("@Email", SqlDbType.NVarChar, 200).Value = email;
cmd.Parameters.Add("@Age", SqlDbType.Int).Value = age;
cmd.ExecuteNonQuery();
```

---

## 存储过程调用

### 安全方式

```csharp
// 安全：使用 CommandType.StoredProcedure
SqlCommand cmd = new SqlCommand("sp_GetUserById", conn);
cmd.CommandType = CommandType.StoredProcedure;
cmd.Parameters.AddWithValue("@UserId", userId);
```

### 危险方式

```csharp
// 高危：拼接存储过程调用
string sql = "EXEC sp_GetUserById " + userId;
SqlCommand cmd = new SqlCommand(sql, conn);
cmd.ExecuteReader();
```

---

## ORDER BY 注入

### 危险模式

```csharp
// 高危：ORDER BY 无法使用参数化
string orderBy = Request.QueryString["sort"];
string sql = "SELECT * FROM Users ORDER BY " + orderBy;
SqlCommand cmd = new SqlCommand(sql, conn);
```

### 安全方式

```csharp
// 安全：白名单校验
string orderBy = Request.QueryString["sort"];
string[] allowedColumns = { "Id", "Name", "CreatedAt" };
if (!allowedColumns.Contains(orderBy))
{
    orderBy = "Id";
}
string sql = "SELECT * FROM Users ORDER BY " + orderBy;
```

---

## 常见漏洞场景

### 场景 1：动态表名/列名

```csharp
// 高危：动态表名无法使用参数化
string table = Request.QueryString["table"];
string sql = "SELECT * FROM " + table;

// 安全：白名单校验
string table = Request.QueryString["table"];
if (!ALLOWED_TABLES.Contains(table))
{
    throw new ArgumentException("Invalid table");
}
```

### 场景 2：IN 子句

```csharp
// 高危：IN 子句拼接
string ids = Request.QueryString["ids"]; // "1,2,3"
string sql = "SELECT * FROM Users WHERE Id IN (" + ids + ")";

// 安全：动态生成参数
string[] idArray = ids.Split(',');
string[] paramNames = idArray.Select((_, i) => $"@Id{i}").ToArray();
string sql = $"SELECT * FROM Users WHERE Id IN ({string.Join(",", paramNames)})";
SqlCommand cmd = new SqlCommand(sql, conn);
for (int i = 0; i < idArray.Length; i++)
{
    cmd.Parameters.AddWithValue(paramNames[i], int.Parse(idArray[i]));
}
```

### 场景 3：LIKE 子句

```csharp
// 高危：LIKE 拼接
string keyword = Request.QueryString["keyword"];
string sql = "SELECT * FROM Users WHERE Name LIKE '%" + keyword + "%'";

// 安全：参数化 LIKE
string sql = "SELECT * FROM Users WHERE Name LIKE @Keyword";
SqlCommand cmd = new SqlCommand(sql, conn);
cmd.Parameters.AddWithValue("@Keyword", "%" + keyword + "%");
```

### 场景 4：批量操作

```csharp
// 高危：批量 SQL 拼接
foreach (string id in ids)
{
    string sql = "DELETE FROM Users WHERE Id = " + id;
    SqlCommand cmd = new SqlCommand(sql, conn);
    cmd.ExecuteNonQuery();
}

// 安全：参数化批量
string sql = "DELETE FROM Users WHERE Id = @Id";
SqlCommand cmd = new SqlCommand(sql, conn);
cmd.Parameters.Add("@Id", SqlDbType.Int);
foreach (int id in ids)
{
    cmd.Parameters["@Id"].Value = id;
    cmd.ExecuteNonQuery();
}
```

---

## 修复要求

1. **始终使用 SqlParameter 参数化**，避免字符串拼接
2. **动态标识符使用白名单**（表名、列名、ORDER BY）
3. **存储过程使用 CommandType.StoredProcedure**
4. **输入验证作为补充**，不能替代参数化
