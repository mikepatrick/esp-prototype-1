from lib.rotary_irq_esp import RotaryIRQ


def show_oled1_rotated_90(oled, rot_buf):
	oled.fill(0)
	for y in range(128):
		for x in range(64):
			oled.pixel(127 - y, x, rot_buf.pixel(x, y))
	oled.show()

def show_oled1_rotated_270(oled, rot_buf):
	oled.fill(0)
	for y in range(128):
		for x in range(64):
			oled.pixel(y, 63 - x, rot_buf.pixel(x, y))
	oled.show()

def paint_oled_1(oled, rot_buf, text, x=10, y=10):
	"""Paint text on the rotated OLED display."""
	rot_buf.fill(0)
	rot_buf.text(text, x, y)
	show_oled1_rotated_270(oled, rot_buf)

def paint_oled(oled, text, x=10, y=10):
	"""Paint text on an OLED display."""
	oled.fill(0)
	oled.text(text, x, y)
	oled.show()

def configure_rotary_encoder(pin_clk, pin_dt, min_val=0, max_val=3):
    """Configure a rotary encoder with the specified parameters."""
    r = RotaryIRQ(pin_num_clk=pin_clk,
                  pin_num_dt=pin_dt,
                  min_val=min_val,
                  max_val=max_val,
                  reverse=False,
                  pull_up=True,
                  range_mode=RotaryIRQ.RANGE_WRAP)
    return r

def pot_value_to_vu_display(raw_value):
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
