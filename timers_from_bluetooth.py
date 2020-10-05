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

logger = logging.getLogger(__name__)

# Alexa Gadget code.  
# Parent class: https://github.com/alexa/Alexa-Gadgets-Raspberry-Pi-Samples/blob/master/src/agt/alexa_gadget.py
class TimersFromBluetooth(AlexaGadget):
    """
    An Alexa Gadget that reacts to a single timer set on an Echo device.

    Threading is used to prevent blocking the main thread when the timer is
    counting down.
    """

    def __init__(self, manage_timers):
        self.manage_timers = manage_timers

        # Dictionary of timers where key is token and value is end time
        self.timers = {}
        self.sortedTimers = None

        super().__init__("alexa_timer_display.ini")        

    def on_connected(self, device_addr):
        logger.info("Bluetooth on_connected called")
        #self.display.show_text("Connected")
        #self.display.clear()

    def on_disconnected(self, device_addr):
        logger.info("Bluetooth on_disconnect called")
        self.timers = {}
        time.sleep(1)
        #self.display.show_text("Disconnected")

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

        # Check if we had an MQTT AllTimersUptime recently, if so, ignore the bluetooth update
        # if (self.lastAllTimersUpdate + ignoreBluetoothIfMqttUpdateInLastSeconds) > time.time():
        #     return

        # check if this is an update to an alrady running timer (e.g. users asks alexa to add 30s)
        # if it is, just adjust the end time

        self.timers[directive.payload.token] = t
        self.sort_timers()
        logger.info("Calling timer_changed from bluetooth")
        self.manage_timers.timer_changed()

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
        self.timers.pop(directive.payload.token, None)
        self.sort_timers()
        self.manage_timers.timer_changed()
    

    def sort_timers(self):
        self.sortedTimers = sorted(self.timers.items(), key = lambda kv:(kv[1], kv[0]))

    def clear_all_timers(self):
        self.timers = {}

if __name__ == '__main__':

    if os.geteuid() != 0:
        exit("You need to have root privileges to run this program.\nPlease try again, this time using 'sudo'. Exiting.")
    gadget = TimersFromBluetooth(None)
    logger.info("gadget about to call main")
    gadget.main()
        


