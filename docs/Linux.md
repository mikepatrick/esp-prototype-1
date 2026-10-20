### SSH

[Instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

### Connecting to chip

Ubuntu locks down serial connections by default.  Add user to appropriate group to allow connection to `ttyusb0`.

```
sudo usermod -aG dialout $USER
```

### Installing VSCode

```
sudo apt update
sudo apt install -y wget gpg apt-transport-https

wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg

sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/keyrings/packages.microsoft.gpg
rm -f packages.microsoft.gpg

echo "deb [arch=amd64,arm64,armhf signed-by=/etc/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null

sudo apt update
sudo apt install -y code

```

### Virtual Environment (venv)

- Create virtualenv: `python -m venv .venv`
- Activate virtualenv: `source .venv/bin/activate`
- Install dependencies:
  - `python -m pip install -r requirements.txt`
  - `python -m pip install -r requirements-stubs.txt --target typings --no-user`

### Sync code to chip (Linux)

- Sync button in VSCode appears to work, or:
- `mpremote connect /dev/ttyUSB0 fs cp src/main.py :main.py + fs cp src/utility.py :utility.py + fs cp -r src/lib/ : + fs cp .env :.env`