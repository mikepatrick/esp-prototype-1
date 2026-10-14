from machine import Pin, I2C
from lib import ssd1306
from lib.rotary_irq_esp import RotaryIRQ
import time

r = RotaryIRQ(pin_num_clk=32,
              pin_num_dt=33,
              min_val=0,
              max_val=5,
              reverse=False,
              pull_up=True,
              range_mode=RotaryIRQ.RANGE_WRAP)

val_old = r.value()


# ESP32 Pin assignment
i2c_1 = I2C(0, scl=Pin(22), sda=Pin(21))
i2c_2 = I2C(1, scl=Pin(27), sda=Pin(14))
oled_width = 128
oled_1_height = 64
oled_2_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_1_height, i2c_1)
oled2 = ssd1306.SSD1306_I2C(oled_width, oled_2_height, i2c_2)
oled.text('Hello, Wokwi!', 10, 10)
oled.show()
oled2.text('Yo, esse!', 10, 10)
oled2.show()
while True:
    val_new = r.value()

    if val_old != val_new:
        if val_new == 1:
            oled.fill(0)
            oled.text('No. 1', 10, 10)
            oled.show()
        elif val_new == 2:
            oled.fill(0)
            oled.text('No. 2', 10, 10)
            oled.show()
        else:
            oled.fill(0)
            oled.text('unknown' + str(val_old), 10, 10)
            oled.show()
        val_old = val_new
        print('result =', val_new)

    time.sleep_ms(50)