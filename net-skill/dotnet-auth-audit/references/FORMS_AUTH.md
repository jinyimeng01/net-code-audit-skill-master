# Forms Authentication 审计

## 目录

- [框架识别](#框架识别)
- [配置分析](#配置分析)
- [常见漏洞模式](#常见漏洞模式)
- [审计检查清单](#审计检查清单)

---

## 框架识别

### 识别特征

| 特征类型 | 特征内容 |
|----------|----------|
| 配置文件 | `web.config` 中 `<authentication mode="Forms">` |
| 核心类 | `FormsAuthentication`, `FormsAuthenticationTicket` |
| Cookie 名称 | `.ASPXAUTH` (默认) |
| 适用 | ASP.NET WebForms / MVC (非 Core) |

---

## 配置分析

### web.config 配置

```xml
<authentication mode="Forms">
  <forms loginUrl="~/Account/Login"
         timeout="30"
         slidingExpiration="true"
         protection="All"
         requireSSL="false"
         cookieless="UseCookies"
         name=".ASPXAUTH"
         path="/"
         domain="" />
</authentication>

<authorization>
  <deny users="?" />  <!-- 拒绝匿名用户 -->
  <allow users="*" />  <!-- 允许所有已认证用户 -->
</authorization>
```

---

## 常见漏洞模式

### 1. requireSSL=false

```xml
<!-- 危险：Cookie 可通过 HTTP 传输 -->
<forms requireSSL="false" />

<!-- 安全：强制 SSL -->
<forms requireSSL="true" />
```

### 2. protection 配置不当

```xml
<!-- 危险：不加密/不验证 -->
<forms protection="None" />
<forms protection="Encryption" />  <!-- 无验证，可能被篡改 -->

<!-- 安全：完整保护 -->
<forms protection="All" />  <!-- 加密 + 验证 -->
```

### 3. 超时时间过长

```xml
<!-- 危险：超时 365 天 -->
<forms timeout="525600" />

<!-- 安全：合理超时 -->
<forms timeout="30" slidingExpiration="true" />
```

### 4. Cookieless 配置

```xml
<!-- 危险：Cookie 可嵌入 URL -->
<forms cookieless="UseUri" />

<!-- 安全：仅使用 Cookie -->
<forms cookieless="UseCookies" />
```

### 5. machineKey 硬编码/弱密钥

```xml
<!-- 危险：硬编码 machineKey -->
<machineKey validationKey="自动生成的弱密钥"
            decryptionKey="自动生成的弱密钥"
            validation="SHA1" />

<!-- 安全：使用强密钥 + 现代算法 -->
<machineKey validationKey="[256位随机密钥]"
            decryptionKey="[256位随机密钥]"
            validation="HMACSHA256"
            decryption="AES" />
```

### 6. authorization 顺序错误

```xml
<!-- 危险：allow 在前，deny 无效 -->
<authorization>
  <allow users="*" />
  <deny users="?" />  <!-- 永远不会执行 -->
</authorization>

<!-- 安全：deny 在前 -->
<authorization>
  <deny users="?" />
  <allow users="*" />
</authorization>
```

### 7. 位置特定授权

```xml
<!-- 检查点：特定路径的授权覆盖 -->
<location path="admin">
  <system.web>
    <authorization>
      <allow roles="Admin" />
      <deny users="*" />
    </authorization>
  </system.web>
</location>
```

---

## 审计检查清单

### Cookie 安全

- [ ] requireSSL 是否为 true
- [ ] protection 是否为 All
- [ ] cookieless 是否为 UseCookies
- [ ] 超时时间是否合理

### 密钥安全

- [ ] machineKey 是否硬编码
- [ ] validation 算法是否安全（不使用 MD5/SHA1）
- [ ] decryption 算法是否安全（使用 AES）
- [ ] 密钥是否足够长

### 授权配置

- [ ] authorization 规则顺序是否正确
- [ ] 是否有路径特定的授权覆盖
- [ ] 敏感路径是否正确配置

### 登录安全

- [ ] 登录页面是否使用 HTTPS
- [ ] 是否有防暴力破解机制
- [ ] 错误消息是否统一
