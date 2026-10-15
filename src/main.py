import time

import framebuf
from machine import ADC, I2C, Pin

from lib import ssd1306
from lib.rotary_irq_esp import RotaryIRQ
from utility import (configure_rotary_encoder, connect_wifi,
                     get_time_and_date_strings, load_env, paint_oled,
                     paint_oled_1, paint_oled_list, pot_value_to_vu_display,
                     sync_ntp_time)

FEATURES = ["Menu", "EQ", "VU", "Clock", "Standby"]
FEATURE_DESCRIPTIONS= ["Detail Screen", "Equalizer", "VU Meter", "Clock", "Standby"]

MENU_INDEX = 0
EQ_INDEX = 1
VU_INDEX = 2
CLOCK_INDEX = 3
STANDBY_INDEX = 4

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
if connect_wifi(env_vars):
    sync_ntp_time()
else:
    print("WiFi connection failed. Skipping NTP time sync.")

# Rotary encoder setup
rotary_encoder = configure_rotary_encoder(pin_clk=32, pin_dt=33, min_val=0, max_val=3)
prev_feature = rotary_encoder.value()
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
## 1. Initialize the ADC on an analog pin (GPIO 34)
pot = ADC(Pin(34))

## 2. Configure full 3.3V voltage range attenuation
## This allows the pin to safely read the full range from 0 to 3.3V
pot.init(atten=ADC.ATTN_11DB)

# LED setup
error_led = Pin(2, Pin.OUT)
indicator_leds = [
    error_led, # red
    Pin(15, Pin.OUT), # green
    Pin(17, Pin.OUT)] # yellow

# Second button setup
button2_pin = Pin(23, Pin.IN, Pin.PULL_UP)
button2_pressed = False
button2_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_isr)
# Display setup
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

rot_buf = framebuf.FrameBuffer1(bytearray(64 * 128 // 8), 64, 128)

oled2.rotate(False)

# Initial display
paint_oled_1(oled, rot_buf, FEATURES[MENU_INDEX], DEFAULT_X, DEFAULT_Y)
paint_oled(oled2, FEATURE_DESCRIPTIONS[MENU_INDEX], DEFAULT_X, DEFAULT_Y)

# loop variables
prev_pot_value = pot.read_u16()
draw_pot = False
eq_selected = False
vu_selected = False
vu_display = FEATURE_DESCRIPTIONS[VU_INDEX]
is_in_standby = False
pushed_into_feature = MENU_INDEX  # Start in the menu feature, which is index 0

# Main logic loop
while True:
    selected_feature = rotary_encoder.value()

    # Turning encoder selects feature.  Update display 1 if encoder has been turned.
    if prev_feature != selected_feature:
        if selected_feature in range(len(FEATURES)):
            paint_oled_1(oled, rot_buf, FEATURES[selected_feature], DEFAULT_X, DEFAULT_Y)
        else:
            paint_oled_1(oled, rot_buf, '?: ' + str(selected_feature), DEFAULT_X, DEFAULT_Y)
        prev_feature = selected_feature
        print('Feature selector value = ', selected_feature)

    # Turn on yellow LED if VU is selected, green LED if EQ is selected, and turn off both if neither is selected.
    for i, led in enumerate(indicator_leds):
        if i == selected_feature and i != 0:
            led.on()
        else:
            led.off()
    time.sleep_ms(50)

    # Handle Encoder Button Press (flags raised by the background interrupt)
    if encoder_button_pressed:
        print('Button click detected via Interrupt!')
        pushed_into_feature = selected_feature
        print('Pushed into feature = ', pushed_into_feature)
        # If in standby, wake up and paint displays.
        if is_in_standby:
            # If we are in standby, wake up the system
            oled.poweron()
            oled2.poweron()
            is_in_standby = False
            paint_oled_1(oled, rot_buf, FEATURES[selected_feature], DEFAULT_X, DEFAULT_Y)
            paint_oled(oled2, FEATURE_DESCRIPTIONS[selected_feature], DEFAULT_X, DEFAULT_Y)
        # If not in standby, check if standby is selected.  If so, power off displays and enter standby.
        # Otherwise, update display 2 with the description of the selected feature.
        else:
            if selected_feature == STANDBY_INDEX:
                oled.poweroff()
                oled2.poweroff()
                is_in_standby = True
            else:
                paint_oled(oled2, FEATURE_DESCRIPTIONS[selected_feature], DEFAULT_X, DEFAULT_Y)

        # Reset the flag so we don't repeat this block until the next physical press
        encoder_button_pressed = False

    # Don't bother reading other sensors if we are in standby
    if is_in_standby:
        continue

    # Handle second button press (flags raised by the background interrupt)
    if button2_pressed:
        print('Button 2 click detected via Interrupt!')
        for i, led in enumerate(indicator_leds):
            led.on()
            time.sleep_ms(400)
        time.sleep_ms(400)
        # Reset the flag so we don't repeat this block until the next physical press
        button2_pressed = False
        # Eject from main logic loop to REPL
        raise Exception("Button 2 invoking error handler")
    # Potentiometer
    # 3. Read the raw ADC value (returns an integer between 0 and 4095)
    raw_value = pot.read_u16()
    if raw_value - prev_pot_value > 50 or prev_pot_value - raw_value > 50:
        prev_pot_value = raw_value
        draw_pot = True
    # 4. (Optional) Convert the raw value back into actual voltage
    # voltage = raw_value * (3.3 / 4095)
    # Print results to the console
    # print(f"Raw Value: {raw_value} | Voltage: {voltage:.2f}V")

    if pushed_into_feature == VU_INDEX and draw_pot:
        # Update VU detail display based on potentiometer value.
        vu_display = pot_value_to_vu_display(raw_value)
        FEATURE_DESCRIPTIONS[VU_INDEX] = vu_display
        paint_oled(oled2, vu_display, DEFAULT_X, DEFAULT_Y)
        draw_pot = False

    if pushed_into_feature == CLOCK_INDEX:
        time_str, date_str = get_time_and_date_strings(UTC_OFFSET)
        FEATURE_DESCRIPTIONS[CLOCK_INDEX] = time_str
        paint_oled_list(oled2, [time_str, date_str], DEFAULT_X, DEFAULT_Y)
        time.sleep(1)