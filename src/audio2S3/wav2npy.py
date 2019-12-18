#!/usr/bin/env python
import subprocess
import os
import sys
from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank
import scipy.io.wavfile as wav
import numpy as np
from pydub import AudioSegment

reduce_mfcc = []

sound=AudioSegment.from_mp3('output.mp3')


for i in range(len(sound)//(1000*60)):
    split_audio = sound[i*1000*60:(i+1)*1000*60]
    split_audio.export('./tmp/sage_file'+str(i)+'.wav', format="wav")
    #s3r.Object('sagemaker-tired','sleep_wav_file/'+ key+'.'+str(i)+'.wav').put(Body=open('/tmp/sage_file'+str(i)+'.wav','rb')) # YW


wav_list = os.listdir('/tmp')
for file_name in wav_list:
    print(file_name)
    reduce_mfcc.clear()
    wav_path_input = '/tmp/' + file_name
    save_path = './result/' + file_name
    print(save_path)
    (rate,sig) = wav.read(wav_path_input)
    mfcc_feat = mfcc(sig,rate, nfft=2048)
    leng = np.shape(mfcc_feat)[0] // 100
    
    for i in range(leng):
        reduce_mfcc.append((mfcc_feat[i*100:i*100+101].sum(axis=0))/100.0)
        
    result = np.array(reduce_mfcc)
    print(mfcc_feat)
    print(np.shape(reduce_mfcc))

    np.save('./result/'+file_name, result)
