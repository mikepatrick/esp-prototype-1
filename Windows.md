### SSH

#### Install Git
- `winget install --id Git.Git -e --source winget`

#### Create key and add to agent:

- User Powershell:
  -  `ssh-keygen -t ed25519 -C "mpatrick76@gmail.com"`
- Admin Powershell:
  -  `Set-Service -Name ssh-agent -StartupType Manual`
  - `Start-Service ssh-agent`
- Add public key to Github account
- User Powershell:
  - `ssh-add c:\Users\mike\.ssh\id_ed25519`
  - Verify: `ssh -T git@github.com`

### Syncing code to chip (Windows)
- Single file

```
$cli = "$env:USERPROFILE\.vscode\extensions\rt-thread.rt-thread-micropython-1.0.11\ampy\cli.exe"

& $cli -p COM3 -d 2 put "$PWD\main.py"
```

- All python files (CLI)


```

  $cli = "$env:USERPROFILE\.vscode\extensions\rt-thread.rt-thread-micropython-1.0.11\ampy\cli.exe"
  if (-not (Test-Path $cli)) { throw "Uploader not found: $cli" }

  Get-ChildItem -File -Filter *.py | ForEach-Object {
    Write-Host "Uploading $($_.Name)"
    & $cli -p COM3 -d 2 put $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "Upload failed: $($_.Name)" }
  }
  ```
  
- All Python files (VSCode task)

Run **Tasks: Run Task** and select **Push Code (Windows)**. It uploads workspace `.py` files with one `ampy put` command, which works with standard MicroPython firmware. Close the extension's REPL terminal first so it releases the serial port.
