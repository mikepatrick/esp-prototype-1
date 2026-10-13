### MicroPython Firmware

- Download here: https://micropython.org/download/ESP32_GENERIC/
  - v1.29.0 (2026-08-24) .bin
- Install esptool
  - `pip install esptool`  (Mac/Linux)
  - `py -m pip install esptool`  (Windows)
- Flash firmware to chip
  -  `py -m esptool --port COM3 erase_flash`
  -  `py -m esptool --port COM3 --baud 460800 write_flash 0x1000 '.\ESP32_GENERIC-20260824-v1.29.0.bin`

### Version control

- Install git (Windows): `winget install --id Git.Git -e --source winget`
  - `git config --global user.name <GIT_USERNAME>`
  - `git config --global user.email "<GIT_EMAIL>"`


### Libraries

#### Using

- https://github.com/miketeachman/micropython-rotary
- ssd1306.py copied from ~~Wokwi~~ [Github](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py)

#### To Look At

- https://github.com/peterhinch/micropython-micro-gui

### VSCode

- Install VSCode, RT-Thread MicroPython extension


### Resources

- [Wokwi emulator](https://wokwi.com/projects/477055555124397057)
