[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$Branch,
    [Parameter(Mandatory)] [string]$Message,
    [switch]$KeepBranch,
    [switch]$SkipChecks
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

git check-ref-format --branch $Branch *> $null
if ($LASTEXITCODE -ne 0 -or $Branch -eq "main") {
    throw "Provide a valid feature branch, not main."
}
if (git status --porcelain) { throw "Working tree must be clean before a squash merge." }

git fetch origin --prune
if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }
git show-ref --verify --quiet "refs/heads/$Branch"
if ($LASTEXITCODE -ne 0) {
    git show-ref --verify --quiet "refs/remotes/origin/$Branch"
    if ($LASTEXITCODE -ne 0) { throw "Branch '$Branch' does not exist locally or on origin." }
    git branch --track $Branch "origin/$Branch"
    if ($LASTEXITCODE -ne 0) { throw "Could not create local tracking branch '$Branch'." }
}

$sourceCommit = git rev-parse $Branch
git switch main
if ($LASTEXITCODE -ne 0) { throw "Could not switch to main." }
git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw "main could not be fast-forwarded from origin." }

git merge-base --is-ancestor $sourceCommit HEAD
if ($LASTEXITCODE -eq 0) { throw "Branch '$Branch' is already contained in main." }

git merge --squash $Branch
if ($LASTEXITCODE -ne 0) {
    throw "Squash merge has conflicts. Resolve them on main, run checks, and commit manually."
}

if (-not $SkipChecks) {
    & (Join-Path $PSScriptRoot "check.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Project checks failed; squashed changes remain staged on main." }
}

git commit -m $Message
if ($LASTEXITCODE -ne 0) { throw "Could not create the squash commit." }
git push origin main
if ($LASTEXITCODE -ne 0) { throw "Could not push main." }

if (-not $KeepBranch) {
    git branch -D $Branch
    if ($LASTEXITCODE -ne 0) { throw "main was pushed, but local branch cleanup failed." }
    git ls-remote --exit-code --heads origin $Branch *> $null
    if ($LASTEXITCODE -eq 0) {
        git push origin --delete $Branch
        if ($LASTEXITCODE -ne 0) { throw "main was pushed, but remote branch cleanup failed." }
    }
}

Write-Output "SQUASH_OK branch=$Branch commit=$(git rev-parse --short HEAD) deleted=$(-not $KeepBranch)"
