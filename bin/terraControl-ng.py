#!/usr/bin/env python3

import smbus2, os, sys, signal, socket, configparser, syslog
from time import time, localtime, strftime, sleep
from gpiozero import LED


configFile = "/etc/terraControl-ng/terraControl-ng.config"

bus = smbus2.SMBus(1)
currentEpoch = 0
previousEpoch = int(time())
globalsLogIdent = "terraControl-ng"
terra1Status = "S"
terra2Status = "S"
currentDisplay = 0
valuesTerra1 = [0, 0]
valuesTerra2 = [0, 0]


def terminate(signalNumber, frame):

    updateDisplay("X","1","0","0")
    logMessage("LOG_INFO", "SIGTERM received. Terminating..")
    logMessage("LOG_INFO", "Turning heaters OFF")
    terra1PinHeater.off()
    terra2PinHeater.off()
    logMessage("LOG_INFO", "Turning lights OFF")
    terra1PinLight.off()
    terra2PinLight.off()
    syslog.closelog()
    sys.exit(0)

def reloadConfig(signalNumber, frame):

    global terra1Enabled, terra1Addr, terra1PinHeater, terra1PinLight
    global terra1HeatingTime, terra1HeatingTimeout, terra1OverheatTimeout
    global terra1TempDay, terra1TempNight, terra1TempMax
    global terra1LogFileTemp
    global terra1LogFileHum

    global terra2Enabled, terra2Addr, terra2PinHeater, terra2PinLight
    global terra2HeatingTime, terra2HeatingTimeout, terra2OverheatTimeout
    global terra2TempDay, terra2TempNight, terra2TempMax
    global terra2LogFileTemp
    global terra2LogFileHum

    global globalsStartDay, globalsStartNight
    global globalsLogIdent, globalsLogsUpdateInterval

    global displayEnabled, displayUpdateInterval, displaySocketType, displaySocketFile, displayBindIP, displayBindPort 


    if not os.path.exists(configFile):

        logMessage("LOG_ERR", "Config file " + configFile + " not found. Quitting..")
        
    else:

        config = configparser.ConfigParser()
        config.read(configFile)

        terra1Enabled = config["terra1"].getboolean("enabled")
        terra1Addr = config["terra1"].getint("addr")
        terra1PinHeater = LED(config["terra1"].getint("pinHeater"))
        terra1PinLight = LED(config["terra1"].getint("pinLight"))
        terra1HeatingTime = config["terra1"].getint("heatingTime")
        terra1HeatingTimeout = config["terra1"].getint("heatingTimeout")
        terra1OverheatTimeout = config["terra1"].getint("overheatTimeout")
        terra1TempDay = config["terra1"].getint("tempDay")
        terra1TempNight = config["terra1"].getint("tempNight")
        terra1LogFileTemp = config["terra1"]["logFileTemp"]
        terra1LogFileHum = config["terra1"]["logFileHum"]

        terra2Enabled = config["terra2"].getboolean("enabled")
        terra2Addr = config["terra2"].getint("addr")
        terra2PinHeater = LED(config["terra2"].getint("pinHeater"))
        terra2PinLight = LED(config["terra2"].getint("pinLight"))
        terra2HeatingTime = config["terra2"].getint("heatingTime")
        terra2HeatingTimeout = config["terra2"].getint("heatingTimeout")
        terra2OverheatTimeout = config["terra2"].getint("overheatTimeout")
        terra2TempDay = config["terra2"].getint("tempDay")
        terra2TempNight = config["terra2"].getint("tempNight")
        terra2LogFileTemp = config["terra2"]["logFileTemp"]
        terra2LogFileHum = config["terra2"]["logFileHum"]

        globalsStartDay = config["globals"]["startDay"]
        globalsStartNight = config["globals"]["startNight"]

        globalsLogIdent = config["globals"]["logIdent"]
        globalsLogsUpdateInterval = config["globals"].getint("logsUpdateInterval")

        displayEnabled = config["display"].getboolean("displayEnabled")
        displayUpdateInterval = config["display"].getint("displayUpdateInterval")
        displaySocketType = config["display"]["socketType"]
        displaySocketFile = config["display"]["socketFile"]
        displayBindIP = config["display"]["bindIP"]
        displayBindPort = config["display"].getint("bindPort")

        logMessage("LOG_INFO", "Config file loaded successfully")

def logMessage(logLevel, message):

    syslog.syslog(getattr(syslog, logLevel), message)

def logValues(fileName, date, time, value):

    try:

        f = open(fileName, "a")

    except:

        logMessage("LOG_ERR", "Failed to open log file " + fileName)

    else:

        f.writelines(date + " " + time + "," + str(value) + "\n")
        f.close()

def trimLogFile(fileName):

    try:

        f = open(fileName, "r")

    except:

        logMessage("LOG_ERR", "Failed to open log file " + fileName)

    else:

        content = f.readlines()

        try:

            f = open(fileName, "w")

        except:

            logMessage("LOG_ERR", "Failed to open log file " + fileName)

        else:

            for x in range(-144, 0):

                f.writelines(content[x])

            f.close()




def updateDisplay(status, ident, temp, hum):

    if displayEnabled:

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
    
            client.connect(displaySocketFile)

        except:
            
            logMessage("LOG_ERR", "Can't bind to display socket.")
            client.close()

        else:
            
            message = str(status + "," + ident + "," + temp + "," + hum)
            client.send(message.encode("utf-8")[:1024])
            client.close()

def readValues(sensorAddr, pinLight, pinHeater):

    try:
        
        bus.write_i2c_block_data(sensorAddr, 0x2c, [0x06])

    except:
        
        logMessage("LOG_ERR", "Error (E1) communicating with sensor " + str(sensorAddr) + " . Quiting..")
        logMessage("LOG_INFO", "Turning heater OFF")
        pinHeater.off()
        logMessage("LOG_INFO", "Turning light OFF")
        pinLight.off()
        syslog.closelog()
        sys.exit(1)

    try:

      data = bus.read_i2c_block_data(sensorAddr, 0x00, 6)

    except:

      logMessage("LOG_ERR", "Error (E2) communicating with sensor " + str(sensorAddr) + " . Quiting..")
      logMessage("LOG_INFO", "Turning heater OFF")
      pinHeater.off()
      logMessage("LOG_INFO", "Turning light OFF")
      pinLight.off()
      syslog.closelog()
      sys.exit(1)

    else:

# Disabled due to spam
#      logMessage("LOG_INFO", "Reading temperature..")
      temperature = data[0] * 256 + data[1]
      tempConv = -45 + (175 * temperature / 65535.0)
      humConv = 100 * (data[3] * 256 + data[4]) / 65535.0
      tempTrimmed = f"{tempConv:.1f}"
      humTrimmed = f"{humConv:.1f}"
      
      return(tempTrimmed, humTrimmed)

def setHeater(isEnabled, pinHeater, terraNumber):

    if isEnabled == 1:

        logMessage("LOG_INFO", "Turning terra " + str(terraNumber) + " heater ON")
        pinHeater.on()

    elif isEnabled == 0:

        logMessage("LOG_INFO", "Turning terra " + str(terraNumber) + " heater OFF")
        pinHeater.off()

def setLight(isEnabled, pinLight1, pinLight2):

    if isEnabled == 1:

        logMessage("LOG_INFO", "Turning light ON")
        pinLight1.on()
        pinLight2.on()

    elif isEnabled == 0:

        logMessage("LOG_INFO", "Turning light OFF")
        pinLight1.off()
        pinLight2.off()


if __name__ == '__main__':

# Reloading causes crash for some reason
#    signal.signal(signal.SIGHUP, reloadConfig)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGQUIT, terminate)
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


reloadConfig(signal.SIGHUP, "X")
syslog.openlog(globalsLogIdent)


while True:

    currentEpoch = int(time())
    epochDiff = currentEpoch - previousEpoch

    currentTime = strftime("%H:%M", localtime())
    currentDate = strftime("%Y-%m-%d", localtime())

    if epochDiff < globalsLogsUpdateInterval:
      
        if currentTime >= globalsStartDay and currentTime < globalsStartNight:

            terra1TempSet = terra1TempDay
            terra2TempSet = terra2TempDay

            if not (terra1PinLight.is_active or terra2PinLight.is_active):

                setLight(1, terra1PinLight, terra2PinLight)

        else:

            terra1TempSet = terra1TempNight
            terra2TempSet = terra2TempNight

            if terra1PinLight.is_active or terra2PinLight.is_active:

                setLight(0, terra1PinLight, terra2PinLight)

        if terra1Enabled:

            terra1Status = "R"
            valuesTerra1 = readValues(terra1Addr, terra1PinHeater, terra1PinLight)

            if terra1TempSet > float(valuesTerra1[0]):

                terra1Status = "H"

                if not terra1PinHeater.is_active:

                    setHeater(1, terra1PinHeater, 1)

            elif terra1TempSet <= float(valuesTerra1[0]):

                terra1Status = "S"

                if terra1PinHeater.is_active:

                    setHeater(0, terra1PinHeater, 1)


        if terra2Enabled:
            
            terra2Status = "R"
            valuesTerra2 = readValues(terra2Addr, terra2PinHeater, terra2PinLight)

            if terra2TempSet - float(valuesTerra2[0]) > 0.2:

                terra2Status = "H"

                if not terra2PinHeater.is_active:

                    setHeater(1, terra2PinHeater, 2)

            elif terra2TempSet <= float(valuesTerra2[0]):

                terra2Status = "S"
                
                if terra2PinHeater.is_active:

                    setHeater(0, terra2PinHeater, 2)

        sleep(1)

        if (epochDiff % displayUpdateInterval == 0):

            if terra1Enabled and currentDisplay != 1:

                updateDisplay(terra1Status, "1", valuesTerra1[0], valuesTerra1[1] )

                if terra2Enabled:

                    currentDisplay = 1

            elif terra2Enabled and currentDisplay != 2:

                updateDisplay(terra2Status, "2", valuesTerra2[0], valuesTerra2[1] )

                if terra2Enabled:

                    currentDisplay = 2


    else:


        if terra1Enabled:

            logValues(terra1LogFileTemp, currentDate, currentTime, valuesTerra1[0])
            trimLogFile(terra1LogFileTemp)
            logValues(terra1LogFileHum, currentDate, currentTime, valuesTerra1[1])
            trimLogFile(terra1LogFileHum)

        if terra2Enabled:

            logValues(terra2LogFileTemp, currentDate, currentTime, valuesTerra2[0])
            trimLogFile(terra2LogFileTemp)
            logValues(terra2LogFileHum, currentDate, currentTime, valuesTerra2[1])
            trimLogFile(terra2LogFileHum)

        previousEpoch = currentEpoch

# This point is never reached, but for safety..

updateDisplay("X","1","0","0")
logMessage("LOG_INFO", "SIGTERM received. Terminating..")
logMessage("LOG_INFO", "Turning heaters OFF")
terra1PinHeater.off()
terra2PinHeater.off()
logMessage("LOG_INFO", "Turning lights OFF")
terra1PinLight.off()
terra2PinLight.off()
syslog.closelog()
sys.exit(0)
syslog.closelog()
