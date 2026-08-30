[CmdletBinding(DefaultParameterSetName = "Paths")]
param(
    [Parameter(Mandatory)] [string]$Message,
    [Parameter(Mandatory, ParameterSetName = "Paths")] [string[]]$Paths,
    [Parameter(Mandatory, ParameterSetName = "All")] [switch]$All,
    [switch]$SkipChecks
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if ($All) {
    git add --all
}
else {
    git add -- $Paths
}
if ($LASTEXITCODE -ne 0) { throw "git add failed" }

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { throw "There are no staged changes to commit." }
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "Staged changes failed git diff --check." }

if (-not $SkipChecks) {
    & (Join-Path $PSScriptRoot "check.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Project checks failed." }
}

git commit -m $Message
if ($LASTEXITCODE -ne 0) { throw "git commit failed" }
Write-Output "COMMIT_OK commit=$(git rev-parse --short HEAD)"
