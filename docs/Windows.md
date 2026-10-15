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

- All files (mpremote)
  - `mpremote connect COM3 fs cp src/main.py :main.py + fs cp src/utility.py :utility.py + fs cp -r src/lib/ : + fs cp .env :.env`

### Virtual Environment (venv)

- Create virtualenv: `python -m venv .venv`
- Activate virtualenv: `.\.venv\Scripts\Activate.ps1`
- Install dependencies:
  - `python -m pip install -r requirements.txt`
  - `python -m pip install -r requirements-stubs.txt --target typings --no-user`

### Terminal commands and shortcuts

#### REPL

- `CTRL-D` - soft reset
- `CTRL-]` - exit and release COM port
- `CTRL-C` - send interrupt