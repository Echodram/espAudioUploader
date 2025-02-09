from machine import Pin, ADC , Timer
import time
import socket
import uos
import wave 
import hashlib
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

class Settings:
    WIFI_SSID = "t"
    PASSWORD = "123456789"
    HOST = '34.121.82.35'
    PORT = 40500
    
class ClientEsp32:
    
    _ms = 1000
    _minute_in_seconds = 30
    _number_of_minutes = 1
    _period = _ms*_minute_in_seconds*_number_of_minutes
    
    def __init__(self, family=socket.AF_INET, _type=socket.SOCK_STREAM, timeout=10):
    
        #networks variables
        self.host = None
        self.port = None
        self.ssid = None
        self.root = '/sd/'
        self._type = _type
        self.family = family
        self.password = None
        self.isconnected = False
        self.clientsocket = None
        
        self.connectToWifi()
           
    def connect_to_server(self):
        self.clientsocket = socket.socket(self.family, self._type)
        self.clientsocket.connect((Settings.HOST, Settings.PORT))
        
    def receive_data(self, buffer=1024):
        return self.clientsocket.recv(buffer)
    
    def close_connection(self):
        self.clientsocket.close()
        self.clientsocket = None
        
    def send_data(self, data):
        self.clientsocket.send(data)
        
        
    def connectToWifi(self):
        while True:
            time.sleep(5)
            print("____ATTEMPTING TO CONNECT TO WIFI_____")
            try :
                wlan.connect(Settings.WIFI_SSID, Settings.PASSWORD)
                if wlan.isconnected():
                    print('_____WIFI CONNECTED_____')
                    break
            except :
                pass
    
    
    def test(self):
        self.connect_to_server()
        self.send_data(b'TEST')
        data = self.receive_data(buffer = 20).decode()
        if data == 'OK':
            print(data)
        self.close_connection()
        
    def serverResponse(self):
        self.connect_to_server()
        self.send_data(b'SENDED')
        data = self.receive_data(buffer = 20).decode()
        if data == 'RECEIVED':
            print('SERVER RESPONSE : ',data)
        self.isconnected = False
        self.close_connection()
    
    def getChunknum(self, nframes, chunk_size):
        return (nframes + chunk_size - 1)//chunk_size
    
    def send_file(self, filename):
        while not self.isconnected :
            print('Attempting to connect to the server ...')
            try :
                #esp.connect((host, port))
                self.connect_to_server()
                self.isconnected = True 
            except:
                time.sleep(5)
                continue
            
        print('Connected to the server ...')
        
        audio = wave.open(f'/sd/{filename}', 'rb')
            #Envoyer les informations du fichier
        print('File correctly opened')
        chunk_size = 4*1024
        chunk_index = 0
        params = audio.getparams()
        (nchannels, samplewidth, framerate,nframes,comptype,compname) = params[:6]
        numck = self.getChunknum(nframes, chunk_size)
        date = time.localtime()
        audioParamsToSend = {'nchannels' : nchannels,
                            'samplewidth': samplewidth,
                            'framerate'  : framerate,
                            'nframes'    : nframes,
                            'comptype'   : comptype,
                            'compname'   : compname,
                            'numchunk'   : numck,
                             'filename' : filename,
                             'date'     : f'{date[0]}__{date[1]}__{date[2]}'
                             }
        
        self.send_data(str(audioParamsToSend).encode())
        print("file's header sended")
        while True:
          chunk = audio.readframes(4*chunk_size)
          if not chunk:
              if chunk_index >= numck:
                  print('file successfully sended')
              break
          self.send_data(chunk)
          chunk_index += 4  
        self.close_connection()
        self.isconnected = False
        self.serverResponse()
    

                 





