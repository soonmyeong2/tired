#!/usr/bin/env python
import subprocess
import os
import sys
from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank
import scipy.io.wavfile as wav
import numpy as np

reduce_mfcc = []

files_list = os.listdir(sys.argv[1])
for file_name in files_list:
    file_path_input = sys.argv[1] + file_name
    raw_file_name = os.path.basename(file_name).split('.')[0]
    file_path_output = sys.argv[2] + raw_file_name + '.wav'
    command = "ffmpeg -i " + file_path_input + " -codec:a pcm_s16le -ac 1 " + file_path_output
    subprocess.call(command, shell=True)
    
wav_list = os.listdir(sys.argv[2])
for file_name in wav_list:
    reduce_mfcc.clear()
    wav_path_input = sys.argv[2] + file_name
    save_path = sys.argv[3] + file_name
    (rate,sig) = wav.read(wav_path_input)
    mfcc_feat = mfcc(sig,rate, nfft=2048)
    leng = np.shape(mfcc_feat)[0] // 100
    
    for i in range(leng):
        reduce_mfcc.append((mfcc_feat[i*100:i*100+101].sum(axis=0))/100.0)
        
    result = np.array(reduce_mfcc)
    print(mfcc_feat)
    print(np.shape(reduce_mfcc))
    np.save(save_path[:-4], result)
