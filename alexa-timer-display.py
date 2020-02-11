#!/usr/bin/python3
#
# Alexa Timer Display
# Uses Alexa Gadget API
#

import logging
import sys
import threading
import time

import dateutil.parser
from agt import AlexaGadget

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


# Alexa Gadget code
class TimerGadget(AlexaGadget):
    """
    An Alexa Gadget that reacts to a single timer set on an Echo device.

    Threading is used to prevent blocking the main thread when the timer is
    counting down.
    """

    def __init__(self):
        super().__init__()
        self.timer_thread = None
        self.timer_token = None
        self.timer_end_time = None

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
            logger.info("Received SetAlert directive but scheduledTime has already passed. Ignoring")
            return

        # check if this is an update to an alrady running timer (e.g. users asks alexa to add 30s)
        # if it is, just adjust the end time
        if self.timer_token == directive.payload.token:
            logger.info("Received SetAlert directive to update to currently running timer. Adjusting")
            self.timer_end_time = t
            return

        # check if another timer is already running. if it is, just ignore this one
        if self.timer_thread is not None and self.timer_thread.isAlive():
            logger.info("Received SetAlert directive but another timer is already running. Ignoring")
            return

        # start a thread to rotate the servo
        logger.info("Received SetAlert directive. Starting a timer. " + str(int(t - time.time())) + " seconds left..")
        self.timer_end_time = t
        self.timer_token = directive.payload.token

        # run timer in it's own thread to prevent blocking future directives during count down
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.start()

    def on_alerts_deletealert(self, directive):
        """
        Handles Alerts.DeleteAlert directive sent from Echo Device
        """
        # check if this is for the currently running timer. if not, just ignore
        if self.timer_token != directive.payload.token:
            logger.info("Received DeleteAlert directive but not for the currently active timer. Ignoring")
            return

        # delete the timer, and stop the currently running timer thread
        logger.info("Received DeleteAlert directive. Cancelling the timer")
        self.timer_token = None


    def _run_timer(self):
        """
        Runs a timer
        """
        # check every 500ms
        start_time = time.time()
        time_remaining = self.timer_end_time - start_time
        while self.timer_token and time_remaining > 0:
            logger.info("Received SetAlert directive. Starting a timer.  %d seconds left..", time_remaining)
            time_total = self.timer_end_time - start_time
            time_remaining = max(0, self.timer_end_time - time.time())

            # Format the timer digits for display
            timer = time.strftime("%H:%M:%S", time.gmtime(time_remaining))

            # Display timer here
            logger.info("Display timer value: %s", timer)

            time.sleep(0.5)

 

if __name__ == '__main__':
    try:
        TimerGadget().main()
    finally:
        if KeyboardInterrupt:
            logger.debug('Cleaning up code here')

