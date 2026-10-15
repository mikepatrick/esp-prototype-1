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
- Single file (ampy)

```
$cli = "$env:USERPROFILE\.vscode\extensions\rt-thread.rt-thread-micropython-1.0.11\ampy\cli.exe"

& $cli -p COM3 -d 2 put "$PWD\src\main.py" "/main.py"
```

- All files (mpremote)

- `mpremote connect COM3 fs cp src/main.py :main.py + fs cp src/utility.py :utility.py + fs cp -r src/lib/ : + fs cp .env :.env`

### Pyenv

- Install using admin powershell window

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

- 3.14.8 not available on windows for some reason?  `pyenv update` threw error.
- `pyenv install 3.14.5`
- `pyenv global 3.14.5`

- Create virtualenv: `python -m venv .venv`
- Activate virtualenv: `.\.venv\Scripts\Activate.ps1`
- Install `mpremote`: `python -m pip install mpremote`

### Terminal commands and shortcuts

#### Rt-Thread MicroPython REPL

- `CTRL-D` - soft reset
- `CTRL-]` - exit and release COM port
- `CTRL-C` - send interrupt