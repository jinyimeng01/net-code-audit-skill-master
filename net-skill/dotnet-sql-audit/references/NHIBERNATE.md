# NHibernate SQL 注入审计详解

## 目录

- [NHibernate 基础概念](#nhibernate-基础概念)
- [HQL 注入检测](#hql-注入检测)
- [Native SQL 注入检测](#native-sql-注入检测)
- [ICriteria 安全性](#icriteria-安全性)
- [常见漏洞场景](#常见漏洞场景)

---

## NHibernate 基础概念

### 识别特征

**NuGet 依赖：**
```
NHibernate
FluentNHibernate
```

**代码特征：**
```csharp
using NHibernate;
using NHibernate.Linq;

ISession session = sessionFactory.OpenSession();
```

### 查询方式

| 方式 | 说明 | 是否可注入 |
|------|------|-----------|
| HQL | Hibernate 查询语言 | 取决于是否参数化 |
| Native SQL | 原始 SQL | 取决于是否参数化 |
| ICriteria | 类型安全查询构建器 | 否（安全） |
| QueryOver | 强类型查询 | 否（安全） |
| NHibernate LINQ | LINQ 查询 | 否（安全） |

---

## HQL 注入检测

### 危险模式（字符串拼接）

```csharp
// 高危：HQL 字符串拼接
string username = Request.Form["username"];
var users = session.CreateQuery(
    "FROM User WHERE Username = '" + username + "'").List<User>();

// 高危：StringBuilder 拼接
StringBuilder hql = new StringBuilder("FROM User WHERE 1=1");
if (name != null)
{
    hql.Append(" AND Name = '" + name + "'");
}
var users = session.CreateQuery(hql.ToString()).List<User>();

// 高危：String.Format
var users = session.CreateQuery(
    String.Format("FROM User WHERE Id = {0}", id)).List<User>();
```

### 安全模式（参数绑定）

```csharp
// 安全：命名参数
string hql = "FROM User WHERE Username = :username";
var users = session.CreateQuery(hql)
    .SetParameter("username", username)
    .List<User>();

// 安全：位置参数
string hql = "FROM User WHERE Id = ?";
var users = session.CreateQuery(hql)
    .SetParameter(0, id)
    .List<User>();

// 安全：多参数
string hql = "FROM User WHERE Name = :name AND Age > :age";
var users = session.CreateQuery(hql)
    .SetParameter("name", name)
    .SetParameter("age", age)
    .List<User>();

// 安全：SetString / SetInt32 等类型化方法
string hql = "FROM User WHERE Name = :name";
var users = session.CreateQuery(hql)
    .SetString("name", name)
    .List<User>();
```

### 检测正则

```bash
grep -rn 'CreateQuery.*+' --include="*.cs"
grep -rn 'FROM.*+.*WHERE' --include="*.cs"
grep -rn 'CreateQuery.*\$"' --include="*.cs"
```

---

## Native SQL 注入检测

### 危险模式

```csharp
// 高危：Native SQL 拼接
string id = Request.Query["id"];
var users = session.CreateSQLQuery(
    "SELECT * FROM Users WHERE Id = " + id).List<User>();

// 高危：SQLQuery 拼接
string name = Request.Form["name"];
var users = session.CreateSQLQuery(
    "SELECT * FROM Users WHERE Name = '" + name + "'").List();
```

### 安全模式

```csharp
// 安全：命名参数
string sql = "SELECT * FROM Users WHERE Id = :id";
var users = session.CreateSQLQuery(sql)
    .AddEntity(typeof(User))
    .SetParameter("id", id)
    .List<User>();

// 安全：位置参数
string sql = "SELECT * FROM Users WHERE Name = ?";
var users = session.CreateSQLQuery(sql)
    .AddEntity(typeof(User))
    .SetParameter(0, name)
    .List<User>();
```

---

## ICriteria 安全性

### 安全的 ICriteria

```csharp
// 安全：ICriteria 类型安全
var users = session.CreateCriteria<User>()
    .Add(Restrictions.Eq("Name", name))
    .Add(Restrictions.Gt("Age", age))
    .List<User>();

// 安全：QueryOver 强类型
var users = session.QueryOver<User>()
    .Where(u => u.Name == name)
    .And(u => u.Age > age)
    .List();
```

### 危险的 ICriteria 方法

```csharp
// 高危：SqlRestriction 拼接
string filter = "Name = '" + name + "'";
var users = session.CreateCriteria<User>()
    .Add(Restrictions.SqlRestriction(filter))
    .List<User>();

// 安全：SqlRestriction 带参数
var users = session.CreateCriteria<User>()
    .Add(Restrictions.SqlRestriction(
        "Name = ?", name, NHibernateUtil.String))
    .List<User>();
```

### 危险方法列表

| 方法 | 风险 | 说明 |
|------|------|------|
| `Restrictions.SqlRestriction(sql)` | **高危** | 直接执行 SQL 片段 |
| `Restrictions.SqlRestriction(sql, val, type)` | 中 | 带参数但需检查 |
| `Projections.SqlProjection(sql, ...)` | **高危** | SQL 投影 |

---

## 常见漏洞场景

### 场景 1：动态 HQL 构建

```csharp
// 高危
public List<User> Search(string name, int? age)
{
    StringBuilder hql = new StringBuilder("FROM User WHERE 1=1");
    if (name != null)
        hql.Append(" AND Name = '" + name + "'");
    if (age.HasValue)
        hql.Append(" AND Age = " + age);
    return session.CreateQuery(hql.ToString()).List<User>();
}

// 安全
public List<User> Search(string name, int? age)
{
    StringBuilder hql = new StringBuilder("FROM User WHERE 1=1");
    var queryParams = new Dictionary<string, object>();

    if (name != null)
    {
        hql.Append(" AND Name = :name");
        queryParams["name"] = name;
    }
    if (age.HasValue)
    {
        hql.Append(" AND Age = :age");
        queryParams["age"] = age.Value;
    }

    var query = session.CreateQuery(hql.ToString());
    foreach (var kvp in queryParams)
    {
        query.SetParameter(kvp.Key, kvp.Value);
    }
    return query.List<User>();
}
```

### 场景 2：ORDER BY 注入

```csharp
// 高危：ORDER BY 拼接
string orderBy = Request.Query["sort"];
string hql = "FROM User ORDER BY " + orderBy;
var users = session.CreateQuery(hql).List<User>();

// 安全：白名单校验
string orderBy = Request.Query["sort"];
if (!ALLOWED_COLUMNS.Contains(orderBy))
    orderBy = "Id";
string hql = "FROM User ORDER BY " + orderBy;
```

### 场景 3：IN 子句

```csharp
// 高危：IN 拼接
string ids = Request.Query["ids"];
var users = session.CreateQuery(
    "FROM User WHERE Id IN (" + ids + ")").List<User>();

// 安全：使用 SetParameterList
int[] idArray = ids.Split(',').Select(int.Parse).ToArray();
var users = session.CreateQuery("FROM User WHERE Id IN (:ids)")
    .SetParameterList("ids", idArray)
    .List<User>();
```

### 场景 4：LIKE 查询

```csharp
// 高危：LIKE 拼接
var users = session.CreateQuery(
    "FROM User WHERE Name LIKE '%" + keyword + "%'").List<User>();

// 安全：参数化 LIKE
var users = session.CreateQuery("FROM User WHERE Name LIKE :keyword")
    .SetParameter("keyword", "%" + keyword + "%")
    .List<User>();
```

### 场景 5：NHibernate LINQ

```csharp
// 安全：NHibernate LINQ 自动参数化
var users = session.Query<User>()
    .Where(u => u.Name == name)
    .ToList();

// 安全：动态 LINQ
var query = session.Query<User>();
if (!string.IsNullOrEmpty(name))
    query = query.Where(u => u.Name.Contains(name));
var users = query.ToList();
```

---

## 检查清单

### HQL 检查

- [ ] 搜索所有 `CreateQuery()` 调用
- [ ] 检查 HQL 字符串是否有拼接
- [ ] 确认使用 `SetParameter()` 绑定参数
- [ ] ORDER BY 是否有白名单校验

### Native SQL 检查

- [ ] 搜索所有 `CreateSQLQuery()` 调用
- [ ] 检查 SQL 字符串是否有拼接
- [ ] 确认使用参数绑定

### ICriteria 检查

- [ ] 搜索 `Restrictions.SqlRestriction()` 使用
- [ ] 检查 `Projections.SqlProjection()` 使用
- [ ] 确认使用类型安全的 Criteria 方法

---

## 修复要求

1. **始终使用参数绑定**（`:paramName` 或 `?`）
2. **优先使用 ICriteria/QueryOver/LINQ**（类型安全）
3. **禁止 Native SQL 字符串拼接**
4. **ORDER BY 使用白名单**校验
5. **禁止使用 Restrictions.SqlRestriction() 无参数版本**
