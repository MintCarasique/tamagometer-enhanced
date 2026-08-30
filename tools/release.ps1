[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern("^\d+\.\d+\.\d+(?:-rc\.\d+)?$")]
    [string]$Version,
    [switch]$SkipChecks,
    [ValidateRange(60, 1800)] [int]$TimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot
$tag = "v$Version"

if ((git branch --show-current) -ne "main") { throw "Releases must start from main." }
if (git status --porcelain) { throw "Working tree must be clean before a release." }

git fetch origin --prune --tags
if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }
git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw "main could not be fast-forwarded from origin." }

$versionFile = Get-Content "desktop/tamagometer_desktop/__init__.py" -Raw
$versionPattern = '__version__\s*=\s*["'']{0}["'']' -f [regex]::Escape($Version)
if ($versionFile -notmatch $versionPattern) {
    throw "Desktop version metadata does not equal $Version."
}
$changelog = Get-Content "CHANGELOG.md" -Raw
if ($changelog -notmatch "(?m)^## \[$([regex]::Escape($Version))\] - \d{4}-\d{2}-\d{2}\s*$") {
    throw "CHANGELOG.md has no dated [$Version] release section."
}

git rev-parse --verify --quiet "refs/tags/$tag" *> $null
if ($LASTEXITCODE -eq 0) { throw "Local tag $tag already exists." }
git ls-remote --exit-code --tags origin "refs/tags/$tag" *> $null
if ($LASTEXITCODE -eq 0) { throw "Remote tag $tag already exists." }

if (-not $SkipChecks) {
    & (Join-Path $PSScriptRoot "check.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Project checks failed." }
}

$headCommit = git rev-parse HEAD
git push origin main
if ($LASTEXITCODE -ne 0) { throw "Could not push main." }
git tag -a $tag -m "Tamagometer Enhanced $Version"
if ($LASTEXITCODE -ne 0) { throw "Could not create tag $tag." }
git push origin $tag
if ($LASTEXITCODE -ne 0) { throw "Could not push tag $tag." }
Write-Host "[ok] Pushed $tag at $($headCommit.Substring(0, 7))"

$remoteUrl = git remote get-url origin
if ($remoteUrl -notmatch "github\.com[/:](?<repo>[^/]+/[^/]+?)(?:\.git)?$") {
    throw "The origin remote is not a supported GitHub URL. Tag was pushed; monitor it manually."
}
$repository = $Matches.repo
$headers = @{ "User-Agent" = "Tamagometer-Release-Tool"; "Accept" = "application/vnd.github+json" }
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$run = $null
$lastStatus = ""

while ((Get-Date) -lt $deadline) {
    $runs = (Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$repository/actions/runs?per_page=20").workflow_runs
    $run = $runs | Where-Object { $_.head_sha -eq $headCommit -and $_.head_branch -eq $tag } | Select-Object -First 1
    if ($run) {
        $status = "$($run.status)/$($run.conclusion)"
        if ($status -ne $lastStatus) {
            Write-Host "[wait] GitHub Actions $status"
            $lastStatus = $status
        }
        if ($run.status -eq "completed") { break }
    }
    Start-Sleep -Seconds 10
}

if (-not $run -or $run.status -ne "completed") {
    throw "Timed out waiting for the tag workflow. Tag was pushed; check GitHub Actions."
}
if ($run.conclusion -ne "success") {
    $jobs = (Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$repository/actions/runs/$($run.id)/jobs?filter=all").jobs
    $summary = ($jobs | ForEach-Object { "$($_.name)=$($_.conclusion)" }) -join ", "
    throw "Release workflow failed: $summary ($($run.html_url))"
}

$release = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$repository/releases/tags/$tag"
$expectedAssets = @("TamagometerDesktop.exe", "tamagometer_enhanced.fap", "SHA256SUMS.txt", "THIRD_PARTY_NOTICES.md")
$assetNames = @($release.assets.name)
$missingAssets = @($expectedAssets | Where-Object { $_ -notin $assetNames })
if ($missingAssets) { throw "Release is missing assets: $($missingAssets -join ', ')" }
$expectedPrerelease = $Version -match "-rc\."
if ([bool]$release.prerelease -ne $expectedPrerelease) {
    throw "Release prerelease state does not match version $Version."
}

Write-Output "RELEASE_OK tag=$tag run=$($run.html_url) release=$($release.html_url) assets=$($assetNames.Count)"
