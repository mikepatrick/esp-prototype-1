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

& $cli -p COM3 -d 2 put "$PWD\src\main.py" "/main.py"
```

- All source files (VS Code task)

Run **Tasks: Run Task** and select **Push Code (Windows)**. The task copies the contents of `src` to the device root, so `main.py` stays at `/main.py` and libraries remain under `/lib`. Close the REPL terminal first so it releases the serial port.
