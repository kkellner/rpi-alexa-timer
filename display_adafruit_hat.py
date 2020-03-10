#!/usr/bin/env python
# 
# Display time using Adafruit HAT/Bonnet and LED 32x64 Matrix display
#
# Setup needed:
#
#  curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh > rgb-matrix.sh
#  sudo bash rgb-matrix.sh
#
import time
import logging
import sys

#from samplebase import SampleBase

from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions

logger = logging.getLogger(__name__)

class DisplayAdafruitHat():
    def __init__(self):
        print("__init__")

        options = RGBMatrixOptions()
        options.hardware_mapping = "adafruit-hat-pwm"
        options.rows = 32
        options.cols = 64

        options.chain_length = 1
        options.parallel = 1
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = 100
        options.disable_hardware_pulsing = 0
        #options.pwm_lsb_nanoseconds = 130
        options.pwm_lsb_nanoseconds = 500  # 400=Good
        options.led_rgb_sequence = "RGB"
        options.pixel_mapper_config = ""
        options.show_refresh_rate = 0
        options.gpio_slowdown = 0
        options.daemon = 0
        options.drop_privileges = False
 
        self.matrix = RGBMatrix(options = options)

        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font = graphics.Font()
        self.fontSmall = graphics.Font()

        # Setup Fonts
        # Get fonts from here: https://github.com/dk/ibm-vio-os2-fonts
        #self.font.LoadFont("../../../fonts/10x20.bdf")
        #self.font.LoadFont("ibm-vio-12x20-r-iso10646-1-20.bdf")

        self.fontSmall.LoadFont("fonts/ibm-vio-6x10-r-iso10646-1-10-modified.bdf")
        self.font.LoadFont("fonts/ibm-vio-12x30-r-iso10646-1-30-modified.bdf")
        #self.font.LoadFont("fonts/ibm-vio-10x21-r-iso10646-1-21.bdf")
        #self.font.LoadFont("fonts/ibm-vio-12x22-r-iso10646-1-22-modified.bdf")
        #self.font.LoadFont("../../../fonts/helvR12.bdf")
        self.matrix.brightness = 100 
        #self.textColor = graphics.Color(255, 0, 0)
        logger.info("display adafruit hat init complete")


    def display_time_remaining(self, primary_time_remaining, secondary_time_remaining = None):

       
        self.offscreen_canvas.Clear()
 
        # Set the default Y offset for primary timer to middle of display
        outTextPrimaryYOffset = 25

        # Display Secondary timer (if one is set)
        if secondary_time_remaining is not None:
            outTextSecondary = self.format_time_remaining(secondary_time_remaining, True)
            #outTextSecondary = " " + outTextSecondary
            textColor = graphics.Color(128, 0, 0)
            graphics.DrawText(self.offscreen_canvas, self.fontSmall, 4, 31, textColor, outTextSecondary)
            # We change the Y offset of primary timer to top of display to leave room for secondary timer
            outTextPrimaryYOffset = 20

        # Display Primary Timer
        outTextPrimary = self.format_time_remaining(primary_time_remaining)
        textColor = graphics.Color(255, 0, 0)
        graphics.DrawText(self.offscreen_canvas, self.font, 2, outTextPrimaryYOffset, textColor, outTextPrimary)
        
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def format_time_remaining(self, time_remaining, no_flash_colon = False):

        if time_remaining is None:
            return ""

        halfSecond = (time_remaining % 1) >= 0.5

        #logger.info("%d seconds left.  halfSecond: %d", time_remaining, halfSecond)

        # Format the timer digits for display
        minutes = time.strftime("%M", time.gmtime(time_remaining))
        seconds = time.strftime("%S", time.gmtime(time_remaining))

        if halfSecond or (minutes == "00" and seconds == "00") or no_flash_colon:
            sperator = ":" 
        else:
            sperator = "~"

        if minutes == "00":
            minutes = "  "

        if minutes.startswith('0'):
            minutes = minutes.replace('0', ' ', 1)

        outText = minutes + sperator + seconds
        return outText

    def clear(self):
        self.show_text("")

    def show_text(self, outText, line = 1):
        self.offscreen_canvas.Clear()
        textColor = graphics.Color(255, 0, 0)
        len = graphics.DrawText(self.offscreen_canvas, self.fontSmall, 2, (15*line), textColor, outText)
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def test(self):

        #self.textColor = graphics.Color(255, 0, 0)
        #self.textColor = graphics.Color(255, 255, 255)
        #pos = offscreen_canvas.width
        #self.matrix.brightness = 15 

        i = 1800.0
        while i >= 0:
            self.display_time_remaining(i)
            time.sleep(0.5)
            i = i - 0.5

# Main function
if __name__ == "__main__":
    FORMAT = '%(asctime)-15s %(threadName)-10s %(levelname)6s %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.NOTSET, format=FORMAT)
    #logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)

    display = DisplayAdafruitHat()
    #display.show_text("00:00")
    display.test()
    #display.display_time_remaining(60)
    #time.sleep(60)
