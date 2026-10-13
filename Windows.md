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

