# What is it?

It's a simple "daemon" for monitoring temperature and humidity in terrarium, using different sensors and Raspberry PI Zero.
It creates log as csv file and logs to syslog. Also it can control light and camera.

Currently it supports only sht-31 sensors.


***Be aware that this is highly customized sollution and a work in progress and you should probably not use this code for controling temperature in terrarium with live animals!***

## **Prerequisites**

*raspi-config - enable i2c*

*apt install python3-smbus2 python3-cffi*

*pip3 install mod-oled-128x64 --break-system-packages*

*reboot*

## **TO-DO**

### Functionality

 - [x] Move variables to config file - config file parser needed
 - [ ] Add simple www server (python) for displaying chart directly on Raspberry
 - [ ] ~~Add configuration change from www ( [ ] Add default absolute max temperature and time of heating, [ ] Password protection )~~
 - [ ] Add option to choose time and date for chart
 - [ ] Add API with status in JSON
 - [x] Convert epoch to human-readeable dates/times
 - [x] Add watchdog service
 - [x] Add catch photo with lighting
 - [x] Logging to syslog
 - [x] Signal handling (systemd)
 - [x] OLED display (separate daemon using sockets)

### Modules

**UPS:**

*As separate daemon: https://github.com/vonKloppen/raspiUPS

- [x] Monitoring service
- [x] Clean shutdown of PI
- [x] Logging to syslog

### Hardware
- add diagrams and instructions for building fully working project with DIY heater and off-shelf one.


## **BUGS**
Occasionally it crashes OS beyond recovery - probably due to bug in i2c implementation in Raspbian.
Possible fixes:
- use i2c multiplexer
- use filelock mechanism
- reduce i2c speed (probably does nothing).
  




