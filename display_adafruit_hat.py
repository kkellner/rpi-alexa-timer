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
    def __init__(self, *args, **kwargs):

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
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = "RGB"
        options.pixel_mapper_config = ""
        options.show_refresh_rate = 0
        options.gpio_slowdown = 1
        options.daemon = 0
        options.drop_privileges = False
        #  options.disable_hardware_pulsing = True

        self.matrix = RGBMatrix(options = options)
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font = graphics.Font()

        # Setup Fonts
        # Get fonts from here: https://github.com/dk/ibm-vio-os2-fonts
        #self.font.LoadFont("../../../fonts/7x13.bdf")
        #self.font.LoadFont("../../../fonts/10x20.bdf")
        #self.font.LoadFont("ibm-vio-12x20-r-iso10646-1-20.bdf")
        self.font.LoadFont("ibm-vio-12x30-r-iso10646-1-30.bdf")
        #self.font.LoadFont("ibm-vio-10x21-r-iso10646-1-21.bdf")
        #self.font.LoadFont("ibm-vio-12x22-r-iso10646-1-22-modified.bdf")
        #self.font.LoadFont("../../../fonts/helvR12.bdf")
        self.matrix.brightness = 75 
        self.textColor = graphics.Color(255, 0, 0)


    def display_time_remaining(self, time_remaining):

        halfSecond = (time_remaining % 1) >= 0.5

        logger.info("%d seconds left.  halfSecond: %d", time_remaining, halfSecond)

        # Format the timer digits for display
        minutes = time.strftime("%M", time.gmtime(time_remaining))
        seconds = time.strftime("%S", time.gmtime(time_remaining))
        sperator = ":" 
        outText = minutes + sperator + seconds

        self.offscreen_canvas.Clear()
        #len = graphics.DrawText(self.offscreen_canvas, font, pos, 10, textColor, my_text)
        #len = graphics.DrawText(self.offscreen_canvas, self.font, 2, 15, self.textColor, outText)
        len = graphics.DrawText(self.offscreen_canvas, self.font, 2, 25, self.textColor, outText)
        #print("time:"+outText)
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)


    def off(self):
        self.offscreen_canvas.Clear()
        graphics.DrawText(self.offscreen_canvas, self.font, 2, 25, self.textColor, "")
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def test(self):

        self.textColor = graphics.Color(255, 0, 0)
        #self.textColor = graphics.Color(255, 255, 255)
        #pos = offscreen_canvas.width
        self.matrix.brightness = 75 

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
    display.test()