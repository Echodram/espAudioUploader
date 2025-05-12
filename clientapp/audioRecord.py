import uos
import time
from machine import Pin
from machine import I2S
from machine import SDCard

sd = SDCard(slot=2, mosi = 15,sck = 14,cs = 13,miso = 2)
uos.mount(sd, "/sd")

class Config :
    """
    Overview:
        The Config class defines configuration parameters for audio recording and playback using an ESP32. 
        It includes settings for pin assignments, audio format, sample rate, and buffer sizes.

    Key Attributes
        Pin Configuration:
            SCK_PIN: Pin number for the clock signal.
            WS_PIN: Pin number for the word select signal.
            SD_PIN: Pin number for the data signal.
            I2S_ID: Identifier for the I2S interface.
        Audio Configuration:
            WAV_FILE: Name of the WAV file to be recorded.
            RECORD_TIME_IN_SECONDS: Duration of the audio recording in seconds.
            WAV_SAMPLE_SIZE_IN_BITS: Bit depth of the audio samples (e.g., 32 bits).
            FORMAT: Audio format (mono or stereo).
            SAMPLE_RATE_IN_HZ: Sample rate for audio recording (e.g., 22050 Hz).
        Derived Parameters:
            NUM_CHANNELS: Number of audio channels based on the selected format.
            WAV_SAMPLE_SIZE_IN_BYTES: Size of each sample in bytes.
            RECORDING_SIZE_IN_BYTES: Total size of the recording buffer calculated based on recording duration, sample rate, and sample size.
    """
    
    SCK_PIN = 18
    WS_PIN = 25
    SD_PIN = 32
    I2S_ID = 0
    BUFFER_LENGTH_IN_BYTES = 40000

    # ======= AUDIO CONFIGURATION =======
    WAV_FILE = "mic.wav"
    RECORD_TIME_IN_SECONDS = 30
    WAV_SAMPLE_SIZE_IN_BITS = 32
    FORMAT = I2S.MONO
    SAMPLE_RATE_IN_HZ = 22050
    
    # ======= AUDIO CONFIGURATION =======
    format_to_channels = {I2S.MONO: 1, I2S.STEREO: 2}
    NUM_CHANNELS = format_to_channels[FORMAT]
    WAV_SAMPLE_SIZE_IN_BYTES = WAV_SAMPLE_SIZE_IN_BITS // 8
    RECORDING_SIZE_IN_BYTES = (
        RECORD_TIME_IN_SECONDS * SAMPLE_RATE_IN_HZ * WAV_SAMPLE_SIZE_IN_BYTES * NUM_CHANNELS
    )

class AudioRecord:
    """
    Overview
        The AudioRecorder class captures audio input using the I2S interface and saves it as a WAV file. It constructs the WAV file header, 
        records audio data, and manages file writing to an SD card.

    Key Methods
        *__init__(self)
            -Initializes the I2S audio input with specified configuration parameters (pins, sample rate, etc.).
            -Prepares an empty filename for the recorded audio.
        *create_wav_header(self, sampleRate, bitsPerSample, num_channels, num_samples)
            -Generates a WAV file header based on the provided audio parameters.
            -Returns a byte sequence representing the WAV header.
        *recordAudio(self, filename)
            -Records audio for a specified duration and saves it to a WAV file on the SD card.
            -Creates the WAV file header and writes it to the file.
            -Continuously reads audio data from the microphone and writes it to the file until the specified recording size is reached or an interruption occurs.
            Handles exceptions during recording and ensures proper file closure.
    """
    def __init__(self):
        
        self.audio_in = I2S(
            Config.I2S_ID,
            sck=Pin(Config.SCK_PIN),
            ws=Pin(Config.WS_PIN),
            sd=Pin(Config.SD_PIN),
            mode=I2S.RX,
            bits=Config.WAV_SAMPLE_SIZE_IN_BITS,
            format=Config.FORMAT,
            rate=Config.SAMPLE_RATE_IN_HZ,
            ibuf=Config.BUFFER_LENGTH_IN_BYTES,
        )
        
        self.file_name = ''

    def create_wav_header(self, sampleRate, bitsPerSample, num_channels, num_samples):
        datasize = num_samples * num_channels * bitsPerSample // 8
        o = bytes("RIFF", "ascii")  # (4byte) Marks file as RIFF
        o += (datasize + 36).to_bytes(
            4, "little"
        )  # (4byte) File size in bytes excluding this and RIFF marker
        o += bytes("WAVE", "ascii")  # (4byte) File type
        o += bytes("fmt ", "ascii")  # (4byte) Format Chunk Marker
        o += (16).to_bytes(4, "little")  # (4byte) Length of above format data
        o += (1).to_bytes(2, "little")  # (2byte) Format type (1 - PCM)
        o += (num_channels).to_bytes(2, "little")  # (2byte)
        o += (sampleRate).to_bytes(4, "little")  # (4byte)
        o += (sampleRate * num_channels * bitsPerSample // 8).to_bytes(4, "little")  # (4byte)
        o += (num_channels * bitsPerSample // 8).to_bytes(2, "little")  # (2byte)
        o += (bitsPerSample).to_bytes(2, "little")  # (2byte)
        o += bytes("data", "ascii")  # (4byte) Data Chunk Marker
        o += (datasize).to_bytes(4, "little")  # (4byte) Data size in bytes
        return o
    

    def recordAudio(self, filename):
        self.filename = filename
        wav_file = filename
        wav = open(f"/sd/{filename}", "wb")
        wav_header = self.create_wav_header(Config.SAMPLE_RATE_IN_HZ,
                                       Config.WAV_SAMPLE_SIZE_IN_BITS,
                                       Config.NUM_CHANNELS,
                                       Config.SAMPLE_RATE_IN_HZ * Config.RECORD_TIME_IN_SECONDS,)  
        num_bytes_written = wav.write(wav_header)
        mic_samples = bytearray(10000)
        mic_samples_mv = memoryview(mic_samples)
        num_sample_bytes_written_to_wav = 0
        print("Recording size: {} bytes".format(Config.RECORDING_SIZE_IN_BYTES))
        print("==========  START RECORDING ==========")
        try:
            while num_sample_bytes_written_to_wav < Config.RECORDING_SIZE_IN_BYTES:
                num_bytes_read_from_mic = self.audio_in.readinto(mic_samples_mv)
                if num_bytes_read_from_mic > 0:
                    num_bytes_to_write = min(
                        num_bytes_read_from_mic, Config.RECORDING_SIZE_IN_BYTES - num_sample_bytes_written_to_wav
                    )
                    num_bytes_written = wav.write(mic_samples_mv[:num_bytes_to_write])
                    num_sample_bytes_written_to_wav += num_bytes_written
            print("==========  DONE RECORDING ==========")
        except (KeyboardInterrupt, Exception) as e:
            print("caught exception {} {}".format(type(e).__name__, e))

        wav.close()
        





