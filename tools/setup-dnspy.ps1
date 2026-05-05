#Requires -Version 5.1
<#
.SYNOPSIS
    Download and extract dnSpy for .NET decompilation.
.DESCRIPTION
    This script downloads the latest stable dnSpy.Console release from GitHub
    and extracts it to ./dnSpy/ under the project root.
    Run this before auditing binary-only .NET projects.
.NOTES
    Requires PowerShell 5.1+ and internet access.
    dnSpy is a third-party tool: https://github.com/dnSpy/dnSpy
#>

[CmdletBinding()]
param(
    [string]$OutputPath = "$PSScriptRoot\..\dnSpy",
    [string]$Version = "6.5.0"
)

$ErrorActionPreference = "Stop"

$arch = if ([Environment]::Is64BitOperatingSystem) { "win64" } else { "win32" }
$zipName = "dnSpy-${Version}-${arch}.zip"
$downloadUrl = "https://github.com/dnSpy/dnSpy/releases/download/v${Version}/${zipName}"

Write-Host "[+] dnSpy Setup Script" -ForegroundColor Cyan
Write-Host "    Version : $Version" -ForegroundColor Gray
Write-Host "    Arch    : $arch" -ForegroundColor Gray
Write-Host "    Output  : $OutputPath" -ForegroundColor Gray
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    Write-Host "[+] Created directory: $OutputPath" -ForegroundColor Green
}

$zipPath = Join-Path $OutputPath $zipName

# Download
if (-not (Test-Path $zipPath)) {
    Write-Host "[+] Downloading from GitHub ..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
        Write-Host "[+] Download complete: $zipPath" -ForegroundColor Green
    } catch {
        Write-Error "Failed to download dnSpy. Please check your network or download manually from: https://github.com/dnSpy/dnSpy/releases"
        exit 1
    }
} else {
    Write-Host "[*] Zip already exists: $zipPath" -ForegroundColor Gray
}

# Extract
Write-Host "[+] Extracting ..." -ForegroundColor Yellow
Expand-Archive -Path $zipPath -DestinationPath $OutputPath -Force
Write-Host "[+] Extraction complete." -ForegroundColor Green

# Verify
$exePath = Join-Path $OutputPath "dnSpy.Console.exe"
if (Test-Path $exePath) {
    Write-Host "[+] dnSpy.Console.exe found at:" -ForegroundColor Green
    Write-Host "    $exePath" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage example:" -ForegroundColor Cyan
    Write-Host "    dnSpy\dnSpy.Console.exe -o audit-output\decompiled -r bin\" -ForegroundColor White
} else {
    Write-Warning "dnSpy.Console.exe not found after extraction. Please verify manually."
}

Write-Host ""
Write-Host "[*] Done." -ForegroundColor Cyan
