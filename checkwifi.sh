#!/bin/bash -x
#
# Add to to cron via:
#   crontab -e
#   */10 * * * * /home/pi/rpi-alexa-timer/checkwifi.sh
#

GATEWAY=`ip r | grep default | cut -d ' ' -f 3`
GATEWAY="172.20.0.140"
ping -q -c 1 -W 10 ${GATEWAY} > /dev/null
if [ $? != 0 ] 
then
  # Wait 10 minutes after failed ping to try again
  sleep 10
  ping -q -c 1 -W 10 ${GATEWAY} > /dev/null
  if [ $? != 0 ] 
  then
    echo "Reboot because we can't ping default gateway"
    # sudo /sbin/shutdown -r now
  fi
fi

