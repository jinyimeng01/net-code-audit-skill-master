# .NET Offensive Security & Code Audit Skill Suite

[![License](https://img.shields.io/badge/license-Mulan%20PSL%20v2-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-18-green.svg)](#core-capabilities)
[![Coverage](https://img.shields.io/badge/coverage-.NET%20Full%20Stack-orange.svg)](#support-matrix)
[![中文](https://img.shields.io/badge/README-中文-blue.svg)](README.md)

> A comprehensive AI Agent security audit skill suite for the entire .NET ecosystem, covering the full attack surface from legacy ASP.NET WebForms to modern ASP.NET Core 9.x, Blazor, SignalR, and Minimal API.

## Scope

- **Frameworks**: ASP.NET WebForms, MVC 5, Web API 2, ASP.NET Core (2.x–9.x), WCF, IIS deployment packages
- **Scenarios**: Authorized source code audits, binary-only audits (dnSpy decompilation), defensive hardening reviews, red team lab validations
- **Deliverable**: A single, reviewable, safe-by-default `quality_report.md`

## Security Boundary

- Reports output only safe verification evidence and remediation suggestions by default.
- Content involving command execution, deserialization, SSRF, credential forgery, and ViewState/machineKey must comply with [REDTEAM_LAB_BOUNDARY.md](net-skill/shared/REDTEAM_LAB_BOUNDARY.md).
- Do not generate weaponized payloads, full keys, or tokens for unauthorized targets by default.

## Core Capabilities

| Capability | Coverage | Entry Skill |
|:-----|:---------|:----------|
| Master Orchestrator | Authorization boundaries, decompilation, attack surface indexing, specialized dispatch, final report | [dotnet-offsec-audit](net-skill/dotnet-offsec-audit/SKILL.md) |
| Full Pipeline | Agent phased execution, quality gates, single `quality_report.md` | [dotnet-audit-pipeline](net-skill/dotnet-audit-pipeline/SKILL.md) |
| Routing & Parameters | MVC / Web API / Core / WebForms / WCF / Minimal API routes, parameter sources, request templates | [dotnet-route-mapper](net-skill/dotnet-route-mapper/SKILL.md) |
| Authentication & Authorization | FormsAuth, Identity, JWT, OAuth/OIDC, Windows Auth, Membership, IDOR | [dotnet-auth-audit](net-skill/dotnet-auth-audit/SKILL.md) |
| Call-Chain Tracing | From Controller / Page / Handler / WCF to SQL, file, XML, command, etc. | [dotnet-route-tracer](net-skill/dotnet-route-tracer/SKILL.md) |
| Component Vulnerabilities | NuGet, DLL, configuration dependencies and CVE/GHSA trigger conditions | [dotnet-vuln-scanner](net-skill/dotnet-vuln-scanner/SKILL.md) |
| SQL Injection | ADO.NET, EF, Dapper, NHibernate, dynamic SQL | [dotnet-sql-audit](net-skill/dotnet-sql-audit/SKILL.md) |
| XXE / XML | XmlDocument, XmlReader, XDocument, XmlSerializer, XSLT, SOAP / OOXML / SVG | [dotnet-xxe-audit](net-skill/dotnet-xxe-audit/SKILL.md) |
| File Upload | HttpPostedFile, IFormFile, SaveAs, CopyToAsync, path and type validation | [dotnet-file-upload-audit](net-skill/dotnet-file-upload-audit/SKILL.md) |
| File Read | File.ReadAllText, FileStream, StreamReader, Response.WriteFile, path traversal | [dotnet-file-read-audit](net-skill/dotnet-file-read-audit/SKILL.md) |
| Deserialization | 11 formatters, Json.NET TypeNameHandling, ViewState / machineKey, Remoting | [dotnet-deserialization-audit](net-skill/dotnet-deserialization-audit/SKILL.md) |
| Command Execution | Process.Start, PowerShell, CodeDom, Roslyn, XAML / XSLT, Assembly.Load | [dotnet-command-exec-audit](net-skill/dotnet-command-exec-audit/SKILL.md) |
| SSRF | HttpClient, WebRequest, URL parser, redirect, DNS rebinding, metadata | [dotnet-ssrf-audit](net-skill/dotnet-ssrf-audit/SKILL.md) |
| Configuration Secrets | machineKey, connection strings, JWT / OAuth / SAML secrets, certs, IIS / Swagger / ELMAH | [dotnet-config-secrets-audit](net-skill/dotnet-config-secrets-audit/SKILL.md) |
| Web Risk | XSS, CSRF / SameSite, CORS, Host Header, Open Redirect, IDOR / BOLA / BFLA | [dotnet-web-risk-audit](net-skill/dotnet-web-risk-audit/SKILL.md) |
| Minimal API | MapGet / MapPost, EndpointFilter, Source Generator, OpenAPI | [dotnet-minimal-api-audit](net-skill/dotnet-minimal-api-audit/SKILL.md) |
| Blazor | IJSRuntime, MarkupString, Circuit, AuthenticationStateProvider | [dotnet-blazor-audit](net-skill/dotnet-blazor-audit/SKILL.md) |
| SignalR | Hub, HubContext, Group, Message Broadcast, WebSocket | [dotnet-signalr-audit](net-skill/dotnet-signalr-audit/SKILL.md) |

Full index: [net-skill/README.md](net-skill/README.md).

> 📖 [中文 README](README.md)

## Quick Start

### Recommended Execution Flow

```text
Phase 0: Authorization boundary + source identification + dnSpy decompilation
Phase 1: collect_dotnet_surface.py → surface_index.json + attack_surface_matrix.md
Phase 2: route-mapper + auth-audit + vuln-scanner
Phase 3: High-risk route grading + specialized attack surface aggregation
Phase 4: route-tracer call-chain tracing
Phase 5: SQL / XXE / File / Deserialization / Command Exec / SSRF / Secrets / Web / Minimal API / Blazor / SignalR
Phase 6: Quality check → single final report quality_report.md
```

### Attack Surface Indexer

```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py <source_path> -o <output_path>\surface
```

Outputs `surface_index.json` (machine-readable) and `attack_surface_matrix.md` (human review matrix). Each finding includes `category`, `rule_id`, `recommended_skill`, `confidence`, and `evidence_kind`.

### Prompt Template

```text
Use the net-skill dotnet-offsec-audit and dotnet-audit-pipeline in the current directory
to audit the current .NET project within the authorized scope. If the source is incomplete,
decompile first with output directory ./audit-output. Generate only one quality_report.md,
using safe verification by default. Mask all secrets and tokens.
```

## Architecture

```text
net-skill/
├── dotnet-offsec-audit/          # Master orchestrator
├── dotnet-audit-pipeline/        # Pipeline + quality gates
├── dotnet-route-mapper/          # Route enumeration
├── dotnet-auth-audit/            # Auth audit
├── dotnet-route-tracer/          # Call-chain tracing
├── dotnet-vuln-scanner/          # Component vulnerability scan
├── dotnet-sql-audit/             # SQL injection
├── dotnet-xxe-audit/             # XXE / XML
├── dotnet-file-upload-audit/     # File upload
├── dotnet-file-read-audit/       # File read / path traversal
├── dotnet-deserialization-audit/ # Deserialization (11 formatters)
├── dotnet-command-exec-audit/    # Command execution
├── dotnet-ssrf-audit/            # SSRF
├── dotnet-config-secrets-audit/  # Configuration secrets
├── dotnet-web-risk-audit/        # Web comprehensive risks
├── dotnet-minimal-api-audit/     # Minimal API
├── dotnet-blazor-audit/          # Blazor
├── dotnet-signalr-audit/         # SignalR
└── shared/                       # Shared standards & taxonomy
```

## Support Matrix

| Framework | Status |
|-----------|--------|
| ASP.NET WebForms | ✅ Full |
| ASP.NET MVC 5 | ✅ Full |
| ASP.NET Web API 2 | ✅ Full |
| ASP.NET Core (2.x–9.x) | ✅ Full |
| WCF | ✅ Full |
| IIS Deployment Packages | ✅ Full |
| Blazor Server / WASM | ✅ v2.0 |
| SignalR | ✅ v2.0 |
| Minimal API | ✅ v2.0 |
| gRPC (.NET) | 🚧 Partial |

## Toolchain

| Script | Purpose |
|------|------|
| `net-skill/dotnet-offsec-audit/scripts/collect_dotnet_surface.py` | Attack surface indexer |
| `net-skill/dotnet-vuln-scanner/scripts/scan_dotnet_dependencies.py` | Dependency CVE scanner |
| `tools/setup-dnspy.ps1` | dnSpy auto-download & setup |

## Quality & Standards

- **Final Report**: `{output_path}/quality_report.md` — unique, complete, reviewable
- **Safe Output**: Safe verification by default, secrets redacted, weaponized payloads limited to lab scenarios only
- **CI Validation**: GitHub Actions auto-validates skill structure, Python syntax, and frontmatter integrity
- **Maintenance Sync**: Skill changes require synchronized updates to references, taxonomy, scripts, README, and pipeline templates

## Documentation

- [AGENTS.md](AGENTS.md) — Agent usage guide
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) — Version history
- [LICENSE](LICENSE) — Mulan PSL v2

## License

Licensed under [Mulan PSL v2](LICENSE).
