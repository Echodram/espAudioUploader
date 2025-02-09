from AudioEspClient import ClientEsp32
from audioRecord import AudioRecord

import urequests as re
import uos
import time
import ntptime

try:
    ntptime.settime()
except:
    pass


audioEspClient = ClientEsp32()
record = AudioRecord()

while True:

    deadline = time.ticks_add(time.ticks_ms(), ClientEsp32._period)
    date = time.localtime()
    name = f'{date[0]}__{date[1]}__{date[2]}_{date[3]}H{date[4]}.wav'
    
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        if time.ticks_diff(deadline, time.ticks_ms()) < 100 :
            record.recordAudio(name)
            time.sleep(2)
            audioEspClient.test()
            audioEspClient.send_file(name)
                   