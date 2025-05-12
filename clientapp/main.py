"""
Overview
    -This script manages the audio recording and transmission process using an ESP32 device. It connects to Wi-Fi, records audio periodically, and sends the recorded files to a server.

Key Components
    Imports:
        -ClientEsp32: Handles client-server communication.
        -AudioRecord: Manages audio recording functionality.
        -Standard libraries for file management and time handling.
    Wi-Fi Setup:
        -Connects to a Wi-Fi network.
        -Synchronizes the device time using an NTP server.
    Main Loop
        -Recording and Sending:
        -Checks the current time and records audio at specified intervals (defined by anchor_period_minutes).
        -Constructs a filename based on the current date and time.
        -Calls the recordAudio method to capture audio and save it to a WAV file.
        -Sends the recorded file to the server using send_file.
        -Deletes the WAV file from the SD card after successful transmission.
    Wi-Fi Connection Check:
        Reconnects to Wi-Fi if the connection is lost.
    
"""
from AudioEspClient import ClientEsp32
from audioRecord import AudioRecord
import os
import urequests as re
import uos
import time
import ntptime
import network
wlan = network.WLAN(network.STA_IF)

try:
    ntptime.settime()
except:
    pass

client = ClientEsp32()
client.connectToWifi()
record = AudioRecord()
anchor_period_minutes = 5

while True:
    date = time.localtime()
    if date[4] % anchor_period_minutes == 0:
        name = f'{date[0]}__{date[1]}__{date[2]}_{date[3]}H{date[4]}.wav'
        record.recordAudio(name)
        time.sleep(1)
        #client.test()
        client.send_file(name)
        os.remove(f'/sd/{name}')
    else :
        pass
    
    if wlan.isconnected() :
        pass
    else:
        client.connectToWifi()
            
                    
