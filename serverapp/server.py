import socketserver
import wave
import socket
import hashlib
import requests 
import os
from datetime import datetime


 
class NetworkAddress:
    HOST = ""
    PORT = 8000
       
class AudioServerTCPHandler(socketserver.BaseRequestHandler):
    def __ini__(self):
        self.dataInfos = {}
  
    
    def getFileParams(self, audioParamsBytes):
        self.dataInfos = eval(audioParamsBytes)
        nchannels   = self.dataInfos['nchannels']
        samplewidth = self.dataInfos['samplewidth']
        framerate   = self.dataInfos['framerate']
        nframes     = self.dataInfos['nframes']
        comptype    = self.dataInfos['comptype']
        compname    = self.dataInfos['compname']
        return nchannels, samplewidth, framerate, nframes, comptype, compname
    
    def getEspHashValue(self):
        return self.dataInfos['hashValue']
    
    def getChunkNum(self):
        return self.dataInfos['numchunk']
    
    def handle(self) -> None:
        '''
           For Handling esp32 requests
        '''
        chunk_recv = 0
        self.data = self.request.recv(1024)
        print(self.data.decode())
        nchannels, samplewidth, framerate, nframes, comptype,compname = None, None, None, None, None, None
        hashEspValue = None
        try:
            if type(eval(self.data.decode())) == dict :
                if 'hash' not in eval(self.data.decode()).keys():
                    nchannels, samplewidth, framerate, nframes, comptype,compname = self.getFileParams(self.data.decode())
            else:
                hashEspValue = eval(self.data.decode())['hash']
        except:
            print('not a dict')
      
        if self.data.decode() == 'TEST':
           self.request.sendall(b'OK')
        
        elif self.data.decode() == 'SENDED':
           print('CLIENT RESPONSE :', self.data.decode())
           self.request.sendall(b'RECEIVED')
           
        elif self.data.decode() != 'TEST' and self.data.decode() != 'SENDED':
            file_name = f'{datetime.now().strftime("%Y_%d_%B_%Hh%M.WAV")}'
            with wave.open(file_name, 'wb') as audio:
                if nchannels is not None and samplewidth is not None and framerate is not None:
                    print(nchannels)
                    audio.setparams((nchannels, samplewidth, framerate,nframes,comptype,compname))
                    print("wave file dowloading...")
                    chunk_size = 1024
                    while True:
                        try:
                            chunk = self.request.recv(4*chunk_size)
                        except socket.error as msg:
                            print(msg)  
                        if not chunk:
                            print("Download complete")
                            break
                        else:
                            try:
                                audio.writeframes(chunk)
                            except:
                                pass           
            self.request.sendall(b'DATA RECEIVED')
                              
if __name__ == "__main__" :
    with socketserver.TCPServer((NetworkAddress.HOST, NetworkAddress.PORT), AudioServerTCPHandler) as server:
        print('Server started')
        server.serve_forever()

