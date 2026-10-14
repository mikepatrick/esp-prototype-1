param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^COM\d+$')]
    [string]$Port,

    [Parameter(Mandatory = $true)]
    [string]$WorkspaceRoot
)

$ErrorActionPreference = 'Stop'
$extensionRoot = Join-Path $env:USERPROFILE '.vscode\extensions'
$cli = Get-ChildItem -LiteralPath $extensionRoot -Directory -Filter 'rt-thread.rt-thread-micropython-*' |
    Sort-Object LastWriteTimeUtc -Descending |
    ForEach-Object { Join-Path $_.FullName 'ampy\cli.exe' } |
    Where-Object { Test-Path -LiteralPath $_ } |
    Select-Object -First 1

if (-not $cli) {
    throw 'Could not find the RT-Thread MicroPython extension ampy CLI.'
}

$WorkspaceRoot = (Resolve-Path -LiteralPath $WorkspaceRoot).Path
$sourceRoot = Join-Path $WorkspaceRoot 'src'
if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot 'main.py'))) {
    throw 'Expected src\main.py in the workspace.'
}

$stage = Join-Path $env:TEMP ([guid]::NewGuid().ToString())
try {
    New-Item -ItemType Directory -Path $stage | Out-Null
    Get-ChildItem -LiteralPath $sourceRoot -Force | Copy-Item -Destination $stage -Recurse -Force

    Write-Host "Uploading src contents to $Port with main.py at the filesystem root..."
    & $cli -p $Port -d 2 put $stage '/'
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    Write-Host 'Upload complete.'
}
finally {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
}