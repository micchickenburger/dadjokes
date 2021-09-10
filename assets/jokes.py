#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import subprocess
import re
import logging
import random
import re
import struct
import smbus2
import RPi.GPIO as GPIO
from gpiozero import Button
from time import sleep
from waveshare_epd import epd2in13_V2
from PIL import Image,ImageDraw,ImageFont

#
# Variables
#
PUSH_BUTTON_PIN = 26
JOKES_FONT_PATH = '/usr/lib/jokes/indie-flower.ttf'
QUOTES_FONT_PATH = '/usr/lib/jokes/allura.ttf'
FONT_PATH = None
MODES = ["jokes", "quotes"]

# UPS-Lite Variables
UPS_I2C = 1             # 0: /dev/i2c-0, 1: /dev/i2c-1
UPS_PIN = 4
UPS_SPI_ADDRESS = 0x36
# Only enable UPS if it can be found in the i2c device
i2cdetect = subprocess.run(['i2cdetect', '-y', str(UPS_I2C)], capture_output=True, text=True).stdout
ENABLE_UPS = bool(re.search(r'36', i2cdetect))

items = None
iterator = 0
bus = None

# Add attribute to Button class to track when button was recently held
Button.was_held = False

logging.basicConfig(level=logging.DEBUG)

#
# UPS-Lite Functions
#

def readVoltage(bus):
  try:
    "This function returns as float the voltage from the Raspi UPS Hat via the provided SMBus object"
    read = bus.read_word_data(UPS_SPI_ADDRESS, 0x02)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    voltage = swapped * 1.25 / 1000 / 16
    return voltage
  except:
    return 0.0

def readCapacity(bus):
  try:
    "This function returns as a float the remaining capacity of the battery connected to the Raspi UPS Hat via the provided SMBus object"
    read = bus.read_word_data(UPS_SPI_ADDRESS, 0x04)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    capacity = swapped / 256
    return capacity
  except:
    return 0.0

def QuickStart(bus):
  bus.write_word_data(UPS_SPI_ADDRESS, 0x06, 0x4000)

def PowerOnReset(bus):
  bus.write_word_data(UPS_SPI_ADDRESS, 0xfe, 0x0054)

def getBattery(bus):
  voltage = readVoltage(bus)
  charge = readCapacity(bus)
  logging.info('Battery: ' + str(charge) + '% @ ' + str(voltage) + 'V')
  logging.info('Charging: ' + str(GPIO.input(UPS_PIN)))

  # Draw battery icon
  if GPIO.input(UPS_PIN):
    battery = Image.open('/usr/lib/jokes/battery/charging.bmp')
  elif charge > 80:
    battery = Image.open('/usr/lib/jokes/battery/full.bmp')
  elif charge > 60:
    battery = Image.open('/usr/lib/jokes/battery/three_quarters.bmp')
  elif charge > 40:
    battery = Image.open('/usr/lib/jokes/battery/half.bmp')
  elif charge > 20:
    battery = Image.open('/usr/lib/jokes/battery/one_quarter.bmp')
  else:
    battery = Image.open('/usr/lib/jokes/battery/empty.bmp')

  return battery

#
# Item Formatting Logic
#

def draw_item():
  global iterator

  # Don't draw item when changing modes
  if button.was_held:
    button.was_held = False # reset; button is not being held anymore if the script got to this point
    return

  # Format variables
  font_size = 30 # start with largest + 1
  item = None

  while item == None:
    # Select a random item
    item = items[iterator].strip()
    iterator += 1

  while True:
    # Load next smaller font size
    font_size -= 1 # decrease font size with each iteration
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Get the total width in pixels of the all the characters in the string and divide by screen width
    # to get the number of lines that need to be rendered.  Divide the number of lines by the average
    # character size to know the maximum character length of each line.
    item_width = font.getsize(item)[0]
    line_count = item_width / SCREEN_WIDTH
    max_length_px = (item_width - line_count * font.getsize('W')[0]) / line_count # subtract width of capital W to each line to account for kerning
    max_length_char = int(max_length_px / (item_width / len(item)))

    # Split the string by nearest word boundary to the max line length, and then stop at spaces
    lines = re.compile(r'.{1,%s}(?:\s+|$)'%max_length_char).findall(item)

    # For documenting any rendering issues
    logging.debug("Total item width: " + str(item_width) + "px / Max px per Line: " + str(max_length_px))
    logging.debug(str(line_count) + " lines: " + str(lines))
    logging.debug("# Chars: " + str(len(item)) + " / Max Chars per Line: " + str(max_length_char) + " / Font size: " + str(font_size))

    # If the total height of all the lines is greater than the screen height, try again
    line_height = font.getsize(item)[1] * 0.9 # keep lines a little closer together
    if (line_height * len(lines)) < SCREEN_HEIGHT:
      break

  logging.info("Writing item to screen...")
  image = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)  # 255: clear the frame
  draw = ImageDraw.Draw(image)

  # Evenly space lines
  space_remaining = SCREEN_HEIGHT - (len(lines) * line_height)
  top = space_remaining / 2
  for i in range(len(lines)):
    # Remove excess whitespace from line
    line = lines[i].strip()

    # Center text
    left = (SCREEN_WIDTH - font.getsize(line)[0]) / 2

    # Output line
    draw.text((left, top), line, font = font, fill = 0)
    top += line_height

  # Draw battery icon
  if ENABLE_UPS:
    image.paste(getBattery(bus), (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 19))

  # Draw to screen
  epd.display(epd.getbuffer(image))

#
# Setup program for a given mode
#
def setup(mode):
  global items
  global FONT_PATH

  if mode == 'jokes':
    FONT_PATH = JOKES_FONT_PATH
    ITEMS_PATH = '/usr/lib/jokes/jokes.txt'
    START_MSG = 'Dad Jokes'
  elif mode == 'quotes':
    FONT_PATH = QUOTES_FONT_PATH
    ITEMS_PATH = '/usr/lib/jokes/quotes.txt'
    START_MSG = 'Motivational Quotes'
  else:
    sys.exit('Unknown mode: ' + mode)

  # Clear frame
  image = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255) # 255: clear frame
  draw = ImageDraw.Draw(image)

  # Let user know system is starting
  font = ImageFont.truetype(FONT_PATH, 30)
  left = (SCREEN_WIDTH - font.getsize(START_MSG)[0]) / 2
  top = (SCREEN_HEIGHT - font.getsize(START_MSG)[1]) / 2
  draw.text((left, top), START_MSG, font = font, fill = 0)
  epd.display(epd.getbuffer(image))

  # Load items into memory
  items_file = open(ITEMS_PATH, 'r')
  items = items_file.readlines()

  # Randomly arrange items
  # We randomly arrange the list once in memory to prevent items from repeating in a session
  # At reboot the list will be in a different random arrangement once again
  random.shuffle(items)

  # Render first item
  draw_item()

#
# Change modes
#
def change_modes():
  global mode

  button.was_held = True

  # Get index for next mode in list
  index = (MODES.index(mode) + 1) % len(MODES)
  mode = MODES[index]
  setup(mode)

#
# Main Program Logic
#
try:
  # Determine operation mode, defaulting to jokes
  mode = os.getenv('DADJOKES_MODE', 'jokes')

  # Prepare screen
  epd = epd2in13_V2.EPD()
  SCREEN_WIDTH = epd.height
  SCREEN_HEIGHT = epd.width
  logging.info("Screen resolution: " + str(SCREEN_WIDTH) + "px by " + str(SCREEN_HEIGHT) + "px")
  logging.info("Init and clear display")
  epd.init(epd.FULL_UPDATE)

  # Setup GPIO and SMBus for UPS-Lite and push-button communication
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)

  if ENABLE_UPS:
    logging.info("Found UPS device.  Enabling battery indicator.")
    bus = smbus2.SMBus(UPS_I2C)         # 0: /dev/i2c-0, 1: /dev/i2c-1
    GPIO.setup(UPS_PIN, GPIO.IN)        # UPS-Lite Charging Indicator
    #PowerOnReset(bus)                  # Enabling this seems to break UPS voltage and capacity reporting
    QuickStart(bus)
  else:
    logging.info("Could not find UPS device.  Disabling battery indicator.")

  # Register push button to draw item to screen
  button = Button(PUSH_BUTTON_PIN)
  button.when_released = draw_item

  # Register push button to switch modes when held down for at least two seconds
  button.hold_time = 2
  button.when_held = change_modes

  # Setup mode
  setup(mode)

  while True:
    sleep(1)

except IOError as e:
  logging.info(e)

except KeyboardInterrupt:
  logging.info("ctrl + c:")
  epd2in13_V2.epdconfig.module_exit()
  GPIO.cleanup()
  exit()
