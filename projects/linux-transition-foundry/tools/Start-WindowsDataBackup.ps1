[CmdletBinding()]
param([Parameter(Mandatory=$true)][ValidateNotNullOrEmpty()][string]$Destination,[switch]$IncludeDownloads)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
function Get-Sha256([string]$Path) {
  $stream=[IO.File]::OpenRead($Path)
  try { $sha=[Security.Cryptography.SHA256]::Create(); try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-","").ToLowerInvariant() } finally {$sha.Dispose()} }
  finally {$stream.Dispose()}
}
$dest=[IO.Path]::GetFullPath($Destination); $profile=[IO.Path]::GetFullPath($env:USERPROFILE)
if ($dest.StartsWith($profile,[StringComparison]::OrdinalIgnoreCase)) { throw "Use a separate external drive, not a folder inside the source profile." }
if (!(Test-Path -LiteralPath $dest)) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }
$dest=(Resolve-Path -LiteralPath $dest).Path
$root=Join-Path $dest ("Ubuntu-Migration-"+(Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Path $root | Out-Null
$folders=@(
 @{Name="Desktop";Path=[Environment]::GetFolderPath("Desktop")},
 @{Name="Documents";Path=[Environment]::GetFolderPath("MyDocuments")},
 @{Name="Pictures";Path=[Environment]::GetFolderPath("MyPictures")},
 @{Name="Music";Path=[Environment]::GetFolderPath("MyMusic")},
 @{Name="Videos";Path=[Environment]::GetFolderPath("MyVideos")},
 @{Name="Favorites";Path=(Join-Path $profile "Favorites")}
)
if ($IncludeDownloads) {$folders+=@{Name="Downloads";Path=(Join-Path $profile "Downloads")}}
$roots=@()
foreach($f in $folders) {
 $src=[string]$f.Path
 if ([string]::IsNullOrWhiteSpace($src) -or !(Test-Path -LiteralPath $src -PathType Container)) {Write-Warning "Skipping unavailable folder $($f.Name)";continue}
 $dst=Join-Path $root $f.Name; New-Item -ItemType Directory -Path $dst | Out-Null
 & robocopy $src $dst /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /XJ /FFT /NP | Out-Null
 if ($LASTEXITCODE -ge 8) {throw "Robocopy failed for $($f.Name), exit code $LASTEXITCODE"}
 $roots+=@{name=$f.Name;source=$src}
}
$entries=@()
Get-ChildItem -LiteralPath $root -File -Recurse -Force | ForEach-Object {
 $rel=$_.FullName.Substring($root.Length).TrimStart([char[]]@('\','/')).Replace('\','/')
 $entries+=@{path=$rel;size=[int64]$_.Length;sha256=(Get-Sha256 $_.FullName)}
}
$manifest=@{format="linux-transition-foundry-backup";version=1;created_utc=(Get-Date).ToUniversalTime().ToString("o");source_os=(Get-CimInstance Win32_OperatingSystem).Caption;source_computer=$env:COMPUTERNAME;included_roots=$roots;file_count=$entries.Count;files=$entries}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $root "migration-manifest.json") -Encoding UTF8
Write-Host "Backup copied to $root; files recorded: $($entries.Count)"
Write-Warning "Verify on another device and open sample files. Do not erase Windows based on this output."
