# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import socket
import network
s = socket.socket()
s.close()

wlan = network.WLAN(network.STA_IF)
wlan.active(False)