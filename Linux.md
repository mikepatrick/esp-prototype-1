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

### Installing pyenv

Installing pyenv and using a virtualenv is only required if modifying the python installation - i.e. if running `python -m pip install mpremote`

If not using `mpremote`, to push code to the chip, `pyenv` is not required.

Install prerequisites:

```
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
libffi-dev liblzma-dev git
```

Download and run install script
```
curl https://pyenv.run | zsh
```

Then add to `~/.zshrc`:

```
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"

# Restart your shell for the changes to take effect.

# Load pyenv-virtualenv automatically by adding
# the following to ~/.bashrc:

eval "$(pyenv virtualenv-init -)"
```

Install and activate virtualenv
```
# Install 3.14.8 and set it as global default
pyenv install 3.14.8
pyenv global 3.14.8
# Create and activate virtual environment
pyenv virtualenv esp-prototype-1
pyenv activate esp-prototype-1
# Install mpremote into virtualenv
python -m pip install mpremote
```

### Sync code to chip (Linux)

- Sync button in VSCode appears to work, or:
- `mpremote connect /dev/ttyUSB0 fs cp src/main.py :main.py + fs cp src/utility.py :utility.py + fs cp -r src/lib/ :`