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

foreach ($file in Get-ChildItem -LiteralPath $sourceRoot -Filter '*.py' -File) {
    $remotePath = '/' + $file.Name
    Write-Host "Uploading $($file.Name) to $remotePath"
    & $cli -p $Port -d 2 put $file.FullName $remotePath
    if ($LASTEXITCODE -ne 0) {
        throw "Upload failed: $($file.Name)"
    }
}

$libraryRoot = Join-Path $sourceRoot 'lib'
if (Test-Path -LiteralPath $libraryRoot) {
    Write-Host 'Uploading src\lib to /lib'
    & $cli -p $Port -d 2 put $libraryRoot '/lib'
    if ($LASTEXITCODE -ne 0) {
        throw 'Upload failed: src\lib'
    }
}

Write-Host 'Upload complete.'