[CmdletBinding()]
param(
    [switch]$SkipQmlLint,
    [switch]$SkipCompile
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$desktopRoot = Join-Path $repoRoot "desktop"

function Invoke-LoggedCommand {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [scriptblock]$Command
    )

    $logPath = [IO.Path]::GetTempFileName()
    try {
        & $Command *> $logPath
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[failed] $Name" -ForegroundColor Red
            Get-Content -LiteralPath $logPath -Tail 80
            throw "$Name failed with exit code $LASTEXITCODE"
        }
        return Get-Content -LiteralPath $logPath -Raw
    }
    finally {
        Remove-Item -LiteralPath $logPath -Force -ErrorAction SilentlyContinue
    }
}

Push-Location $desktopRoot
try {
    $testOutput = Invoke-LoggedCommand "Desktop tests" {
        python -m unittest discover -s tests
    }
    $testCount = if ($testOutput -match "Ran (\d+) tests?") { $Matches[1] } else { "unknown" }
    Write-Host "[ok] Desktop tests ($testCount)"

    if (-not $SkipQmlLint) {
        $qmlLint = Get-Command "pyside6-qmllint" -ErrorAction SilentlyContinue
        if (-not $qmlLint) {
            $packageRoot = python -c "import pathlib, PySide6; print(pathlib.Path(PySide6.__file__).parent)"
            $candidate = Join-Path $packageRoot "qmllint.exe"
            if (-not (Test-Path -LiteralPath $candidate)) {
                $candidate = Join-Path $packageRoot "qmllint"
            }
            if (-not (Test-Path -LiteralPath $candidate)) {
                throw "pyside6-qmllint was not found. Install desktop/requirements-dev.txt."
            }
            $qmlLint = $candidate
        }
        $qmlFiles = Get-ChildItem "tamagometer_desktop/qt/qml" -Recurse -Filter "*.qml" |
            ForEach-Object { $_.FullName }
        $null = Invoke-LoggedCommand "QML lint" { & $qmlLint @qmlFiles }
        Write-Host "[ok] QML lint"
    }

    if (-not $SkipCompile) {
        $null = Invoke-LoggedCommand "Python compileall" { python -m compileall -q . }
        Write-Host "[ok] Python compileall"
    }
}
finally {
    Pop-Location
}

Write-Output "CHECKS_OK tests=$testCount"
