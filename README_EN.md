# .NET Offensive Security & Code Audit Skill Suite

[![License](https://img.shields.io/badge/license-Mulan%20PSL%20v2-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-18-green.svg)](#core-capabilities)
[![Coverage](https://img.shields.io/badge/coverage-.NET%20Full%20Stack-orange.svg)](#support-matrix)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success.svg)](.github/workflows/validate.yml)
[![中文](https://img.shields.io/badge/README-中文-blue.svg)](README.md)

> A comprehensive AI Agent security audit skill suite for the entire .NET ecosystem, covering the full attack surface from legacy ASP.NET WebForms to modern ASP.NET Core 9.x, Blazor, SignalR, and Minimal API.

## Table of Contents

- [Scope](#scope)
- [Security Boundary](#security-boundary)
- [Core Capabilities](#core-capabilities)
- [Quick Start](#quick-start)
  - [Environment Setup](#environment-setup)
  - [Scenario 1: Full Source Code Audit](#scenario-1-full-source-code-audit)
  - [Scenario 2: Binary-Only Audit](#scenario-2-binary-only-audit)
  - [Scenario 3: Single Vulnerability Deep Dive](#scenario-3-single-vulnerability-deep-dive)
- [Attack Surface Indexer](#attack-surface-indexer)
- [Architecture Overview](#architecture-overview)
- [Detailed Execution Flow](#detailed-execution-flow)
- [Output Standards](#output-standards)
- [Support Matrix](#support-matrix)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [License](#license)

## Scope

| Scenario | Description |
|----------|-------------|
| **ASP.NET Full Stack** | WebForms, MVC 5, Web API 2, ASP.NET Core (2.x–9.x), WCF, IIS deployment packages |
| **Source Code Audit** | Complete `.csproj` / `.sln` projects, published site directories |
| **Binary-Only Audit** | Only `bin/` directories, `.dll` / `.exe` files requiring dnSpy decompilation |
| **Modern .NET** | Minimal API, Blazor Server / WASM, SignalR, Source Generator |
| **Audit Modes** | Authorized source code audits, defensive hardening reviews, red team lab validations |

## Security Boundary

- **Safe-by-default**: Reports output only safe verification evidence (DNS callback, error echo, filename reflection, harmless command output) and remediation suggestions.
- **Red Team Lab Boundary**: Content involving command execution, deserialization, SSRF, credential forgery, and ViewState / machineKey must comply with [REDTEAM_LAB_BOUNDARY.md](net-skill/shared/REDTEAM_LAB_BOUNDARY.md).
- **No Default Weaponization**: Do not generate weaponized payloads, full keys, tokens, connection strings, or forgeable identity materials for unauthorized targets by default.

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

> [中文 README](README.md)

---

## Quick Start

### Environment Setup

1. **Python 3.10+**
   ```powershell
   python --version
   ```

2. **dnSpy (required for binary audits)**
   ```powershell
   # Auto-download
   .\tools\setup-dnspy.ps1

   # Or manual: https://github.com/dnSpy/dnSpy/releases
   ```

3. **Copy `net-skill/` into the audit project root or agent workspace**

### Scenario 1: Full Source Code Audit

For projects with complete `.cs` / `.csproj` / `.sln` source code.

**Step 1: Run Attack Surface Indexer**
```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py `
  .\target-project `
  -o .\audit-output\surface
```

Outputs:
- `audit-output/surface/surface_index.json` — Machine-readable attack surface
- `audit-output/surface/attack_surface_matrix.md` — Human review matrix

**Step 2: Execute Full Audit via Master Skill**

```text
Use the net-skill dotnet-offsec-audit and dotnet-audit-pipeline in the current directory
to audit the current .NET project within the authorized scope. Output directory: ./audit-output.
Generate only one quality_report.md, using safe verification by default. Mask all secrets and tokens.
```

**Step 3: Review Final Report**
```text
audit-output/quality_report.md
```

### Scenario 2: Binary-Only Audit

For projects with only `bin/` directories or `.dll` / `.exe` files.

**Step 1: Decompile**
```powershell
# Using dnSpy downloaded by setup script
dnSpy\dnSpy.Console.exe -o audit-output\decompiled -r target-project\bin\

# Verify decompilation
Test-Path audit-output\decompiled\*.cs  # Should be True
```

**Step 2: Index Decompiled Code**
```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py `
  .\audit-output\decompiled `
  -o .\audit-output\surface
```

**Step 3: Audit with Decompilation Source Annotated**

```text
Use the net-skill dotnet-offsec-audit and dotnet-audit-pipeline to audit the decompiled code
(source: DLLs in target-project/bin/). Output directory ./audit-output, final report quality_report.md.
All evidence from decompiled code must annotate the original DLL name and decompilation path.
```

### Scenario 3: Single Vulnerability Deep Dive

For scenarios where the vulnerability type is already known (e.g., only audit SQL injection or deserialization).

```text
Use the net-skill dotnet-sql-audit in the current directory to audit all ADO.NET / Entity Framework /
Dapper SQL injection risks in the current project. Output to ./audit-output/sql-specialized/.
```

---

## Attack Surface Indexer

```powershell
python net-skill\dotnet-offsec-audit\scripts\collect_dotnet_surface.py <source_path> -o <output_path>\surface
```

**Output Files:**

| File | Purpose |
|------|---------|
| `surface_index.json` | Machine-readable index; each finding includes category, rule_id, severity_hint, recommended_skill, confidence, evidence_kind, file, line, snippet |
| `attack_surface_matrix.md` | Human review matrix sorted by risk severity |

**Coverage:**

- **Routes**: Controller, Page, Handler, WCF Operation, Minimal API MapGet/MapPost
- **Auth**: Authorize, AllowAnonymous, FormsAuth, JWT, OAuth
- **Sinks**: BinaryFormatter, TypeNameHandling, Process.Start, HttpClient, machineKey, File.ReadAllText, IJSRuntime, MarkupString, Hub, etc.
- **Config**: debug=true, customErrors=Off, Swagger exposure, ELMAH, Hangfire

---

## Architecture Overview

```text
net-skill/
├── dotnet-offsec-audit/              # Master: auth → decompile → index → dispatch → report
│   └── scripts/collect_dotnet_surface.py
├── dotnet-audit-pipeline/            # Pipeline: 6-phase execution + quality gates
├── dotnet-route-mapper/              # Routes: HTTP / WCF / WebForms / Minimal API
├── dotnet-auth-audit/                # Auth: FormsAuth / Identity / JWT / OAuth / IDOR
├── dotnet-route-tracer/              # Tracing: entry → sink reachability
├── dotnet-vuln-scanner/              # Components: NuGet / DLL / CVE / GHSA
├── dotnet-sql-audit/                 # SQLi: ADO.NET / EF / Dapper / NHibernate
├── dotnet-xxe-audit/                 # XXE/XML: XmlDocument / XmlReader / XDocument / XSLT
├── dotnet-file-upload-audit/         # Upload: IFormFile / SaveAs / bypass
├── dotnet-file-read-audit/           # Read: FileStream / Path.Combine / traversal
├── dotnet-deserialization-audit/     # Deser: 11 formatters / ViewState / Remoting
├── dotnet-command-exec-audit/        # Command: Process.Start / PowerShell / CodeDom / Roslyn
├── dotnet-ssrf-audit/                # SSRF: HttpClient / WebRequest / DNS Rebind / Metadata
├── dotnet-config-secrets-audit/      # Secrets: machineKey / JWT / IIS exposure
├── dotnet-web-risk-audit/            # Web: XSS / CSRF / CORS / Host Header / Open Redirect
├── dotnet-minimal-api-audit/         # Minimal API: EndpointFilter / Source Gen / OpenAPI
├── dotnet-blazor-audit/              # Blazor: JS Interop / MarkupString / Circuit / XSS
├── dotnet-signalr-audit/             # SignalR: Hub / Group / Broadcast / WebSocket
└── shared/                           # Shared standards
    ├── DOTNET_ATTACK_SURFACE_TAXONOMY.md
    ├── DOTNET_DECOMPILE_STRATEGY.md
    ├── DOTNET_OUTPUT_STANDARD.md
    ├── REDTEAM_LAB_BOUNDARY.md
    └── SEVERITY_RATING.md
```

---

## Detailed Execution Flow

```text
Phase 0: Authorization Boundary Confirmation
  ├── Confirm audit authorization scope and target system ownership
  ├── Identify project type (WebForms / MVC / Core / WCF / Minimal API / Blazor)
  └── If source incomplete → dnSpy decompile → verify decompiled/ contains .cs files

Phase 1: Attack Surface Indexing
  ├── collect_dotnet_surface.py scans source / decompiled code
  ├── Generates surface_index.json (machine-readable)
  └── Generates attack_surface_matrix.md (human review)

Phase 2: Base Audits (Parallel)
  ├── dotnet-route-mapper: full routes, parameters, Burp request templates
  ├── dotnet-auth-audit: auth framework, route-auth mapping, bypass clues
  └── dotnet-vuln-scanner: NuGet/DLL component vulnerabilities & trigger conditions

Phase 3: Cross-Filtering & Prioritization
  ├── Unauthenticated/weak-auth routes + high-risk sinks cross-match
  ├── Component vulnerability trigger entry confirmation
  └── Configuration secret amplification chain identification

Phase 4: Call-Chain Tracing
  └── dotnet-route-tracer: parameter propagation and reachability proof from entry to sink

Phase 5: Specialized Deep Audits (dispatched by surface_index)
  ├── SQL / XXE / File Upload / File Read
  ├── Deserialization / Command Execution / SSRF
  ├── Configuration Secrets / Web Comprehensive Risks
  └── Minimal API / Blazor / SignalR (Modern .NET)

Phase 6: Quality Check & Report Output
  ├── Check quality_report.md completeness (no TODO, no omissions, no bare keys)
  ├── Verify security output (no default weaponized payloads)
  └── Output single final report: quality_report.md
```

---

## Output Standards

**Final Deliverable**: `{output_path}/quality_report.md`

**Must Include:**
- Audit overview, authorization boundary, framework identification, decompilation scope
- Attack surface summary, routing & auth status, P0/P1 high-risk targets
- Per vulnerability: entry route, parameter source, call chain, sink, code evidence, evidence tag, risk rating, impact, remediation
- Safe verification evidence for each high-risk issue, or explanation why impossible
- 11-class formatter coverage status
- Desensitized secret display and key rotation recommendations
- Quality coverage, raw source header integrity, security output check

**Forbidden:**
- Unreplaced `TODO`, `...`, `[Fill in]`
- Omitted outputs ("same as above", "omitted", "refer to previous")
- Full keys, tokens, connection strings
- Default output of weaponized payloads for unauthorized targets

---

## Support Matrix

| Framework | Status | Notes |
|-----------|--------|-------|
| ASP.NET WebForms | Full | Page, Control, Handler, ASMX fully covered |
| ASP.NET MVC 5 | Full | Attribute routing, conventional routing, Filter |
| ASP.NET Web API 2 | Full | ApiController, OData, MediaTypeFormatter |
| ASP.NET Core (2.x–9.x) | Full | MVC, Razor Pages, Middleware, Filter Pipeline |
| WCF | Full | ServiceContract, OperationContract, Binding |
| IIS Deployment Packages | Full | bin/, web.config, deployment directory structure |
| Blazor Server / WASM | v2.0 | Circuit, JS Interop, component rendering |
| SignalR | v2.0 | Hub, HubContext, Group, Message Broadcast |
| Minimal API | v2.0 | MapGet/MapPost, EndpointFilter, Source Generator |
| gRPC (.NET) | Partial | Proto, Service basic identification |

---

## Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| `collect_dotnet_surface.py` error | Python version too old | Upgrade to Python 3.10+ |
| dnSpy decompilation fails | Target is .NET Native / AOT | Log failed DLL, continue auditing other parts |
| `TODO` in quality_report.md | Pipeline phase incomplete | Re-run Phase 6 quality check |
| No `.cs` after decompilation | dnSpy path wrong or Native DLL | Check dnSpy installation path and target framework version |
| Skill loads but no output | Agent did not locate net-skill directory | Ensure net-skill/ is in working directory and explicitly reference it in prompt |

---

## Documentation

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Agent project core configuration and usage guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Skill addition standards, contribution workflow, maintenance sync rules |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [net-skill/README.md](net-skill/README.md) | Internal skill index and reference quick lookup |

## License

Licensed under [Mulan PSL v2](LICENSE).
