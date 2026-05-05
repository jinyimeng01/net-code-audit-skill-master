# Agent Guide: net-code-audit-skill-master

> **Purpose**: A world-class, comprehensive .NET offensive security and code audit skill suite for AI agents.
> **Language**: Chinese (primary) / English (secondary)
> **License**: Mulan PSL v2

## Project Overview

`net-skill` is a collection of specialized security audit skills targeting the entire .NET ecosystem:

- **ASP.NET WebForms, MVC, Web API, ASP.NET Core, WCF, IIS deployment packages**
- **Source code audits, binary-only audits, dnSpy decompiled code audits**
- **Authorized penetration testing, red team lab validation, defensive hardening review**

## Architecture

```
net-skill/
├── dotnet-offsec-audit/          # Master orchestrator
├── dotnet-audit-pipeline/        # Agent team pipeline
├── dotnet-route-mapper/          # Route & parameter enumeration
├── dotnet-auth-audit/            # Authentication & authorization audit
├── dotnet-route-tracer/          # Call-chain tracing (entry → sink)
├── dotnet-vuln-scanner/          # NuGet/DLL dependency vulnerability scan
├── dotnet-sql-audit/             # SQL injection audit
├── dotnet-xxe-audit/             # XXE / XML parser audit
├── dotnet-file-upload-audit/     # File upload audit
├── dotnet-file-read-audit/       # File read / path traversal audit
├── dotnet-deserialization-audit/ # 11-class formatter deserialization audit
├── dotnet-command-exec-audit/    # Command & dynamic code execution audit
├── dotnet-ssrf-audit/            # SSRF / outbound request audit
├── dotnet-config-secrets-audit/  # Configuration & secret leakage audit
├── dotnet-web-risk-audit/        # XSS, CSRF, CORS, Host Header, Open Redirect, IDOR
├── dotnet-minimal-api-audit/     # ASP.NET Core Minimal API audit (NEW v2.0)
├── dotnet-blazor-audit/          # Blazor Server / WASM audit (NEW v2.0)
├── dotnet-signalr-audit/         # SignalR Hub & message audit (NEW v2.0)
└── shared/                       # Common standards & taxonomies
```

## How to Use

### Method 1: Master Orchestrator (Recommended)

Load `net-skill/dotnet-offsec-audit/SKILL.md` as the entry point. It will:

1. Confirm authorization boundaries.
2. Decompile with dnSpy if only binaries are available.
3. Run `collect_dotnet_surface.py` to build the attack surface index.
4. Dispatch specialized skills based on sink types.
5. Produce a single `quality_report.md`.

**Prompt template:**

```text
Use the net-skill in the current directory to perform an authorized code audit
on the current .NET project. If the source is incomplete, decompile first.
Output directory: ./audit-output. Final deliverable: quality_report.md.
Use safe verification by default; mask all secrets and tokens.
```

### Method 2: Pipeline Mode

Load `net-skill/dotnet-audit-pipeline/SKILL.md` for multi-agent phased execution with quality gates.

### Method 3: Single Skill

Load any individual skill under `net-skill/<skill-name>/SKILL.md` when the sink type is already known.

## Output Standards

- **Final report**: `{output_path}/quality_report.md` (mandatory, unique)
- **Machine-readable index**: `surface_index.json`
- **Safe verification by default**: DNS callbacks, error echoes, file name reflections, harmless commands.
- **Weaponized payloads**: Allowed **only** in the "Authorized Lab Validation" section, never by default.
- **Secret masking**: Machine keys, tokens, connection strings must be redacted.

## Red Team Lab Boundary

When dealing with deserialization, command execution, SSRF, or credential forgery:

- Read `net-skill/shared/REDTEAM_LAB_BOUNDARY.md` **before** generating any exploit chain.
- Do not output complete weaponized payloads, full keys, or forgeable identity materials for unauthorized targets.

## Key Scripts

| Script | Purpose |
|--------|---------|
| `net-skill/dotnet-offsec-audit/scripts/collect_dotnet_surface.py` | Attack surface indexer |
| `net-skill/dotnet-vuln-scanner/scripts/scan_dotnet_dependencies.py` | Dependency CVE scanner |
| `tools/setup-dnspy.ps1` | Download and configure dnSpy |

## Maintenance Rules

When adding or modifying a skill, synchronize **all** of the following:

1. `net-skill/<skill-name>/SKILL.md`
2. Corresponding `references/` documents
3. `shared/DOTNET_ATTACK_SURFACE_TAXONOMY.md`
4. `dotnet-offsec-audit/scripts/collect_dotnet_surface.py` rules
5. `dotnet-audit-pipeline/SKILL.md` and quality templates
6. Root `README.md` and `net-skill/README.md`

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

## Contact & Contribution

- See `CONTRIBUTING.md` for contribution guidelines.
- See `CHANGELOG.md` for version history.
- Issues and PRs welcome at `https://github.com/jinyimeng01/net-code-audit-skill-master`
