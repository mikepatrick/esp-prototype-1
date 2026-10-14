from machine import Pin, I2C, ADC
from lib import ssd1306
import framebuf
from lib.rotary_irq_esp import RotaryIRQ
import time
from utility import configure_rotary_encoder, paint_oled, paint_oled_1

FEATURES = ["Menu", "EQ", "VU", "Standby"]
FEATURE_DESCRIPTIONS= ["Detail Screen", "Equalizer", "VU Meter", "Standby"]

DEFAULT_X = 10
DEFAULT_Y = 10

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
# Pin 32 - Rotary encoder CLK pin
# Pin 33 - Rotary encoder DT pin
# Pin 34 - Potentiometer analog input pin


# Rotary encoder setup
r = configure_rotary_encoder(pin_clk=32, pin_dt=33, min_val=0, max_val=3)
prev_val = r.value()

## Variables and function to manage button state and debouncing
button_pressed = False
last_interrupt_time = 0

def button_isr(pin):
    """Interrupt Service Routine triggered when the button is pressed."""
    global button_pressed, last_interrupt_time
    current_time = time.ticks_ms()

    # Debounce check: ignore signals if they happen within 200ms of each other
    if time.ticks_diff(current_time, last_interrupt_time) > 200:
        button_pressed = True
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
indicator_leds = [error_led, Pin(15, Pin.OUT), Pin(17, Pin.OUT)]

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
    print(str(i2c_2))
    raise

rot_buf = framebuf.FrameBuffer1(bytearray(64 * 128 // 8), 64, 128)

oled2.rotate(False)

# Initial display
paint_oled_1(oled, rot_buf, FEATURES[0], DEFAULT_X, DEFAULT_Y)
paint_oled(oled2, FEATURE_DESCRIPTIONS[0], DEFAULT_X, DEFAULT_Y)

# loop variables
prev_pot_value = 0
draw_pot = False
eq_selected = False
vu_selected = False
vu_display = FEATURE_DESCRIPTIONS[2]
is_in_standby = False

# Main logic loop
while True:
    curr_val = r.value()

    # Turning encoder selects feature.  Update display 1 if encoder has been turned.
    if prev_val != curr_val:
        if curr_val == 0:
            paint_oled_1(oled, rot_buf, FEATURES[0], DEFAULT_X, DEFAULT_Y)
        elif curr_val == 1:
            paint_oled_1(oled, rot_buf, FEATURES[1], DEFAULT_X, DEFAULT_Y)
        elif curr_val == 2:
            paint_oled_1(oled, rot_buf, FEATURES[2], DEFAULT_X, DEFAULT_Y)
        elif curr_val == 3:
            paint_oled_1(oled, rot_buf, FEATURES[3], DEFAULT_X, DEFAULT_Y)
        else:
            paint_oled_1(oled, rot_buf, '?: ' + str(curr_val), DEFAULT_X, DEFAULT_Y)
        prev_val = curr_val
        print('Feature selector value = ', curr_val)

    # Turn on yellow LED if VU is selected, green LED if EQ is selected, and turn off both if neither is selected.
    for i, led in enumerate(indicator_leds):
        if i == curr_val and i != 0:
            led.on()
        else:
            led.off()
    time.sleep_ms(50)

    # Handle Button Press (flags raised by the background interrupt)
    if button_pressed:
        print('Button click detected via Interrupt!')
        # If in standby, wake up and paint displays.
        if is_in_standby:
            # If we are in standby, wake up the system
            oled.poweron()
            oled2.poweron()
            is_in_standby = False
            paint_oled_1(oled, rot_buf, FEATURES[curr_val], DEFAULT_X, DEFAULT_Y)
            paint_oled(oled2, FEATURE_DESCRIPTIONS[curr_val], DEFAULT_X, DEFAULT_Y)
        # If not in standby, check if standby is selected.  If so, power off displays and enter standby.
        # Otherwise, update display 2 with the description of the selected feature.
        else:
            if curr_val == 3:
                oled.poweroff()
                oled2.poweroff()
                is_in_standby = True
            else:
                paint_oled(oled2, FEATURE_DESCRIPTIONS[curr_val], DEFAULT_X, DEFAULT_Y)

        # Reset the flag so we don't repeat this block until the next physical press
        button_pressed = False

    # Don't bother reading the potentiometer if we are in standby
    if is_in_standby:
        continue

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

    if curr_val == 2 and draw_pot:
        if raw_value > 4000:
            vu_display = "VU: MAX"
        elif raw_value > 3500:
            vu_display = "VU: XXXXXXX"
        elif raw_value > 3000:
            vu_display = "VU: XXXXXX"
        elif raw_value > 2500:
            vu_display = "VU: XXXXX"
        elif raw_value > 2000:
            vu_display = "VU: XXXX"
        elif raw_value > 1500:
            vu_display = "VU: XXX"
        elif raw_value > 1000:
            vu_display = "VU: XX"
        elif raw_value > 500:
            vu_display = "VU: X"
        else:
            vu_display = "VU: MIN"
        # paint_oled(oled2, vu_display, DEFAULT_X, DEFAULT_Y)
        draw_pot = False