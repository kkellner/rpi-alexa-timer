
import time
import logging

from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT


logger = logging.getLogger('light')

# Alexa Gadget code
class DisplayMax7219():

    def __init__(self):
        # create matrix device
        serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(serial, cascaded=4, block_orientation=90,
                        rotate=0, blocks_arranged_in_reverse_order=False)
        self.device.contrast(16)        
        print("Created device")


    def display_time_remaining(self, time_remaining):

        halfSecond = (time_remaining % 1) >= 0.5

        logger.info("%d seconds left.  halfSecond: %d", time_remaining, halfSecond)

        # Format the timer digits for display
        minutes = time.strftime("%M", time.gmtime(time_remaining))
        seconds = time.strftime("%S", time.gmtime(time_remaining))
        
        #hours = datetime.now().strftime('%H')
        #minutes = datetime.now().strftime('%M')

        if halfSecond or (minutes == "00" and seconds == "00"):
            sperator = ":" 
        else:
            sperator = " "

        if minutes == "00":
            minutes = "  "

        seconds = seconds.replace("0", "O")
        minutes = minutes.replace("0", "O")


        with canvas(self.device) as draw:
            text(draw, (3, 1), minutes, fill="white", font=proportional(LCD_FONT))
            text(draw, (15, 1), sperator, fill="white", font=proportional(TINY_FONT))
            text(draw, (17, 1), seconds, fill="white", font=proportional(LCD_FONT))
        
    def off(self):
        self.device.clear()
        self.device.show()

    def test(self):

        i = 62.0
        while i >= 0:
            self.display_time_remaining(i)
            time.sleep(0.5)
            i = i - 0.5

        time.sleep(2)
        self.off()
        time.sleep(5)

        # start demo
        #msg = "12:05"
        #print(msg)
        #show_message(device, msg, fill="white", font=proportional(CP437_FONT))
        #time.sleep(10)
        #msg = "Slow scrolling: The quick brown fox jumps over the lazy dog"
        #print(msg)
        #show_message(device, msg, fill="white", font=proportional(LCD_FONT), scroll_delay=0.1)

        # hours = datetime.now().strftime('%H')
        # minutes = datetime.now().strftime('%M')
        # with canvas(device) as draw:
        #     text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
        #     #text(draw, (15, 1), ":" if toggle else " ", fill="white", font=proportional(TINY_FONT))
        #     text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
        #     #text(draw, (15, 1), ":", fill="white", font=proportional(CP437_FONT))
        #     text(draw, (17, 1), minutes, fill="white", font=proportional(CP437_FONT))
        # time.sleep(10)



if __name__ == '__main__':
    DisplayMax7219().test()