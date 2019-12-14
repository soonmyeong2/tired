import pyaudio
import wave
import boto3
import json
import time
from pydub import AudioSegment
import keyboard
from datetime import datetime, timedelta


with open('AWS_key.json') as json_file:
    AWS_key = json.load(json_file) #key, URL

key = AWS_key["AWS_access_key"]
secret_key = AWS_key["secret_key"]


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
#RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.mp3"
RECORD_START_TIME = ""
RECORD_END_TIME = ""

def record_voice():
    global RECORD_START_TIME, RECORD_END_TIME
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Start to record the audio.\nEnter 'q' to end recording.")
    RECORD_START_TIME = str(datetime.now().hour).rjust(2, "0")+ str(datetime.now().minute).rjust(2, "0")

    frames = []

    #for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    while True:
        if keyboard.is_pressed('q'):
            break
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording is finished.")
    RECORD_END_TIME = str(datetime.now().hour).rjust(2, "0")+ str(datetime.now().minute).rjust(2, "0")

    stream.stop_stream()
    stream.close()
    p.terminate()

    ### output file 
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def upload_s3():
    # CSE000_191125.13301410.mp3
    file_name = input("\nCourse number : ")
    file_name += str(datetime.now().year).replace("20", "_")\
                 + str(datetime.now().month).rjust(2, '0')\
                 + str(datetime.now().day).rjust(2, '0')\
                 + "."\
                 + RECORD_START_TIME\
                 + RECORD_END_TIME\
                 + ".mp3"
                 
    # 동기화를 위한 delay
    print('Uploading... ', end = '')
    for i in range(5, 0, -1):
        time.sleep(1)
        print('{0}.. '.format(i), end ='')
    s3=boto3.resource('s3', aws_access_key_id=key, aws_secret_access_key=secret_key)
    s3.Object('tired-bucket', 'raw/'+file_name).put(Body=open(WAVE_OUTPUT_FILENAME,'rb'))
    print("\nComplete.")
    
record_voice()
upload_s3()
