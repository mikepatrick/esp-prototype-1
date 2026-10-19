ifeq ($(OS), Windows_NT)
    # Windows-specific settings
    TARGET = COM3
else
    # Linux / macOS settings
    TARGET = /dev/ttyUSB0
endif
# ------------------------------------------------------------------------------
# Global Settings
# ------------------------------------------------------------------------------
# Define the scripts we want to target
INSTALL_WIN := .\bin\win\install.bat
INSTALL_NIX := ./bin/linux/install.sh

.PHONY: all windows linux

# Default target when you run just 'make'
all: linux

linux:
	@echo "Executing Linux setup scripts"
	zsh $(INSTALL_NIX)

windows:
	@echo "Executing Windows setup scripts"
	cmd.exe /c $(INSTALL_WIN)

repl:
	mpremote connect $(TARGET)

push:
	@echo "Pushing main.py and utility.py to ESP-32 device..."
	mpremote connect $(TARGET) fs cp src/main.py :main.py + fs cp src/utility.py :utility.py + fs cp src/app.py :app.py

push-all:
	@echo "Pushing all files to ESP-32 device..."
	mpremote connect $(TARGET) fs cp src/main.py :main.py + fs cp src/utility.py :utility.py + fs cp -r src/lib/ : + fs cp .env :.env

activate-win:
	@echo .\.venv\Scripts\Activate.ps1

activate-nix:
	@echo source ./.venv/bin/activate
