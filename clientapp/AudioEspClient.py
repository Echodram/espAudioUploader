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
    WIFI_SSID = 't'
    PASSWORD = ''
    HOST = '35.226.222.247'
    PORT = 40500
    
class ClientEsp32:
    
   """
    Overview
            -The ClientEsp32 class manages the connection and communication between an ESP32 client and a server for transmitting audio files.
            It handles network connections, data transmission, and audio parameter management.

        Key Features
            -Connection Management: Connects to a server using TCP sockets, with methods for establishing and closing connections.
            -Data Transmission: Sends audio file data and receives server responses, including error handling for connection issues.
            -Wi-Fi Connectivity: Attempts to connect to Wi-Fi using provided credentials.
            -Audio Parameter Handling: Retrieves and organizes audio file parameters for transmission to the server.
            -File Sending: Reads audio files and sends their data in chunks to the server, with progress monitoring.
        Methods
            - __init__(self, family, _type, timeout): Initializes the client with socket parameters and sets up initial states.
            - connect_to_server(): Establishes a connection to the specified server.
            - receive_data(buffer): Receives data from the server with error handling.
            - close_connection(): Closes the current socket connection.
            - reconnect(): Attempts to reconnect to the server after closing the connection.
            - send_data(data): Sends data to the server, handling errors and reconnection attempts.
            - connectToWifi(): Connects to Wi-Fi, retrying until successful.
            - test(): Tests the connection by sending a "TEST" message to the server.
            - serverResponse(): Sends a "SENDED" message and waits for a server acknowledgment.
            - getChunknum(nframes): Calculates the number of chunks needed for the given number of frames.
            - setAudioParams(audioStream, filename): Sets and returns audio parameters for transmission.
            - send_file(filename): Connects to the server and sends the specified audio file in chunks while monitoring for transmission issues.
    """
    
    def __init__(self, family=socket.AF_INET, _type=socket.SOCK_STREAM, timeout=10):
        self.clientsocket = None
        self.isConnected = False
        self.chunk_size = 4*1024
        self.dictParams = {}
        self.family = family
        self._type = _type
        self.date = None
           
    def connect_to_server(self):
        try:
            self.clientsocket = socket.socket(self.family, self._type)
            self.clientsocket.connect((Settings.HOST, Settings.PORT))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
        
    def receive_data(self, buffer=1024):
        try:
            return self.clientsocket.recv(buffer)
        except OSError as exc:
            print(f"An error occured while sendind data : {e}")
        except Exception as e:
            print(f"An error occured while sendinf data : {e}")
        except BrokenPipeError as e:
            print(f"The connexion was closed by the server :{e}")
            
            
    def close_connection(self):
        self.clientsocket.close()
        self.clientsocket = None
        
    def reconnect(self):
        self.close_connection()
        print("Attempting to reconnect to the server")
        self.connect_to_server()
        
    def send_data(self, data):
        try:
            self.clientsocket.send(data)
            return True
        except OSError as e:
            print(f"An error occured while sendind data : {e}")
            time.sleep(1)
            self.reconnect()
            return False
        except Exception as e:
            print(f"An error occured while sendind data : {e}")
            time.sleep(1)
            return False
        except BrokenPipeError as e:
            print(f"The connexion was closed by the server :{e}")
            time.sleep(1)
            return False
        
        
        
        
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
        self.close_connection()
    
    def getChunknum(self, nframes):
        return (nframes + self.chunk_size - 1)//self.chunk_size
    
    def setAudioParams(self, audioStream, filename):
        params = audioStream.getparams()
        (nchannels, samplewidth, framerate,nframes,comptype,compname) = params[:6]
        numck = self.getChunknum(nframes)
        self.date = time.localtime()
        self.dictParams = {
                             'nchannels'  : nchannels,
                             'samplewidth': samplewidth,
                             'framerate'  : framerate,
                             'nframes'    : nframes,
                             'comptype'   : comptype,
                             'compname'   : compname,
                             'numchunk'   : numck,
                             'date'     : f'{self.date[0]}__{self.date[1]}__{self.date[2]}',
                             'filename' : filename
                            }
        return self.dictParams
    
    def send_file(self, filename):
        print('Attempting to connect to the server!!!')
        
        self.connect_to_server()        
        audio = wave.open(f'/sd/{filename}', 'rb')
        audioParamsToSend = self.setAudioParams(audio, filename)
        self.send_data(str(audioParamsToSend).encode())
        
        print("file's header sended")
        while True:
          chunk = audio.readframes(self.chunk_size)
          if not chunk:
              if status == True:
                  print('file successfully sended')
                  self.close_connection()
                  self.serverResponse()
                  break
              else:
                  print('A problem occured while sendind the file')
                  self.close_connection()
                  break
              break
          elif (self.date[4]-time.localtime()[4]==1)  and (time.localtime()[5]%55)==0:
              print('___Next Anchor reached___')
              print('___The transmission will be aborted___')
              self.close_connection()
              break
            
          status = self.send_data(chunk)
        audio.close()
        
        

                 







