#!/usr/bin/env python3

import configparser, syslog, sys, signal
from oled import OLED, Font, Graphics


configFile = "../config/terraControl.config"
logIdent = "terraControl"


def logEvent( logPriority, logMessage ):

    syslog.syslog( getattr( syslog, logPriority ), logMessage )
    

def readConfigFile():


    try:

        config.read_file(open(configFile))

    except:

        logEvent("LOG_ERR", "[ Error ] reading config file.")
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
  config["pins"]["heater"].off()
  config["pins"]["fan"].off()
  logEvent("LOG_INFO", "Turning light OFF")
  config["pins"]["light"].off()

  if bool(config["oled"]["enabled"]):
      
      updateDisplay("X")

  sys.exit(0)





## RUN ONCE
config = configparser.ConfigParser()
syslog.openlog(logIdent)
readConfigFile()

## SETUP OLED IF ENABLED
if bool(config["oled"]["enabled"]):

    initDisplay()

## SETUP SIGNAL HANDLING

if __name__ == '__main__':

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




# DEBUG
print(config['sensor1']['sensorAddr'])
print(bool(config["sensor1"]["enabled"]))







syslog.closelog()
