#!/usr/bin/env python3
"""Collect a lightweight .NET attack-surface index from source or decompiled code."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


TEXT_EXTENSIONS = {
    ".cs",
    ".vb",
    ".fs",
    ".cshtml",
    ".vbhtml",
    ".aspx",
    ".ascx",
    ".ashx",
    ".asmx",
    ".svc",
    ".config",
    ".xml",
    ".json",
    ".csproj",
    ".vbproj",
    ".fsproj",
    ".props",
    ".targets",
    ".yml",
    ".yaml",
}

EXCLUDED_DIRS = {
    ".git",
    ".vs",
    "node_modules",
    "packages",
    "bin",
    "obj",
    ".nuget",
    ".idea",
    ".vscode",
}


def rule(
    category: str,
    rule_id: str,
    severity_hint: str,
    recommended_skill: str,
    confidence: str,
    evidence_kind: str,
    pattern: str,
) -> dict:
    return {
        "category": category,
        "rule_id": rule_id,
        "severity_hint": severity_hint,
        "recommended_skill": recommended_skill,
        "confidence": confidence,
        "evidence_kind": evidence_kind,
        "regex": re.compile(pattern, re.IGNORECASE),
    }


RULES = [
    rule(
        "route",
        "route-aspnet-core",
        "Info",
        "dotnet-route-mapper",
        "High",
        "route-declaration",
        r"\[(HttpGet|HttpPost|HttpPut|HttpDelete|HttpPatch|Route|ApiController)\b|Map(Get|Post|Put|Delete|Patch)\s*\(",
    ),
    rule(
        "route",
        "route-webforms-wcf",
        "Info",
        "dotnet-route-mapper",
        "High",
        "entrypoint",
        r"\b(Page_Load|IHttpHandler|WebMethod|OperationContract|ServiceContract)\b",
    ),
    rule(
        "auth",
        "auth-attributes",
        "Medium",
        "dotnet-auth-audit",
        "Medium",
        "auth-metadata",
        r"\[(Authorize|AllowAnonymous|ValidateAntiForgeryToken|IgnoreAntiforgeryToken)\b|AddAuthorization|UseAuthentication|UseAuthorization",
    ),
    rule(
        "auth",
        "auth-token-validation",
        "High",
        "dotnet-auth-audit",
        "High",
        "auth-config",
        r"AddJwtBearer|TokenValidationParameters|ValidateIssuer|ValidateAudience|ValidateLifetime|IssuerSigningKey|IssuerSigningKeys",
    ),
    rule(
        "auth",
        "auth-windows-identity",
        "High",
        "dotnet-auth-audit",
        "Medium",
        "identity-object",
        r"\b(WindowsIdentity|WindowsPrincipal|ClaimsIdentity|ClaimsPrincipal|GenericIdentity)\b",
    ),
    rule(
        "sql",
        "sql-exec",
        "High",
        "dotnet-sql-audit",
        "High",
        "sink",
        r"\b(SqlCommand|OleDbCommand|OdbcCommand|ExecuteReader|ExecuteNonQuery|ExecuteScalar|FromSqlRaw|ExecuteSqlRaw|SqlQuery|ExecuteSqlCommand|Query<|Execute\()\b",
    ),
    rule(
        "sql",
        "sql-dynamic",
        "High",
        "dotnet-sql-audit",
        "Medium",
        "dynamic-string",
        r"(SELECT|UPDATE|DELETE|INSERT)\s+.*(\+|\{0\}|\$\"|StringBuilder|string\.Format)",
    ),
    rule(
        "xxe",
        "xml-parser",
        "High",
        "dotnet-xxe-audit",
        "Medium",
        "parser",
        r"\b(XmlDocument|XmlReader|XDocument|XPathDocument|XmlSerializer|DataSet\.ReadXml|XslCompiledTransform)\b",
    ),
    rule(
        "xxe",
        "xxe-danger",
        "High",
        "dotnet-xxe-audit",
        "High",
        "dangerous-config",
        r"DtdProcessing\s*=\s*DtdProcessing\.Parse|XmlResolver\s*=\s*new\s+XmlUrlResolver|XmlResolver\s*=\s*[^n]",
    ),
    rule(
        "file-read",
        "file-read",
        "High",
        "dotnet-file-read-audit",
        "High",
        "sink",
        r"\b(File\.ReadAllText|File\.ReadAllBytes|File\.OpenRead|FileStream|StreamReader|Response\.WriteFile|PhysicalFile|TransmitFile)\b",
    ),
    rule(
        "file-read",
        "path-combine",
        "Medium",
        "dotnet-file-read-audit",
        "Medium",
        "path-construction",
        r"\b(Path\.Combine|Server\.MapPath|IWebHostEnvironment\.WebRootPath|ContentRootPath)\b",
    ),
    rule(
        "file-upload",
        "file-upload",
        "High",
        "dotnet-file-upload-audit",
        "High",
        "upload-entrypoint",
        r"\b(IFormFile|HttpPostedFile|HttpPostedFileBase|Request\.Files|SaveAs|CopyToAsync|RadAsyncUpload|ASPxUploadControl)\b",
    ),
    rule(
        "deserialization",
        "deser-formatter",
        "Critical",
        "dotnet-deserialization-audit",
        "High",
        "formatter-sink",
        r"\b(BinaryFormatter|SoapFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|DataContractSerializer)\b",
    ),
    rule(
        "deserialization",
        "deser-method-response",
        "Critical",
        "dotnet-deserialization-audit",
        "High",
        "remoting-sink",
        r"\b(UnsafeDeserializeMethodResponse|DeserializeMethodResponse|DeserializeMessage|IMethodCallMessage|IMethodReturnMessage)\b",
    ),
    rule(
        "deserialization",
        "deser-jsonnet",
        "Critical",
        "dotnet-deserialization-audit",
        "High",
        "type-control",
        r"TypeNameHandling\s*=\s*TypeNameHandling\.(?!None\b)|JsonConvert\.DeserializeObject|JsonSerializerSettings|ISerializationBinder|SerializationBinder",
    ),
    rule(
        "deserialization",
        "deser-javascriptserializer",
        "Critical",
        "dotnet-deserialization-audit",
        "High",
        "type-resolver",
        r"\b(JavaScriptSerializer|SimpleTypeResolver|TypeResolver|DeserializeObject)\b",
    ),
    rule(
        "deserialization",
        "deser-remoting",
        "Critical",
        "dotnet-deserialization-audit",
        "High",
        "remoting-config",
        r"TypeFilterLevel\.Full|RemotingConfiguration|HttpServerChannel|TcpServerChannel|BinaryServerFormatterSinkProvider|SoapServerFormatterSinkProvider",
    ),
    rule(
        "deserialization",
        "deser-viewstate",
        "Critical",
        "dotnet-deserialization-audit",
        "High",
        "viewstate-config",
        r"__VIEWSTATE|ViewStateUserKey|enableViewStateMac|ViewStateEncryptionMode|LosFormatter|ObjectStateFormatter|EventValidation",
    ),
    rule(
        "deserialization",
        "deser-gadget-types",
        "High",
        "dotnet-deserialization-audit",
        "Medium",
        "gadget-indicator",
        r"\b(PSObject|MulticastDelegate|ObjectDataProvider|ExpandedWrapper|ClaimsIdentity|WindowsIdentity|SortedSet|ActivitySurrogateSelector)\b",
    ),
    rule(
        "deserialization",
        "deser-dynamic-type",
        "High",
        "dotnet-deserialization-audit",
        "Medium",
        "type-control",
        r"\b(Type\.GetType|Activator\.CreateInstance|FormatterServices|SerializationInfo|ISerializable)\b",
    ),
    rule(
        "command-exec",
        "cmd-process",
        "Critical",
        "dotnet-command-exec-audit",
        "High",
        "process-sink",
        r"\b(Process\.Start|ProcessStartInfo|UseShellExecute|CreateNoWindow|WorkingDirectory)\b",
    ),
    rule(
        "command-exec",
        "cmd-interpreter",
        "Critical",
        "dotnet-command-exec-audit",
        "High",
        "interpreter",
        r"\b(cmd\.exe|powershell|pwsh|bash|wscript|cscript|mshta|rundll32|regsvr32|InstallUtil|MSBuild|csc\.exe)\b",
    ),
    rule(
        "command-exec",
        "cmd-arguments",
        "High",
        "dotnet-command-exec-audit",
        "Medium",
        "argument-construction",
        r"\b(Arguments|ArgumentList|StartInfo|RedirectStandardOutput|RedirectStandardError)\b",
    ),
    rule(
        "command-exec",
        "dynamic-code",
        "Critical",
        "dotnet-command-exec-audit",
        "High",
        "dynamic-code",
        r"\b(CodeDomProvider|CSharpScript|VBScript|JScript|Assembly\.Load|Assembly\.LoadFrom|AssemblyLoadContext|InvokeMember|MethodInfo\.Invoke)\b",
    ),
    rule(
        "command-exec",
        "xaml-xslt-code",
        "Critical",
        "dotnet-command-exec-audit",
        "High",
        "dynamic-parser",
        r"\b(XamlReader\.Parse|XamlServices\.Load|XslCompiledTransform|XsltSettings|EnableScript|msxsl:script)\b",
    ),
    rule(
        "ssrf",
        "outbound-http",
        "High",
        "dotnet-ssrf-audit",
        "High",
        "outbound-request",
        r"\b(HttpClient|WebClient|HttpWebRequest|WebRequest\.Create|DownloadString|DownloadFile|OpenRead|GetAsync|PostAsync|SendAsync|GrpcChannel\.ForAddress)\b",
    ),
    rule(
        "ssrf",
        "ssrf-redirects",
        "High",
        "dotnet-ssrf-audit",
        "Medium",
        "redirect-config",
        r"\b(AllowAutoRedirect|MaxAutomaticRedirections|AutoRedirect|RedirectUri|Location)\b",
    ),
    rule(
        "ssrf",
        "ssrf-url-parser",
        "High",
        "dotnet-ssrf-audit",
        "Medium",
        "url-validation",
        r"\b(Uri\.TryCreate|new\s+Uri|Dns\.GetHostAddresses|Dns\.GetHostEntry|IPAddress|IsLoopback|HostString|UriBuilder)\b",
    ),
    rule(
        "ssrf",
        "ssrf-metadata",
        "Critical",
        "dotnet-ssrf-audit",
        "Medium",
        "metadata-target",
        r"169\.254\.169\.254|metadata\.google\.internal|100\.100\.100\.200|metadata|IMDS|ManagedIdentityCredential",
    ),
    rule(
        "ssrf",
        "proxy-forwarded-headers",
        "High",
        "dotnet-ssrf-audit",
        "Medium",
        "proxy-header",
        r"X-Forwarded-Host|X-Forwarded-For|X-Original-URL|X-Rewrite-URL|ForwardedHeaders|UseForwardedHeaders|ForwardedHeadersOptions",
    ),
    rule(
        "ssrf",
        "remote-import-chain",
        "High",
        "dotnet-ssrf-audit",
        "Medium",
        "import-chain",
        r"\b(LoadXml|Load\(|Import|FromUri|OpenXmlPackage|SvgDocument|PdfReader|WebRequestHandler)\b",
    ),
    rule(
        "config-secret",
        "machine-key",
        "Critical",
        "dotnet-config-secrets-audit",
        "High",
        "secret-config",
        r"<machineKey\b|machineKey|validationKey|decryptionKey|MachineKeySection",
    ),
    rule(
        "config-secret",
        "secret-config",
        "High",
        "dotnet-config-secrets-audit",
        "High",
        "secret-config",
        r"(connectionStrings|ClientSecret|ClientId|SigningKey|Jwt.*Key|IssuerSigningKey|Password|AccessKey|SecretKey|PrivateKey|Saml|Certificate|Thumbprint)",
    ),
    rule(
        "config-secret",
        "debug-exposure",
        "Medium",
        "dotnet-config-secrets-audit",
        "High",
        "exposure-config",
        r"debug\s*=\s*\"true\"|customErrors\s+mode\s*=\s*\"Off\"|trace\s+enabled\s*=\s*\"true\"|ASPNETCORE_ENVIRONMENT.*Development",
    ),
    rule(
        "config-secret",
        "admin-surface-exposure",
        "High",
        "dotnet-config-secrets-audit",
        "Medium",
        "admin-surface",
        r"\b(SwaggerEndpoint|UseSwagger|UseSwaggerUI|ELMAH|Hangfire|UseHangfireDashboard|HealthChecks|MiniProfiler)\b",
    ),
    rule(
        "web-risk",
        "xss-razor-webforms",
        "High",
        "dotnet-web-risk-audit",
        "High",
        "output-encoding",
        r"\b(Html\.Raw|MvcHtmlString|IHtmlContent|Response\.Write|<%=\s*|ValidateRequest\s*=\s*\"false\"|RequestValidationMode)\b",
    ),
    rule(
        "web-risk",
        "csrf-samesite",
        "Medium",
        "dotnet-web-risk-audit",
        "Medium",
        "browser-boundary",
        r"\b(ValidateAntiForgeryToken|AutoValidateAntiforgeryToken|IgnoreAntiforgeryToken|SameSite|CookieSecurePolicy|Cookie\.SameSite)\b",
    ),
    rule(
        "web-risk",
        "cors-origin",
        "High",
        "dotnet-web-risk-audit",
        "High",
        "cors-config",
        r"\b(AllowAnyOrigin|WithOrigins|AllowCredentials|SetIsOriginAllowed|Access-Control-Allow-Origin|Origin)\b",
    ),
    rule(
        "web-risk",
        "redirect-host",
        "High",
        "dotnet-web-risk-audit",
        "High",
        "redirect-host-boundary",
        r"\b(Redirect\(|RedirectToAction|RedirectToRoute|LocalRedirect|IsLocalUrl|returnUrl|Request\.Host|Request\.Url|HostString|X-Forwarded-Host)\b",
    ),
    rule(
        "web-risk",
        "idor-fields",
        "Medium",
        "dotnet-web-risk-audit",
        "Low",
        "business-identifier",
        r"\b(userId|tenantId|orgId|roleId|ownerId|accountId|customerId|orderId|isAdmin|IsAdmin|price|status)\b",
    ),
    rule(
        "web-risk",
        "iis-rewrite-cache-smuggling",
        "High",
        "dotnet-web-risk-audit",
        "Medium",
        "proxy-cache-boundary",
        r"X-Original-URL|X-Rewrite-URL|ARR|URL Rewrite|RewriteRule|OutputCache|ResponseCache|VaryByParam|Transfer-Encoding|Content-Length",
    ),
    rule(
        "minimal-api",
        "minimal-api-endpoints",
        "Medium",
        "dotnet-minimal-api-audit",
        "High",
        "route-declaration",
        r"\bMap(Get|Post|Put|Delete|Patch|Methods|Fallback)\s*\(",
    ),
    rule(
        "minimal-api",
        "minimal-api-filters",
        "Medium",
        "dotnet-minimal-api-audit",
        "Medium",
        "auth-metadata",
        r"\bAddEndpointFilter(Factory)?\b|\bIEndpointFilter\b",
    ),
    rule(
        "blazor",
        "blazor-js-interop",
        "High",
        "dotnet-blazor-audit",
        "High",
        "sink",
        r"\bIJSRuntime\b|\bJSInvokable\b|\bInvokeAsync\b|\bInvokeVoidAsync\b",
    ),
    rule(
        "blazor",
        "blazor-markup-string",
        "High",
        "dotnet-blazor-audit",
        "High",
        "sink",
        r"\bMarkupString\b|\bAddMarkupContent\b",
    ),
    rule(
        "signalr",
        "signalr-hub",
        "Medium",
        "dotnet-signalr-audit",
        "High",
        "route-declaration",
        r"\bHub\b|\bIHubContext\b|\bHubLifetimeManager\b",
    ),
    rule(
        "signalr",
        "signalr-auth-bypass",
        "High",
        "dotnet-signalr-audit",
        "Medium",
        "auth-metadata",
        r"\[AllowAnonymous\]\s*\n\s*(public|protected)\s+\bTask\b.*\b(Hub|Clients|Groups)\b",
    ),
]


def iter_text_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in TEXT_EXTENSIONS:
            yield root
        return

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part.lower() in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def read_text(path: Path, max_bytes: int) -> str | None:
    try:
        if path.stat().st_size > max_bytes:
            return None
        data = path.read_bytes()
    except OSError:
        return None

    for encoding in ("utf-8-sig", "utf-16", "gb18030", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def normalize_snippet(line: str) -> str:
    snippet = " ".join(line.strip().split())
    return snippet[:220]


def detect_framework_hints(path: Path, text: str) -> set[str]:
    hints: set[str] = set()
    lower_name = path.name.lower()
    lower_text = text.lower()
    if path.suffix.lower() in {".aspx", ".ascx", ".ashx", ".asmx"} or "system.web" in lower_text:
        hints.add("ASP.NET Framework/WebForms")
    if "apicontroller" in lower_text or "system.web.http" in lower_text:
        hints.add("ASP.NET Web API")
    if "controllerbase" in lower_text or "webapplication.createbuilder" in lower_text or "mapcontrollers" in lower_text:
        hints.add("ASP.NET Core")
    if "servicecontract" in lower_text or path.suffix.lower() == ".svc":
        hints.add("WCF")
    if lower_name in {"web.config", "app.config"}:
        hints.add("IIS/.NET Framework config")
    if lower_name in {"appsettings.json", "appsettings.development.json"}:
        hints.add("ASP.NET Core config")
    return hints


def collect(root: Path, max_bytes: int) -> dict:
    findings = []
    files_scanned = 0
    framework_hints: set[str] = set()

    for path in iter_text_files(root):
        text = read_text(path, max_bytes)
        if text is None:
            continue
        files_scanned += 1
        framework_hints.update(detect_framework_hints(path, text))
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            for item in RULES:
                if item["regex"].search(line):
                    findings.append(
                        {
                            "category": item["category"],
                            "rule_id": item["rule_id"],
                            "severity_hint": item["severity_hint"],
                            "recommended_skill": item["recommended_skill"],
                            "confidence": item["confidence"],
                            "evidence_kind": item["evidence_kind"],
                            "file": str(path),
                            "line": line_no,
                            "snippet": normalize_snippet(line),
                        }
                    )

    by_category = Counter(item["category"] for item in findings)
    by_severity = Counter(item["severity_hint"] for item in findings)
    by_skill = Counter(item["recommended_skill"] for item in findings)
    by_evidence_kind = Counter(item["evidence_kind"] for item in findings)
    return {
        "schema_version": 2,
        "target": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files_scanned": files_scanned,
        "framework_hints": sorted(framework_hints),
        "totals": {
            "findings": len(findings),
            "by_category": dict(sorted(by_category.items())),
            "by_severity_hint": dict(sorted(by_severity.items())),
            "by_recommended_skill": dict(sorted(by_skill.items())),
            "by_evidence_kind": dict(sorted(by_evidence_kind.items())),
        },
        "findings": findings,
    }


def render_matrix(index: dict) -> str:
    findings = index["findings"]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in findings:
        grouped[item["category"]].append(item)

    lines = [
        "# .NET Attack Surface Matrix",
        "",
        f"- Target: `{index['target']}`",
        f"- Generated: `{index['generated_at']}`",
        f"- Schema version: `{index['schema_version']}`",
        f"- Files scanned: `{index['files_scanned']}`",
        f"- Findings: `{index['totals']['findings']}`",
        "",
        "## Framework Hints",
        "",
    ]
    if index["framework_hints"]:
        lines.extend(f"- {hint}" for hint in index["framework_hints"])
    else:
        lines.append("- No framework hint found")

    lines.extend(
        [
            "",
            "## Category Summary",
            "",
            "| Category | Count | Highest hint | Recommended skill | First evidence |",
            "|---|---:|---|---|---|",
        ]
    )
    severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Info": 0}
    for category in sorted(grouped):
        items = grouped[category]
        highest_item = max(items, key=lambda item: severity_order.get(item["severity_hint"], 0))
        first = items[0]
        evidence = f"{Path(first['file']).name}:{first['line']} `{first['rule_id']}`"
        lines.append(
            f"| {category} | {len(items)} | {highest_item['severity_hint']} | "
            f"{highest_item['recommended_skill']} | {evidence} |"
        )

    lines.extend(["", "## Findings", ""])
    for item in findings:
        lines.append(
            f"- [{item['severity_hint']}/{item['confidence']}] {item['category']} / {item['rule_id']} "
            f"-> {item['recommended_skill']} ({item['evidence_kind']}) - "
            f"{item['file']}:{item['line']} - `{item['snippet']}`"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect .NET attack-surface hints from source or decompiled code.")
    parser.add_argument("target", help="Source directory, decompiled directory, project file, or config file.")
    parser.add_argument("--output", "-o", help="Output directory. Defaults to <target>_audit/surface.")
    parser.add_argument("--max-file-size", type=int, default=2_000_000, help="Skip text files larger than this many bytes.")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"Target does not exist: {target}")

    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        base = target if target.is_dir() else target.parent
        output_dir = Path(f"{base}_audit") / "surface"
    output_dir.mkdir(parents=True, exist_ok=True)

    index = collect(target, args.max_file_size)
    (output_dir / "surface_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "attack_surface_matrix.md").write_text(render_matrix(index), encoding="utf-8")

    print(f"Wrote {output_dir / 'surface_index.json'}")
    print(f"Wrote {output_dir / 'attack_surface_matrix.md'}")
    print(f"Findings: {index['totals']['findings']} across {index['files_scanned']} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
