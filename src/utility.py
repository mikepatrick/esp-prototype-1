import os
import time

import machine
import network
import ntptime

import lib.ssd1306 as ssd1306
from lib.rotary_irq_esp import RotaryIRQ


def show_oled1_rotated_90(oled: ssd1306.SSD1306_I2C, rot_buf: ssd1306.SSD1306_I2C):
	oled.fill(0)
	for y in range(128):
		for x in range(64):
			oled.pixel(127 - y, x, rot_buf.pixel(x, y))
	oled.show()

def show_oled1_rotated_270(oled: ssd1306.SSD1306_I2C, rot_buf: ssd1306.SSD1306_I2C):
	oled.fill(0)
	for y in range(128):
		for x in range(64):
			oled.pixel(y, 63 - x, rot_buf.pixel(x, y))
	oled.show()

def paint_oled_1(oled: ssd1306.SSD1306_I2C, rot_buf: ssd1306.SSD1306_I2C, text: str, x: int = 10, y: int = 10):
	"""Paint text on the rotated OLED display."""
	rot_buf.fill(0)
	rot_buf.text(text, x, y)
	show_oled1_rotated_270(oled, rot_buf)

def paint_oled(oled: ssd1306.SSD1306_I2C, text: str, x: int = 10, y: int = 10):
	"""Paint text on an OLED display."""
	oled.fill(0)
	oled.text(text, x, y)
	oled.show()

def configure_rotary_encoder(pin_clk: int, pin_dt: int, min_val: int = 0, max_val: int = 3) -> RotaryIRQ:
    """Configure a rotary encoder with the specified parameters."""
    r = RotaryIRQ(pin_num_clk=pin_clk,
                  pin_num_dt=pin_dt,
                  min_val=min_val,
                  max_val=max_val,
                  reverse=False,
                  pull_up=True,
                  range_mode=RotaryIRQ.RANGE_WRAP)
    return r

def pot_value_to_vu_display(raw_value: int) -> str:
	"""Convert a potentiometer value to a VU display string."""
	if raw_value > 60000:
		vu_display = "VU: MAX"
	elif raw_value > 50000:
		vu_display = "VU: XXXXXXX"
	elif raw_value > 40000:
		vu_display = "VU: XXXXXX"
	elif raw_value > 30000:
		vu_display = "VU: XXXXX"
	elif raw_value > 20000:
		vu_display = "VU: XXXX"
	elif raw_value > 15000:
		vu_display = "VU: XXX"
	elif raw_value > 10000:
		vu_display = "VU: XX"
	elif raw_value > 5000:
		vu_display = "VU: X"
	else:
		vu_display = "VU: MIN"
	return vu_display

def load_env(filepath: str = ".env") -> dict[str, str]:
    env_vars = {}
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines or comments
                if not line or line.startswith("#"):
                    continue
                # Split at the first '='
                if "=" in line:
                    key, value = line.split("=", 1)
                    # Strip spaces and optional surrounding quotes
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    env_vars[key] = value
    except OSError:
        print(f"Warning: {filepath} file not found.")
    return env_vars

def connect_wifi(env_vars: dict[str, str]) -> bool:
    """Connects the ESP32 to the local Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"Connecting to {env_vars.get('WIFI_NETWORK')}...")
        wlan.connect(env_vars.get('WIFI_NETWORK'), env_vars.get('WIFI_PASSWORD'))

        # Wait for connection (timeout after 15 seconds)
        timeout = 15
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > timeout:
                print("Wi-Fi connection timed out!")
                return False
            time.sleep(0.5)

    print("Connected! IP Info:", wlan.ifconfig())
    return True

def sync_ntp_time():
    """Fetches the current UTC time from an NTP server and sets the internal RTC."""
    try:
        print("Syncing time with NTP server...")
        # ntptime.settime() fetches UTC time from pool.ntp.org and sets the hardware RTC
        ntptime.settime()
        print("Time synchronized successfully!")
    except Exception as e:
        print("Failed to sync NTP time:", e)