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

logger = logging.getLogger(__name__)


class TimersFromMqtt:

 
    def __init__(self, manage_timers):
        self.manage_timers = manage_timers
        
        # Dictionary of timers where key is timer id and value is end time
        self.timers = {}
        self.sortedTimers = None
        

    def update_all_timers(self, updatedTimersArray):
        """
        Update the timers with an array of Timers.  Array example:
            {
                "id": "AB72C64C86AW2-B0F007155344044W-abed9ed1-8043-3c90-b93b-e8e96cfddbbf",
                "deviceName": "tv_room",
                "expireTime": "2020-10-03T12:46:12-0600"
            }, ...
        """
        #self.lastAllTimersUpdate =  time.time()
        timersMap = {}
        for timer in updatedTimersArray: 
            timerId = timer['id']
            expireTime = dateutil.parser.parse(timer['expireTime'])   
            timersMap[timerId] = expireTime.timestamp()
            logger.info("timer id: %s time: %s", timerId, expireTime)

        self.timers = timersMap
        self.sort_timers()
        logger.info("Calling timer_changed from mqtt")
        self.manage_timers.timer_changed()


    def sort_timers(self):
        self.sortedTimers = sorted(self.timers.items(), key = lambda kv:(kv[1], kv[0]))

