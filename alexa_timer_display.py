#!/usr/bin/python3
#
# Alexa Timer Display
# Uses Alexa Gadget API
#
# Setup and pair bluetooth using instructions here: https://github.com/alexa/Alexa-Gadgets-Raspberry-Pi-Samples
# 1.  Create Amazon ID and Alexa Gadget Secret via Alexa Voice Service Developer Console.
# 2.  Clone repo git clone https://github.com/alexa/Alexa-Gadgets-Raspberry-Pi-Samples.git
# 3.  Run:
#       cd /home/pi/Alexa-Gadgets-Raspberry-Pi-Samples/
#       sudo apt-get install -y python3-pip
#       sudo python3 launch.py --setup
#       sudo python3 launch.py --example kitchen_sink (to pair which alexa)
#
import logging
import sys
import os
import signal
import threading
import time
import math
import netifaces 

import dateutil.parser
from agt import AlexaGadget

#from display_max7219 import DisplayMax7219 as Display
from display_adafruit_hat import DisplayAdafruitHat as Display

logger = logging.getLogger(__name__)

# Alexa Gadget code.  
# Parent class: https://github.com/alexa/Alexa-Gadgets-Raspberry-Pi-Samples/blob/master/src/agt/alexa_gadget.py
class TimerGadget(AlexaGadget):
    """
    An Alexa Gadget that reacts to a single timer set on an Echo device.

    Threading is used to prevent blocking the main thread when the timer is
    counting down.
    """

    def __init__(self, app):
        self.app = app
        self.timer_thread = None

        # Dictionary of timers where key is token and value is end time
        self.timers = {}
        self.sortedTimers = None

        self.event = threading.Event()
        logger.info("init display")
        self.display = Display()

        #netifaces.ifaddresses('wlan0')
        ip = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']

        #self.display.show_text("Startup")
        #self.display.show_text(ip, 2)
        self.display.scroll_text("Startup: " + ip, 2, 2)
        super().__init__("alexa_timer_display.ini")        
        self.display.show_text("Initialize", 2)

    def on_connected(self, device_addr):
        logger.info("on_connected called")
        #self.display.show_text("Connected")
        self.display.clear()

    def on_disconnected(self, device_addr):
        logger.info("on_disconnect called")
        self.timers = {}
        time.sleep(1)
        self.display.show_text("Disconnected")

    def on_alerts_setalert(self, directive):
        """
        Handles Alerts.SetAlert directive sent from Echo Device
        """
        # check that this is a timer. if it is something else (alarm, reminder), just ignore
        if directive.payload.type != 'TIMER':
            logger.info("Received SetAlert directive but type != TIMER. Ignorning")
            return

        # parse the scheduledTime in the directive. if is already expired, ignore
        t = dateutil.parser.parse(directive.payload.scheduledTime).timestamp()
        if t <= 0:
            logger.info("Received SetAlert directive for token %s but scheduledTime has already passed. Ignoring", directive.payload.token)
            return

        # check if this is an update to an alrady running timer (e.g. users asks alexa to add 30s)
        # if it is, just adjust the end time

        self.timers[directive.payload.token] = t

        # if  directive.payload.token in self.timers:
        #     logger.info("Received SetAlert directive for token %s to update to currently running timer. Adjusting", directive.payload.token)
        #     self.timers[directive.payload.token] = t
            

        # if self.timer_token_primary == directive.payload.token:
        #     logger.info("Received SetAlert directive for token %s to update to currently running timer. Adjusting", directive.payload.token)
        #     self.timer_end_time_primary = t
        #     return

        # # check if another timer is already running. if it is, just ignore this one
        # if self.timer_thread is not None and self.timer_thread.isAlive():
        #     logger.info("Received SetAlert directive for token %s but another timer is already running. Ignoring", directive.payload.token)
        #     return

        # logger.info("Received SetAlert directive for token %s. Starting a timer.  %d seconds left.", 
        #     directive.payload.token, int(t - time.time()))

        # self.timer_end_time_primary = t
        # self.timer_token_primary = directive.payload.token

        self.sort_timers()

        # timersLen = len(sortedTimers)
        # if timersLen > 0:
        #     self.timer_end_time_primary = t
        #     self.timer_token_primary = directive.payload.token

        # run timer in it's own thread to prevent blocking future directives during count down
        if self.timer_thread is None:
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.setDaemon(True) 
            self.timer_thread.start()

    def on_alerts_deletealert(self, directive):
        """
        Handles Alerts.DeleteAlert directive sent from Echo Device
        """
        # # check if this is for the currently running timer. if not, just ignore
        # if self.timer_token_primary != directive.payload.token:
        #     logger.info("Received DeleteAlert directive but not for the currently active timer. Ignoring")
        #     return

        # # delete the timer, and stop the currently running timer thread
        # logger.info("Received DeleteAlert directive. Cancelling the timer")
        # self.timer_token_primary = None

        self.timers.pop(directive.payload.token)
        self.sort_timers()
    

    def sort_timers(self):
        self.sortedTimers = sorted(self.timers.items(), key = lambda kv:(kv[1], kv[0]))

    def _run_timer(self):
        """
        Runs a timer
        """
        time_remaining = 1
        while bool(self.timers):

            currentTime = time.time()

            # Get secondary timer info (if any)
            time_remaining_secondary = None
            if len(self.sortedTimers) > 1:
                timer_end_time = self.sortedTimers[1][1]
                time_remaining_secondary = max(0, timer_end_time - currentTime)
            
            timer_end_time = self.sortedTimers[0][1]
            time_remaining = max(0, timer_end_time - currentTime)
            self.display.display_time_remaining(time_remaining, time_remaining_secondary)

            #logger.info("Timer token %s.  %d seconds left.", 
            #    self.sortedTimers[0][0], time_remaining)

            # Format the timer digits for display
            #timer = time.strftime("%H:%M:%S", time.gmtime(time_remaining))
            #logger.info("Display timer value: %s", timer)

            # We grab the time again to caculate sleep
            subseconds = time.time() % 1
            if subseconds >= 0.5:
                sleepTime = 1.0 - subseconds
            else:
                sleepTime = 0.5 - subseconds
            #logger.info("sleepTime: %f", sleepTime)
            self.event.wait(sleepTime)
        
        self.timer_thread = None
        self.display.clear()

    def test(self):
        """
        Test timer thread
        """

        self.register_signal_handler()

        scheduledTime = '2020-02-11T02:00:00-07:00'
        t = dateutil.parser.parse(scheduledTime).timestamp()
        self.timers['2551392553'] = t
        self.sort_timers()
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.setDaemon(True) 
        self.timer_thread.start()
        logger.info("thread _run_timer started")
        self.timer_thread.join()
        logger.info("thread _run_timer ended")

    def register_signal_handler(self):

        self.original_handler_SIGINT = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.signal_handler)
 
        self.original_handler_SIGTERM = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, self.signal_handler) 

    def signal_handler(self, signum, frame):
            logger.info('Shutdown...')

            self.timer_token_primary = None
            self.event.set()

            # Do cleanup here


            # Call original handlers
            if signum==signal.SIGINT:
                self.original_handler_SIGINT(signum, frame)
            elif signum==signal.SIGTERM:
                self.original_handler_SIGTERM(signum, frame)

            sys.tracebacklimit = 0
            sys.exit(0)



if __name__ == '__main__':

    if os.geteuid() != 0:
        exit("You need to have root privileges to run this program.\nPlease try again, this time using 'sudo'. Exiting.")
    gadget = TimerGadget(None)
    logger.info("gadget about to call main")
    gadget.main()
        


