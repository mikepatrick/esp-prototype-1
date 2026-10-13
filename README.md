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
  - `git config --global user.name mikepatrick`
  - `git config --global user.email "mpatrick76@gmail.com"`


### Libraries

#### Using

- https://github.com/miketeachman/micropython-rotary
- ssd1306.py copied from ~~Wokwi~~ [Github](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py)

#### To Look At

- https://github.com/peterhinch/micropython-micro-gui

### VSCode

- Install VSCode, RT-Thread MicroPython extension

### Syncing code to chip (Windows)
- Single file

```
$cli = "$env:USERPROFILE\.vscode\extensions\rt-thread.rt-thread-micropython-1.0.11\ampy\cli.exe"
>> & $cli -p COM3 -d 2 put "$PWD\main.py"
  ```


 ```

  $cli = "$env:USERPROFILE\.vscode\extensions\rt-thread.rt-thread-micropython-1.0.11\ampy\cli.exe"
  if (-not (Test-Path $cli)) { throw "Uploader not found: $cli" }

  Get-ChildItem -File -Filter *.py | ForEach-Object {
    Write-Host "Uploading $($_.Name)"
    & $cli -p COM3 -d 2 put $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "Upload failed: $($_.Name)" }
  }
  ```
  
- All Python files

Run **Tasks: Run Task** and select **Copy workspace to MicroPython device**. It uploads workspace `.py` files with one `ampy put` command, which works with standard MicroPython firmware. Close the extension's REPL terminal first so it releases the serial port.

### Resources

- [Wokwi emulator](https://wokwi.com/projects/477055555124397057)