# rpi-alexa-timer
Raspberry Pi app to display Alexa timers via the Alexa Gadget API



# Install needed software / libaries


## General software

```
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install git -y
sudo apt-get install -y python3-pip
sudo pip3 install dbus-python
```

## Alexa Gadget API libs

Follow instructions on https://github.com/alexa/Alexa-Gadgets-Raspberry-Pi-Samples for Registering a gadget.  You will need to create a Amazon Developer account (instructions in above link) under the same account which has your echo devices registered. After you register a gadget and have a `Amazon ID` and `Alexa Gadget Secret` you can install and setup the libraries:

```
git clone https://github.com/alexa/Alexa-Gadgets-Raspberry-Pi-Samples.git
cd /home/pi/Alexa-Gadgets-Raspberry-Pi-Samples/
sudo python3 launch.py --setup
```

## LED Matrix libs

Since we are using the Adafruit bonnet for Raspberry PI zero W, follow instructions starting at step 6 of this guide https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/driving-matrices

```
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh >rgb-matrix.sh
sudo bash rgb-matrix.sh
```


## Install THIS app

Clone this repo and run a setup script.
```
git clone https://github.com/kkellner/rpi-alexa-timer.git
cd rpi-alexa-timer/config
./config.sh --hostname new-hostname --password pi-user-password
```

# Manually run

TODO: Document config files yml/ini.

```
sudo ./alexa-timer-display.py
```