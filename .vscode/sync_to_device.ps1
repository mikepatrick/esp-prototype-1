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
$workspacePrefix = $WorkspaceRoot.TrimEnd('\') + '\'
$excludedPathPattern = '(?i)(^|[\\/])(?:\.git|\.vscode|__pycache__|\.venv|venv|node_modules)([\\/]|$)'
$files = @(Get-ChildItem -LiteralPath $WorkspaceRoot -Filter '*.py' -File -Recurse | Where-Object {
    $_.FullName.Substring($workspacePrefix.Length) -notmatch $excludedPathPattern
})

if ($files.Count -eq 0) {
    throw 'No Python source files found in the workspace.'
}

$stage = Join-Path $env:TEMP ([guid]::NewGuid().ToString())
try {
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($workspacePrefix.Length)
        $stagedPath = Join-Path $stage $relativePath
        $stagedDirectory = Split-Path -Parent $stagedPath
        New-Item -ItemType Directory -Path $stagedDirectory -Force | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $stagedPath
    }

    Write-Host "Uploading $($files.Count) Python files to $Port..."
    & $cli -p $Port -d 2 put $stage '/'
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    Write-Host 'Upload complete.'
}
finally {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
}