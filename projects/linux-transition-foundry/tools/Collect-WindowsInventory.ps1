#requires -Version 5.1
<#
.SYNOPSIS
  Read-only local inventory for a customer-approved Windows-to-Linux readiness assessment.
.DESCRIPTION
  Collects OS, hardware, installed application, printer and basic device facts.
  Does not install software, change configuration, access user documents, collect credentials,
  transmit data, or contact external services. Review output before sharing: hardware identifiers
  and installed application names may be commercially or personally sensitive.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$OutputPath = ".\windows-inventory.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

function Get-SafeValue {
    param([scriptblock]$Query)
    try { & $Query } catch { $null }
}

$os = Get-SafeValue { Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture, InstallDate, LastBootUpTime }
$computer = Get-SafeValue { Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, TotalPhysicalMemory, SystemType }
$bios = Get-SafeValue { Get-CimInstance Win32_BIOS | Select-Object SMBIOSBIOSVersion, ReleaseDate }
$processor = Get-SafeValue { Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, AddressWidth, DataWidth }
$disks = Get-SafeValue { Get-CimInstance Win32_DiskDrive | Select-Object Model, InterfaceType, MediaType, Size }
$memory = Get-SafeValue { Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity, Speed, MemoryType }
$apps = Get-SafeValue {
    $paths = @(
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )
    foreach ($path in $paths) {
        Get-ItemProperty $path -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName } |
            Select-Object @{Name='Name';Expression={$_.DisplayName}},
                          @{Name='Version';Expression={$_.DisplayVersion}},
                          Publisher, InstallDate
    } | Sort-Object Name, Version -Unique
}
$printers = Get-SafeValue { Get-Printer -ErrorAction Stop | Select-Object Name, DriverName, PortName, Shared }
$secureBoot = Get-SafeValue { Confirm-SecureBootUEFI -ErrorAction Stop }

$result = [ordered]@{
    schema_version = "1.0"
    collected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    collection_mode = "local_read_only"
    computer = $computer
    operating_system = $os
    bios = $bios
    processors = @($processor)
    physical_memory = @($memory)
    disks = @($disks)
    installed_applications = @($apps)
    printers = @($printers)
    secure_boot_enabled = $secureBoot
    limitations = @(
        "Application inventory does not prove application usage or Linux compatibility.",
        "Hardware and application data must be reviewed and approved before external sharing.",
        "No user documents, credentials, browsing history or network traffic are collected.",
        "This report is not a security audit or migration approval."
    )
}

$fullPath = [System.IO.Path]::GetFullPath($OutputPath)
$parent = Split-Path -Parent $fullPath
if ($parent -and -not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $fullPath -Encoding UTF8
Write-Output "Inventory written locally to: $fullPath"
Write-Warning "Review and redact the report before sharing it with a service provider."
