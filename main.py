from machine import Pin, I2C
import ssd1306
from rotary_irq_esp import RotaryIRQ
import time
import utility

FEATURES = ["Menu", "EQ", "VU", "Standby"]
FEATURE_DESCRIPTIONS= ["Detail Screen", "Equalizer", "VU Meter", "Standby"]
# Rotary encoder setup
r = RotaryIRQ(pin_num_clk=32, 
              pin_num_dt=33, 
              min_val=0, 
              max_val=3, 
              reverse=False,
              pull_up=True,
              range_mode=RotaryIRQ.RANGE_WRAP)

prev_val = r.value()

# --- 2. SETUP ENCODERPUSH BUTTON WITH INTERRUPT ---
button_pin = Pin(13, Pin.IN, Pin.PULL_UP)

# Variables to manage button state and debouncing
button_pressed = False
last_interrupt_time = 0

# Variable to manage standby state
is_in_standby = False

def button_isr(pin):
    """Interrupt Service Routine triggered when the button is pressed."""
    global button_pressed, last_interrupt_time
    current_time = time.ticks_ms()
    
    # Debounce check: ignore signals if they happen within 200ms of each other
    if time.ticks_diff(current_time, last_interrupt_time) > 200:
        button_pressed = True
        last_interrupt_time = current_time

# Attach the interrupt to look for a falling edge (HIGH to LOW transition when pressed)
button_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_isr)

# LED setup
error_led = Pin(2, Pin.OUT)
indicator_leds = [error_led, Pin(15, Pin.OUT), Pin(17, Pin.OUT)]

# ESP32 Pin assignment 
i2c_1 = I2C(0, scl=Pin(22, Pin.OUT, Pin.PULL_UP), sda=Pin(21, Pin.OUT, Pin.PULL_UP))
try:
    i2c_2 = I2C(1, scl=Pin(18), sda=Pin(19))
except:
    print("Oh, fuck")
    error_led.on()
    raise
oled_width = 128
oled_1_height = 64
oled_2_height = 32
time.sleep_ms(100)
oled = ssd1306.SSD1306_I2C(oled_width, oled_1_height, i2c_1)
time.sleep_ms(100)
try:
    oled2 = ssd1306.SSD1306_I2C(oled_width, oled_2_height, i2c_2)
except:
    print("ah, shit")
    print(str(i2c_2))

import framebuf
rot_buf = framebuf.FrameBuffer1(bytearray(64 * 128 // 8), 64, 128)

def show_oled1_rotated_90():
    oled.fill(0)
    for y in range(128):
        for x in range(64):
            oled.pixel(127 - y, x, rot_buf.pixel(x, y))
    oled.show()

def show_oled1_rotated_270():
    oled.fill(0)
    for y in range(128):
        for x in range(64):
            oled.pixel(y, 63 - x, rot_buf.pixel(x, y))
    oled.show()

def paint_oled_1(oled, text, x=10, y=10):
    """Helper function to paint text on the OLED screen."""
    rot_buf.fill(0)
    rot_buf.text(text, x, y)
    show_oled1_rotated_270()

def paint_oled(oled, text, x=10, y=10):
    """Helper function to paint text on the OLED screen."""
    oled.fill(0)
    oled.text(text, x, y)
    oled.show()

# Rotete screen 2 180 degrees
# oled2.write_cmd(0xA0)  # Reverse segment mapping
# oled2.write_cmd(0xC0)  # Reverse COM scan direction
oled2.rotate(False)
paint_oled_1(oled, FEATURES[0], 10, 10)
paint_oled(oled2, FEATURE_DESCRIPTIONS[0], 10, 10)

while True:
    curr_val = r.value()
    
    if prev_val != curr_val:
        if curr_val == 0:
            paint_oled_1(oled, FEATURES[0], 10, 10)
        elif curr_val == 1:
            paint_oled_1(oled, FEATURES[1], 10, 10)
        elif curr_val == 2:
            paint_oled_1(oled, FEATURES[2], 10, 10)
        elif curr_val == 3:
            paint_oled_1(oled, FEATURES[3], 10, 10)
        else:
            paint_oled_1(oled, '?: ' + str(curr_val), 10, 10)
        prev_val = curr_val
        print('result =', curr_val)
    for i, led in enumerate(indicator_leds):
        if i == curr_val and i != 0:
            led.on()
        else:
            led.off()
    time.sleep_ms(50)
    # Handle Button Press (flags raised by the background interrupt)
    if button_pressed:
        print('Button click detected via Interrupt!')
        
        # Flash visual feedback on the OLED screen
        # oled.fill(0)
        # oled.text('CLICK DETECTED!', 10, 10)
        # oled.text('Current Val: ' + str(curr_val), 10, 30)
        # oled.show()

        if is_in_standby:
            # If we are in standby, wake up the system
            oled.poweron()
            oled2.poweron()
            is_in_standby = False
            paint_oled_1(oled, FEATURES[curr_val], 10, 10)
            paint_oled(oled2, FEATURE_DESCRIPTIONS[curr_val], 10, 10)
        else:
            if curr_val == 3:
                oled.poweroff()
                oled2.poweroff()
                is_in_standby = True
            else:
                paint_oled(oled2, FEATURE_DESCRIPTIONS[curr_val], 10, 10)

        # Reset the flag so we don't repeat this block until the next physical press
        button_pressed = False
