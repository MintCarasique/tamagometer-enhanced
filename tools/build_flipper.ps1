[CmdletBinding()]
param(
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$flipperRoot = Join-Path $repoRoot "flipper"
if (-not $OutputPath) {
    $OutputPath = Join-Path $repoRoot "artifacts/tamagometer_enhanced_dev.fap"
}
$OutputPath = [IO.Path]::GetFullPath($OutputPath)
if ([IO.Path]::GetExtension($OutputPath) -ne ".fap") {
    throw "OutputPath must name a .fap file."
}

Push-Location $flipperRoot
try {
    # The default target installs the current result into dist. Building only
    # fap_<appid> leaves an existing dist file untouched.
    python -m ufbt
    if ($LASTEXITCODE -ne 0) { throw "Flipper build failed." }

    $builtFile = Join-Path $flipperRoot "dist/tamagometer_enhanced.fap"
    $metadata = Get-Content -LiteralPath (Join-Path $flipperRoot "tamagometer_version.h") -Raw
    if ($metadata -notmatch '#define TAMA_APP_VERSION "([^"]+)"') {
        throw "Runtime version metadata was not found."
    }
    $expectedVersion = $Matches[1]
    $binary = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($builtFile))
    if (-not $binary.Contains($expectedVersion)) {
        throw "Built FAP does not contain the expected version $expectedVersion."
    }
    $outputDirectory = Split-Path -Parent $OutputPath
    $null = New-Item -ItemType Directory -Path $outputDirectory -Force
    if ($OutputPath -ne [IO.Path]::GetFullPath($builtFile)) {
        Copy-Item -LiteralPath $builtFile -Destination $OutputPath -Force
    }
    $builtHash = (Get-FileHash -LiteralPath $builtFile -Algorithm SHA256).Hash
    $outputHash = (Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash
    if ($builtHash -ne $outputHash) { throw "Copied FAP checksum mismatch." }
    Write-Output "FAP_OK version=$expectedVersion path=$OutputPath sha256=$outputHash"
}
finally {
    Pop-Location
}
