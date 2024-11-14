from AudioEspClient import ClientEsp32
from audioRecord import AudioRecord

import urequests as re
import uos
import time


audioEspClient = ClientEsp32()
record = AudioRecord()
i = 0
while True:
    deadline = time.ticks_add(time.ticks_ms(), ClientEsp32._period)
    name = f'file_{i}.wav'
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        if time.ticks_diff(deadline, time.ticks_ms()) < 100 :
            audioEspClient.test()
            record.recordAudio(name)
            time.sleep(2)
            audioEspClient.send_file(record.filename)
            print(uos.listdir("/sd"))
            i = i + 1
