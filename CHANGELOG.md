# CHANGELOG

- 10/15/2026
  - Add MicroPico extension, and initialize MicroPico project at root of folder
  - Automatically adds MicroPython stubs (e.g. `machine`, `framebuf`)
  - Need `openOnStart` and `autoConnect` both set to `false` in settings.json
  - Stubs for ADC (potentiometer) missing `init()` method.'
  - Use "Switch Stubs" action to select ESP32 stubs.
    - Otherwise, `ADC.init()` not found.  Also some issues with `Final[int]` vs `int`?
  - Eventually abandoned when board seemed to get into a bad state.  Might try again.
