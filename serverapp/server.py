import socketserver
import wave
import socket
import os
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler("app.log"),  
        logging.StreamHandler() 
    ]
)

logger = logging.getLogger(__name__)

BASE_DIRECTORY = 'shared'
    
class NetworkAddress:
    HOST = "0.0.0.0"
    PORT = 40500
           
class AudioServerTCPHandler(socketserver.BaseRequestHandler):
    
    def __ini__(self):
        self.dataInfos = {}
        self.foldername = ''
    
    def create_daily_folder(self):
        today = datetime.today()
        self.foldername = today.strftime("%Y-%m-%d")
        if not os.path.exists(self.foldername):
            os.makedirs(self.foldername)
            logger.info('new folder created')
                 
    def getFileParams(self, audioParamsBytes):
        self.dataInfos = eval(audioParamsBytes)
        nchannels   = self.dataInfos['nchannels']
        samplewidth = self.dataInfos['samplewidth']
        framerate   = self.dataInfos['framerate']
        nframes     = self.dataInfos['nframes']
        comptype    = self.dataInfos['comptype']
        compname    = self.dataInfos['compname']
        filename    =    self.dataInfos['filename']
        return nchannels, samplewidth, framerate, nframes, comptype, compname
    
    def getEspHashValue(self):
        return self.dataInfos['hashValue']
    
    def getChunkNum(self):
        return self.dataInfos['numchunk']
    
    def handle(self) -> None:
        '''
           For Handling esp32 requests
        '''
        self.data = self.request.recv(1024)
        logger.info(self.data.decode())
        nchannels, samplewidth, framerate, nframes, comptype,compname = None, None, None, None, None, None
        try:
            if type(eval(self.data.decode())) == dict :
                if 'hash' not in eval(self.data.decode()).keys():
                    nchannels, samplewidth, framerate, nframes, comptype,compname = self.getFileParams(self.data.decode())
            else:
                pass
        except:
            logger.info('incoming file from esp32')
            
        try:
            datetime_at_esp32 = self.dataInfos['date']
            path = os.path.join(BASE_DIRECTORY, datetime_at_esp32)  #the will to a filename should eg : /shared/2024_2_4/2024_2_4.wav
            if not os.path.exists(path):
                os.makedirs(path)
                logger.info('new folder created')
        except:
            logger.info('files header not already received')
      
        if self.data.decode() == 'TEST':
           self.request.sendall(b'OK')
        
        elif self.data.decode() == 'SENDED':
           logger.info(f'CLIENT RESPONSE : {self.data.decode()}')
           self.request.sendall(b'RECEIVED')
           
        elif self.data.decode() != 'TEST' and self.data.decode() != 'SENDED':
            file_name = self.dataInfos['filename']
            with wave.open(f'{path}/{file_name}', 'wb') as audio:
                if nchannels is not None and samplewidth is not None and framerate is not None:
                    logger.info(nchannels)
                    audio.setparams((nchannels, samplewidth, framerate,nframes,comptype,compname))
                    logger.info("wave file dowloading...")
                    chunk_size = 1024
                    while True:
                        try:
                            chunk = self.request.recv(4*chunk_size)
                        except socket.error as msg:
                            logger.error('NO CHUNK RECEIVE')  
                        if not chunk:
                            logger.info("Download complete")
                            break
                        else:
                            try:
                                audio.writeframes(chunk)
                            except:
                                pass           
            self.request.sendall(b'DATA RECEIVED')
                              
if __name__ == "__main__" :
    with socketserver.TCPServer((NetworkAddress.HOST, NetworkAddress.PORT), AudioServerTCPHandler) as server:
        logger.info(f'Server started at {NetworkAddress.HOST}:{NetworkAddress.PORT}')
        server.serve_forever()

