#!/usr/bin/env python3

import RPi.GPIO as gpio
import configparser, syslog, sys, signal, time, smbus
from oled import OLED, Font, Graphics


configFile = "../config/terraControl.config"
logIdent = "terraControl"


def logEvent( logPriority, logMessage ):

    syslog.syslog( getattr( syslog, logPriority ), logMessage )
    

def readConfigFile(*args):


    try:

        config.read_file(open(configFile))

    except:

        logEvent("LOG_ERR", "[ Error ] reading config file.")
        gpio.cleanup()
        sys.exit(1)

    else:
    
        logEvent("LOG_INFO", "[ OK ] reading config file.")


def initDisplay():

    disp = OLED(1)
    disp.begin()
    disp.initialize()
    disp.set_memory_addressing_mode(0)
    disp.set_column_address(0, 127)
    disp.set_page_address(0, 7)
    disp.deactivate_scroll()


def terminate(signalNumber, frame):
  
    logEvent("LOG_INFO", "SIGTERM received. Terminating..")
    
    logEvent("LOG_INFO", "Turning heater OFF")
    gpio.output( config["pins"].getint("heater"), gpio.LOW)

    logEvent("LOG_INFO", "Turning light OFF")
    gpio.output( config["pins"].getint("light"), gpio.LOW)

    logEvent("LOG_INFO", "Turning fan OFF")
    gpio.output( config["pins"].getint("fan"), gpio.LOW)
 
    if config["oled"].getboolean("enabled"):
      
        updateDisplay("X")

    gpio.cleanup()
    sys.exit(0)


def updateDisplay(status):

    dispFont = Font(3)
    disp.clear()

    if status == "X":

        disp.set_contrast_control(contrastDay)
        dispFont.print_string(0, 0, "T: NONE")
        dispFont.print_string(0, 27, "H: NONE")

    else:

        dispFont.print_string(0, 0, "T: " + tempTrimmed)
        dispFont.print_string(0, 27, "H: " + humTrimmed)

    dispFont = Font(1)
    dispFont.print_string(73, 57, "Status: " + status)
    disp.update()


def heatingON():

    logEvent("LOG_INFO", "Turning heating ON")
    gpio.output( config["pins"].getint("heater"), gpio.HIGH)
    gpio.output( config["pins"].getint("fan"), gpio.HIGH)

    if config["oled"].getboolean("enabled"):

        updateDisplay("H")

def heatingOFF():

    logEvent("LOG_INFO", "Turning heating OFF")
    gpio.output( config["pins"].getint("heater"), gpio.LOW)
    gpio.output( config["pins"].getint("fan"), gpio.LOW)

    if config["oled"].getboolean("enabled"):

        updateDisplay("O")


def lightsON():

    logEvent("LOG_INFO", "Turning lights ON")
    gpio.output( config["pins"].getint("light"), gpio.HIGH)


def lightsOFF():

    logEvent("LOG_INFO", "Turning lights OFF")
    gpio.output( config["pins"].getint("light"), gpio.LOW)
                                                

def readFromSensor():

    try:

#        bus.write_i2c_block_data(config["sensor1"]["sensorAddr"], 0x2C, [0x06])
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
#        sleep(config["sensor1"].getfloat("sensorSleep"))
        sleep(0.5)

    except:

        logEvent("LOG_INFO", "Error (E1) communicating with sensor. Turning heater off.")
        gpio.output( config["pins"].getint("heater"), gpio.LOW)
        gpio.output( config["pins"].getint("fan"), gpio.LOW)

        if config["oled"].getboolean("enabled"):

            updateDisplay("E")

        syslog.closelog()
        gpio.cleanup()
        sys.exit(1)



## RUN ONCE

### INITIAL CONFIG FILE SETUP
config = configparser.ConfigParser()
readConfigFile()

### GPIO SETUP
gpio.setmode(gpio.BCM)
gpio.setup( config["pins"].getint("heater"), gpio.OUT)
gpio.setup( config["pins"].getint("light"), gpio.OUT)
gpio.setup( config["pins"].getint("fan"), gpio.OUT)

### SETUP LOG IDENTIFICATION STRING
syslog.openlog(logIdent)


### SETUP OLED IF ENABLED
if config["oled"].getboolean("enabled"):

    initDisplay()

### SETUP SIGNAL HANDLING

if __name__ == '__main__':

    signal.signal(signal.SIGHUP, readConfigFile)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGQUIT, signal.SIG_IGN)
    signal.signal(signal.SIGILL, signal.SIG_IGN)
    signal.signal(signal.SIGTRAP, signal.SIG_IGN)
    signal.signal(signal.SIGABRT, signal.SIG_IGN)
    signal.signal(signal.SIGBUS, signal.SIG_IGN)
    signal.signal(signal.SIGFPE, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    signal.signal(signal.SIGSEGV, signal.SIG_IGN)
    signal.signal(signal.SIGUSR2, signal.SIG_IGN)
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, terminate)


### SETUP SMBUS
bus = smbus.SMBus(1)



while True:

# DEBUG
    print(config['sensor1']['sensorAddr'])
    print(config["sensor2"].getboolean("enabled"))
    readFromSensor()

    time.sleep(10)




gpio.cleanup()
syslog.closelog()
