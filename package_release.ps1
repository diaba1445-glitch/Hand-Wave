# Package HandWave into a clean, standalone distribution zip
$ErrorActionPreference = "Stop"

$version = "v1.0.0"
$distDir = Join-Path $PSScriptRoot "dist_release\HandWave-$version-windows-x64"
$zipPath = Join-Path $PSScriptRoot "dist_release\HandWave-$version-windows-x64.zip"

Write-Host "Creating clean staging folder at: $distDir" -ForegroundColor Cyan
if (Test-Path $distDir) {
    Remove-Item -Recurse -Force $distDir
}
New-Item -ItemType Directory -Force -Path $distDir | Out-Null

# Required files to bundle
$files = @(
    "HandWave.exe",
    "hand_landmarker.task",
    "config.json",
    "Start_HandWave.bat",
    "Open_Settings.bat",
    "HOW_TO_USE.txt",
    "README.md",
    "LICENSE",
    "THIRD_PARTY_LICENSES.md"
)

foreach ($f in $files) {
    $src = Join-Path $PSScriptRoot $f
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $distDir -Force
        Write-Host "  + Bundled $f" -ForegroundColor Green
    } else {
        Write-Warning "File not found: $src"
    }
}

# Copy _internal runtime folder
$internalSrc = Join-Path $PSScriptRoot "_internal"
if (Test-Path $internalSrc) {
    Write-Host "  + Copying _internal runtime (this may take a few seconds)..." -ForegroundColor Yellow
    Copy-Item -Path $internalSrc -Destination (Join-Path $distDir "_internal") -Recurse -Force
    Write-Host "  + _internal runtime copied successfully." -ForegroundColor Green
} else {
    Write-Warning "_internal directory not found. Compile with PyInstaller first if building standalone executable."
}

# Create Zip
if (Test-Path $zipPath) {
    Remove-Item -Force $zipPath
}
Write-Host "Compressing to $zipPath..." -ForegroundColor Cyan
Compress-Archive -Path "$distDir\*" -DestinationPath $zipPath -Force

$zipSize = (Get-Item $zipPath).Length / 1MB
Write-Host "Release package created successfully!" -ForegroundColor Green
Write-Host "Archive: $zipPath" -ForegroundColor White
Write-Host "Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor White
