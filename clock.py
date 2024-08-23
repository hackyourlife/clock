#!/bin/python
# vim:set ts=8 sts=8 sw=8 noet:

import time
import sys
import curses
from datetime import datetime, timedelta

bigfont = True

WIDTH, HEIGHT, chars, SCALE = None, None, None, None

def init_font(size):
	global WIDTH, HEIGHT, chars, SCALE

	bigfont = (size[0] >= (8 * 6)) and (size[1] >= 7)

	if bigfont:
		WIDTH = 6
		HEIGHT = 7

		chars = [
				[ 0b01110,
				  0b10001,
				  0b10011,
				  0b10101,
				  0b11001,
				  0b10001,
				  0b01110 ],
				[ 0b00100,
				  0b01100,
				  0b00100,
				  0b00100,
				  0b00100,
				  0b00100,
				  0b01110 ],
				[ 0b01110,
				  0b10001,
				  0b00001,
				  0b00010,
				  0b00100,
				  0b01000,
				  0b11111 ],
				[ 0b11111,
				  0b00010,
				  0b00100,
				  0b00010,
				  0b00001,
				  0b10001,
				  0b01110 ],
				[ 0b00010,
				  0b00110,
				  0b01010,
				  0b10010,
				  0b11111,
				  0b00010,
				  0b00010 ],
				[ 0b11111,
				  0b10000,
				  0b10000,
				  0b11110,
				  0b00001,
				  0b00001,
				  0b11110 ],
				[ 0b01110,
				  0b10000,
				  0b10000,
				  0b11110,
				  0b10001,
				  0b10001,
				  0b01110 ],
				[ 0b11111,
				  0b00001,
				  0b00001,
				  0b00010,
				  0b00100,
				  0b00100,
				  0b00100 ],
				[ 0b01110,
				  0b10001,
				  0b10001,
				  0b01110,
				  0b10001,
				  0b10001,
				  0b01110 ],
				[ 0b01110,
				  0b10001,
				  0b10001,
				  0b01111,
				  0b00001,
				  0b00001,
				  0b01110 ],
				[ 0b00000,
				  0b01100,
				  0b01100,
				  0b00000,
				  0b01100,
				  0b01100,
				  0b00000 ]
			]

	else:
		WIDTH = 4
		HEIGHT = 6
		chars = [
				[ 0b0100,
				  0b1010,
				  0b1010,
				  0b1010,
				  0b0100,
				  0b0000 ],
				[ 0b0100,
				  0b1100,
				  0b0100,
				  0b0100,
				  0b1110,
				  0b0000 ],
				[ 0b1100,
				  0b0010,
				  0b0100,
				  0b1000,
				  0b1110,
				  0b0000 ],
				[ 0b1110,
				  0b0010,
				  0b1110,
				  0b0010,
				  0b1110,
				  0b0000 ],
				[ 0b1010,
				  0b1010,
				  0b1110,
				  0b0010,
				  0b0010,
				  0b0000 ],
				[ 0b1110,
				  0b1000,
				  0b1110,
				  0b0010,
				  0b1110,
				  0b0000 ],
				[ 0b1110,
				  0b1000,
				  0b1110,
				  0b1010,
				  0b1110,
				  0b0000 ],
				[ 0b1110,
				  0b0010,
				  0b0010,
				  0b0010,
				  0b0010,
				  0b0000 ],
				[ 0b1110,
				  0b1010,
				  0b1110,
				  0b1010,
				  0b1110,
				  0b0000 ],
				[ 0b1110,
				  0b1010,
				  0b1110,
				  0b0010,
				  0b0010,
				  0b0000 ],
				[ 0b0000,
				  0b0100,
				  0b0000,
				  0b0100,
				  0b0000,
				  0b0000 ]
			]

	SCALE = min(int(size[0] / (WIDTH * 8)), int(size[1] / HEIGHT))

mapping = { str(x): x for x in range(10) }
mapping[":"] = 10

def get(x):
	global mapping
	return mapping[x]

def write(x):
	sys.stdout.write(x)

def flush():
	sys.stdout.flush()

def clear():
	write("\x1b[2J")

def move(x, y):
	write("\x1b[%d;%dH" % (y + 1, x + 1))

def draw_block():
	write("\x1b[7m \x1b[0m")

def draw(c, x, y):
	global WIDTH, SCALE, chars
	char = chars[c]
	oy = 0
	def BIT(x):
		return 1 << x
	for line in char:
		for sy in range(SCALE):
			for bit in range(WIDTH):
				move(x + bit * SCALE, y + oy)
				b = line & BIT(WIDTH - 1 - bit)
				for sx in range(SCALE):
					if b:
						draw_block()
					else:
						write(" ")
			oy += 1

def draw_string(s, x, y):
	global WIDTH, SCALE
	for i in range(len(s)):
		c = get(s[i])
		draw(c, x + (WIDTH * SCALE * i), y)
	flush()

last_time = None

def draw_time(size, t=None):
	global WIDTH
	global HEIGHT
	global SCALE
	global last_time

	w = 8 * WIDTH * SCALE
	h = HEIGHT * SCALE
	px = round((size[0] - w) / 2)
	py = round((size[1] - h) / 2)
	if t is None:
		t = datetime.now()

	if type(t) == datetime:
		h = t.hour
		m = t.minute
		s = t.second
	else:
		tmp = t
		s = tmp % 60
		tmp //= 60
		m = tmp % 60
		tmp //= 60
		h = tmp

	z = "%02d:%02d:%02d" % (h, m, s)

	if last_time != z:
		draw_string(z, px, py)
	z = last_time

def get_size():
	width, height = curses.COLS, curses.LINES
	return (width, height)

def parse_time(arg):
	hours = 0
	minutes = 0
	seconds = 0

	state = 0
	buffer = 0
	for c in arg:
		if c >= '0' and c <= '9':
			buffer *= 10
			buffer += ord(c) - 0x30
		elif c == 'h':
			hours = buffer
			buffer = 0
		elif c == 'm':
			minutes = buffer
			buffer = 0
		elif c == 's':
			seconds = buffer
			buffer = 0
	if buffer > 0:
		seconds = buffer
	return (hours, minutes, seconds)


if __name__ == "__main__":
	curses.initscr()
	size = get_size()
	init_font(size)
	curses.nonl()
	curses.noecho()
	curses.curs_set(0)
	clear()

	try:
		if len(sys.argv) == 2:
			timer = parse_time(sys.argv[1])
			start = datetime.now()
			end = start + timedelta(hours=timer[0],
					minutes=timer[1], seconds=timer[2])
			while datetime.now() < end:
				remaining = end - datetime.now()
				draw_time(size, remaining.total_seconds())
				time.sleep(0.01)
		else:
			while True:
				draw_time(size)
				time.sleep(0.01)
	except KeyboardInterrupt:
		pass

	curses.curs_set(1)
	curses.endwin()
