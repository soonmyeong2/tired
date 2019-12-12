import pyaudio
import wave
import boto3
import json
import time

with open('AWS_key.json') as json_file:
    AWS_key = json.load(json_file) #key, URL

key = AWS_key["AWS_access_key"]
secret_key = AWS_key["secret_key"]


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"


def record_voice():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Start to record the audio.")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording is finished.")

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
    s3 = boto3.client('s3', aws_access_key_id=key, aws_secret_access_key=secret_key)
    # upload format CSE000_191206.13301415.mp3

    # 동기화를 위한 delay
    print('업로드 중입니다... ', end = '')
    for i in range(5, -1, -1):
        time.sleep(1)
        print('{0}.. '.format(i), end ='')

    s3.upload_file(WAVE_OUTPUT_FILENAME, 'tired-bucket', 'CSE000_191130')