"""
Overview
    This Python module implements an audio server that receives audio streams from clients. It is designed to facilitate real-time audio processing and playback in various applications, such as music streaming, voice chat, or audio analysis.

Features
    -Socket Communication: Utilizes TCP sockets for reliable audio data transmission.
    -Audio Format Support: Capable of handling only WAV
    -Real-Time Processing: Processes audio data in real time, ensuring minimal latency.
    -Single-Client Support: Can handle multiple clients simultaneously, allowing multiple audio streams to be received and processed.
    -Error Handling: Robust error handling to manage connection issues and data integrity.
    
Requirements
    -Python 3.9 or higher
    -Libraries: socket, wave
    
Usage
    -Run the Server: Execute the server script to start listening for incoming audio streams.
    -Connect Clients: Clients can connect to the server using the specified IP address and port.
    -Receive Audio: The server will receive audio data, process it,  save it to disk.
"""

import socketserver
import wave
import socket
import os
from datetime import datetime
import logging


###Setting logger 
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
    ###Server local adress
    HOST = "0.0.0.0"
    PORT = 40500
           
class AudioServerTCPHandler(socketserver.BaseRequestHandler):
    """
    Overview
        -The AudioServerTCPHandler class extends socketserver.BaseRequestHandler to handle TCP requests for receiving audio data from ESP32 devices. 
         It processes incoming audio parameters, manages file storage, and ensures proper handling of audio data streams.

    Key Features
        -Daily Folder Creation: Automatically creates a folder for each day's audio files based on the current date.
        -Audio Parameter Extraction: Retrieves audio file parameters (channels, sample width, frame rate, etc.) from incoming data.
        -Handling ESP32 Requests: Manages different types of requests such as testing connections and receiving audio data.
        -File Management: Creates directories for storing received audio files and writes audio data to WAV files.
    Methods
        -create_daily_folder(): Creates a folder for the current date if it doesn't exist.
        -getFileParams(audioParamsBytes): Extracts audio parameters from byte data.
        -getEspHashValue(): Retrieves the hash value from the audio data.
        -getChunkNum(): Returns the current chunk number of the audio data.
        -handle(): Main method to handle incoming requests, manage audio data reception, and respond to client requests.
    """

    dataInfos = {}
    foldername = ''
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
                            break
                        except Exception as e:
                            logger.error(f"An error occurer during the reception of the file {e}")
                        if not chunk:
                            logger.info("Download complete")
                            break
                        else:
                            try:
                                audio.writeframes(chunk)
                            except Exception as e:
                                logger.error(f"An error occured during writing the .wav file {e}")
                                pass           
            self.request.sendall(b'DATA RECEIVED')
                              
if __name__ == "__main__" :
    with socketserver.TCPServer((NetworkAddress.HOST, NetworkAddress.PORT), AudioServerTCPHandler) as server:
        logger.info(f'Server started at {NetworkAddress.HOST}:{NetworkAddress.PORT}')
        server.serve_forever()

