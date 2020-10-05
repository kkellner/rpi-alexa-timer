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

from timers_from_bluetooth import TimersFromBluetooth
from timers_from_mqtt import TimersFromMqtt

#from display_max7219 import DisplayMax7219 as Display
from display_adafruit_hat import DisplayAdafruitHat as Display

logger = logging.getLogger(__name__)

class ManageTimers:

 
    def __init__(self, app):
        self.app = app
        
        self.timers_from_bluetooth = None
        self.timers_from_mqtt = None

        self.timer_thread = None

        self.event = threading.Event()

        logger.info("init display")
        self.display = Display()

        #netifaces.ifaddresses('wlan0')
        ip = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']

        #self.display.show_text("Startup")
        #self.display.show_text(ip, 2)
        self.display.scroll_text("Startup: " + ip, 2, 2)

        
    def startup(self):
        self.timers_from_mqtt = TimersFromMqtt(self)
        self.timers_from_bluetooth = TimersFromBluetooth(self)

        #self.display.show_text("Initialize", 2)
        self.display.clear()

        logger.info("About to call gadget main")
        # The following is a blocking call
        self.timers_from_bluetooth.main()


    def timer_changed(self):
        """
        One or more timers have changed
        """

        # If we clear all times from MQTT, then clear them from bluetooth
        # so that we don't display ":00" longer then needed as bluetooth 
        # updates come in about 1 second slower then MQTT
        if len(self.timers_from_mqtt.sortedTimers) == 0:
            self.timers_from_bluetooth.clear_all_timers()

        self._create_timer_thread()


    def _create_timer_thread(self):
        """
        Run timer in it's own thread to prevent blocking future directives during count down
        """
        if self.timer_thread is None:
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.setDaemon(True) 
            self.timer_thread.start()

 
    def _run_timer(self):
        """
        Runs a timer
        """

        time_remaining = 1
        while True:

            timers = self.filter_timers(self.timers_from_mqtt.sortedTimers)
            if not bool(timers):
                timers = self.filter_timers(self.timers_from_bluetooth.sortedTimers)

            # Break out of loop if there are no timers to display
            if not bool(timers):
                break

            currentTime = time.time()

            # Get secondary timer info (if any)
            time_remaining_secondary = None
            if len(timers) > 1:
                timer_end_time = timers[1][1]
                time_remaining_secondary = max(0, timer_end_time - currentTime)
            
            timer_end_time = timers[0][1]
            time_remaining = max(0, timer_end_time - currentTime)
            self.display.display_time_remaining(time_remaining, time_remaining_secondary)

            #logger.info("Timer token %s.  %d seconds left.", 
            #    timers[0][0], time_remaining)

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

    def filter_timers(self, timers):
        """
        Remove any times that have expired more then 15 seconds in the past
        """
        if bool(timers):
            currentTime = time.time()
            currentTimePlus = currentTime - 15
            timers[:] = [x for x in timers if x[1] > currentTimePlus]
        return timers


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

            self.event.set()

            # Call original handlers
            if signum==signal.SIGINT:
                self.original_handler_SIGINT(signum, frame)
            elif signum==signal.SIGTERM:
                self.original_handler_SIGTERM(signum, frame)

            sys.tracebacklimit = 0
            sys.exit(0)