import json
from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank
import scipy.io.wavfile as wav
import numpy as np
import boto3

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    #sagemaker-tired
    bucket_name = message['Records'][0]['s3']['bucket']['name']
    s3_obj = boto3.client('s3')
    key_path = message['Records'][0]['s3']['object']['key']

    reduce_mfcc = []

    print(key_path, bucket_name)
    s3_obj.download_file('sagemaker-tired', key_path, '/tmp/sage_file.wav')

    (rate,sig) = wav.read('/tmp/sage_file.wav')
    mfcc_feat = mfcc(sig,rate, nfft=2048)

    leng = np.shape(mfcc_feat)[0] // 100
    
    for i in range(leng):
        reduce_mfcc.append((mfcc_feat[i*100:i*100+101].sum(axis=0))/100.0)
       
    result = np.array(reduce_mfcc)
    print(np.shape(reduce_mfcc))
    np.save('/tmp/sage_npy', result)
    s3_obj.upload_file('/tmp/sage_npy.npy', 'sagemaker-tired', 'sleep_npy_file/'+(key_path.split('/')[1]).split('.')[0]+'.'+(key_path.split('/')[1]).split('.')[1]+'.npy')
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }