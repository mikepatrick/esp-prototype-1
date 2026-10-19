### Building Micropython

The downloaded micropython firmware does not have debug/trace capability enabled.  To obtain a firmware image with this facility, use the Espressif IDF toolchain to build the firmware.

#### Espressif

Started (here)[https://github.com/micropython/micropython/blob/master/ports/esp32/README.md].  Followed (these)[https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/linux-setup.html] instructions, ~~using `apt` to install `eim` and then the EIM GUI to install the build toolchain~~.

EIM didn't really work (bunch of missing python dependencies when I went to build ESP32 port).  Fell back to shell script install method.

ESP-IDF needs to be 5.5.5.  Using current off `main` branch (6.x) does not work.

```
git fetch --tags
git checkout v5.5.5
git submodule update --init --recursive
./install.sh esp32
source export.sh
```

Then in `micropython` project:

Before building firmware: `export CFLAGS_EXTRA="-DMICROPY_PY_SYS_SETTRACE=1"`

Add `#define MICROPY_PY_SYS_SETTRACE (1)` to micropython/ports/esp32/mpconfigport.h

```
cd /path/to/micropython/ports/esp32
make clean
make submodules
make
```
Flash newly built firmware to chip:

```
python -m esptool --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_size 4MB --flash_freq 40m 0x1000 ~/workspace/micropython/ports/esp32/build-ESP32_GENERIC/bootloader/bootloader.bin 0x8000 ~/workspace/micropython/ports/esp32/build-ESP32_GENERIC/partition_table/partition-table.bin 0x10000 ~/workspace/micropython/ports/esp32/build-ESP32_GENERIC/micropython.bin
```

#### Debugging

- Clone `mp_debugpy` and submodules
    - after `git clone`, `./update_submodules.sh `
- Compile: `python launcher/compile_debugpy.py `
- `cd` into `launcher/compiled` folder
  - flatten this folder - `cp -r launcher/compiled/debugpy/* launcher/compiled/`
- copy debug library to device:
    - `mpremote connect /dev/ttyUSB0 cp -r . :lib/debugpy/ `

See `feature/debugging` branch

