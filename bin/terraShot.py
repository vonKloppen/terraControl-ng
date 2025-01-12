#!/usr/bin/env python3

import os, syslog
from gpiozero import LED
from time import localtime, strftime, sleep

### VARIABLES ###

interval_day = 180
interval_night = 180
dayStart = "08:00"
nightStart  = "18:00"

picOutputTemp = "/mnt/terraControlNG/view.temp"
picOutputTemp1 = "/mnt/terraControlNG/view.temp1"
picOutput = "/mnt/terraControlNG/view.jpg"

###

while True:

  currentTime = strftime("%H:%M", localtime())

  syslog.syslog(syslog.LOG_INFO, "Taking picture")
  os.system('rpicam-still --awb tungsten --immediate 1 --brightness 0.15 -o %s' %(picOutputTemp))
  os.system('convert %s -crop 2140x2464+680+0 %s' %(picOutputTemp, picOutputTemp1))
  os.system('convert %s -rotate 90 %s' %(picOutputTemp1, picOutput))

  if (currentTime >= dayStart) and (currentTime < nightStart):

    sleep(interval_day)

  else:

    sleep(interval_night)

