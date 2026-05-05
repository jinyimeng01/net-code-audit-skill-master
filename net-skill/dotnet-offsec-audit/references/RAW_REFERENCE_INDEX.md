# Raw Hack-Skills Reference Index

这些文件来自本地 `hack-skills`，只用于追溯和深查。默认优先读取各专项结构化 reference。

## Archived Skill Families

- [deserialization-insecure](raw/hack-skills/deserialization-insecure/SKILL.md)
- [cmdi-command-injection](raw/hack-skills/cmdi-command-injection/SKILL.md)
- [ssrf-server-side-request-forgery](raw/hack-skills/ssrf-server-side-request-forgery/SKILL.md)
- [xxe-xml-external-entity](raw/hack-skills/xxe-xml-external-entity/SKILL.md)
- [path-traversal-lfi](raw/hack-skills/path-traversal-lfi/SKILL.md)
- [upload-insecure-files](raw/hack-skills/upload-insecure-files/SKILL.md)
- [xss-cross-site-scripting](raw/hack-skills/xss-cross-site-scripting/SKILL.md)
- [csrf-cross-site-request-forgery](raw/hack-skills/csrf-cross-site-request-forgery/SKILL.md)
- [cors-cross-origin-misconfiguration](raw/hack-skills/cors-cross-origin-misconfiguration/SKILL.md)
- [idor-broken-object-authorization](raw/hack-skills/idor-broken-object-authorization/SKILL.md)
- [http-host-header-attacks](raw/hack-skills/http-host-header-attacks/SKILL.md)
- [open-redirect](raw/hack-skills/open-redirect/SKILL.md)
- [api-auth-and-jwt-abuse](raw/hack-skills/api-auth-and-jwt-abuse/SKILL.md)
- [oauth-oidc-misconfiguration](raw/hack-skills/oauth-oidc-misconfiguration/SKILL.md)
- [saml-sso-assertion-attacks](raw/hack-skills/saml-sso-assertion-attacks/SKILL.md)
- [request-smuggling](raw/hack-skills/request-smuggling/SKILL.md)
- [web-cache-deception](raw/hack-skills/web-cache-deception/SKILL.md)
- [waf-bypass-techniques](raw/hack-skills/waf-bypass-techniques/SKILL.md)

## 使用规则

- 只有结构化 reference 不足以判断绕过、链式影响、产品特性时再读取 raw。
- 不把 raw 中的攻击样例原样输出到最终报告；先转换成授权实验室验证建议、检测规则或修复建议。
