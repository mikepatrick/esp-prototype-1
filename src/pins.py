import time

import framebuf
from machine import ADC, I2C, Pin

from lib import ssd1306
from lib.rotary_irq_esp import RotaryIRQ
from utility import (configure_rotary_encoder, connect_wifi,
                     get_time_and_date_strings, load_env, paint_oled,
                     paint_oled_1, paint_oled_list, pot_value_to_vu_display,
                     sync_ntp_time)

DEFAULT_X = 10
DEFAULT_Y = 10

UTC_OFFSET = -5  # Adjust for your timezone (e.g., UTC-5 for CDT, UTC-6 for CST)

# Pin assignment summary
#
# Pin 2 - Onboard LED and external red indicator LED.  Activated on some errors.
# Pin 13 - Push button on rotary encoder
# Pin 15 - External green indicator LED.  Activated when EQ is selected.
# Pin 17 - External yelow indicator LED.  Activated when VU is selected.
# Pin 18 - I2C SCL for second OLED display
# Pin 19 - I2C SDA for second OLED display
# Pin 21 - I2C SDA for first OLED display
# Pin 22 - I2C SCL for first OLED display
# Pin 23 - Push button for second button
# Pin 32 - Rotary encoder CLK pin
# Pin 33 - Rotary encoder DT pin
# Pin 34 - Potentiometer analog input pin

# Load environment variables
env_vars = load_env(".env")

# Connect to WiFi
print("Initializing Network...")
if connect_wifi(env_vars):
    sync_ntp_time()
else:
    print("WiFi connection failed. Skipping NTP time sync.")

# Rotary encoder setup
print("Configuring rotary encoder")
rotary_encoder = configure_rotary_encoder(pin_clk=32, pin_dt=33, min_val=0, max_val=3)
prev_encoder_val = rotary_encoder.value()
encoder_button_pressed = False
last_interrupt_time = 0

def button_isr(pin):
    """Interrupt Service Routine triggered when the button is pressed."""
    global encoder_button_pressed, last_interrupt_time, button2_pressed
    current_time = time.ticks_ms()

    # Debounce check: ignore signals if they happen within 200ms of each other
    if time.ticks_diff(current_time, last_interrupt_time) > 200:
        print(pin, "Button pressed at", current_time)
        if pin == button_pin:
            encoder_button_pressed = True
        if pin == button2_pin:
            button2_pressed = True
        last_interrupt_time = current_time

## Attach the interrupt to look for a falling edge (HIGH to LOW transition when pressed)
button_pin = Pin(13, Pin.IN, Pin.PULL_UP)
button_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_isr)

# Potentiometer setup
print("Configuring potentiometer...")
## 1. Initialize the ADC on an analog pin (GPIO 34)
pot = ADC(Pin(34))

## 2. Configure full 3.3V voltage range attenuation
## This allows the pin to safely read the full range from 0 to 3.3V
pot.init(atten=ADC.ATTN_11DB)

# LED setup
print("Configuring LEDs...")
error_led = Pin(2, Pin.OUT)
indicator_leds = [
    error_led, # red
    Pin(15, Pin.OUT), # green
    Pin(17, Pin.OUT)] # yellow

# Second button setup
print("Configuring external button...")
button2_pin = Pin(23, Pin.IN, Pin.PULL_UP)
button2_pressed = False
button2_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_isr)

# Display setup
print("Configuring displays...")
try:
    i2c_1 = I2C(0, scl=Pin(22, Pin.OUT, Pin.PULL_UP), sda=Pin(21, Pin.OUT, Pin.PULL_UP))
    i2c_2 = I2C(1, scl=Pin(18), sda=Pin(19))
except:
    print("Error creating I2C objects.  Check pin assignments and wiring.")
    error_led.on()
    raise

oled_width = 128
oled_1_height = 64
oled_2_height = 32
time.sleep_ms(100)

try:
    oled = ssd1306.SSD1306_I2C(oled_width, oled_1_height, i2c_1)
    time.sleep_ms(100)
    oled2 = ssd1306.SSD1306_I2C(oled_width, oled_2_height, i2c_2)
except:
    print("Error creating OLED objects.  Check I2C setup and wiring.")
    raise

print("Sensors configured.")

# Initial display
paint_oled(oled, "Hello", DEFAULT_X, DEFAULT_Y)
paint_oled(oled2, "Goodbye", DEFAULT_X, DEFAULT_Y)

# loop variables
prev_pot_value = pot.read_u16()

# Main logic loop
while True:
    curr_encoder_val = rotary_encoder.value()

    if prev_encoder_val != curr_encoder_val:
        prev_encoder_val = curr_encoder_val
        print('Feature selector value = ', curr_encoder_val)

    # Handle Encoder Button Press (flags raised by the background interrupt)
    if encoder_button_pressed:
        # Reset the flag so we don't repeat this block until the next physical press
        encoder_button_pressed = False

    # Handle second button press (flags raised by the background interrupt)
    if button2_pressed:
        print('Button 2 click detected via Interrupt!')
        button2_pressed = False
        # Eject from main logic loop to REPL
        raise Exception("Button 2 invoking error handler")
    # Potentiometer
    # 3. Read the raw ADC value (returns an integer between 0 and 65536)
    raw_value = pot.read_u16()
    if raw_value - prev_pot_value > 50 or prev_pot_value - raw_value > 50:
        prev_pot_value = raw_value
        if raw_value % 10 == 0:
            print(f"Pot value: {raw_value}")
        time.sleep_ms(200)
