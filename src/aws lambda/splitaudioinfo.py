import json
import io
import boto3
from pydub import AudioSegment
        
def lambda_handler(event, context):
    s3=boto3.client('s3')
    s3r=boto3.resource('s3')
    bucket='tired-bucket'
    for i in event['Records']:
        type=i['eventName']
        if type != 'INSERT':
            return {
                'body':json.dumps('NOT INSERT')
            }
            
        newImage=i['dynamodb']['NewImage']
        #print(newImage)
        #{'S': 'CSE000_191201'} {'L': [{'N': '13351336'}]} {"S": "raw/CSE000_191201.13301415.mp3"}
        key=newImage['key']['S']
        sleeptime_dict=newImage['sleeptime']['L']
        sleeptime=[]
        for j in sleeptime_dict:
            sleeptime.append(j['N'])
        keypath=newImage['key_path']['S']
        print(key, sleeptime, keypath)
        #AAA111_191212 ['23002306'] raw/AAA111_191212.23002320.mp3
        
        time=int(keypath[-12:-4])
        time_f=int(time/10000)
        time_l=int(time%10000)
        
        splitsleeptime=[]
        splitsleeptime_real=[]

        for j in sleeptime:
            i_f=int(int(j)/10000)
            i_l=int(int(j)%10000)
            splitsleeptime_real.extend([i_f, i_l])
            
            #save class period
            time_t_hour=int(i_f/100)-int(time_f/100)
            i_f=(i_f-time_f-40*time_t_hour)*10000
            time_t_hour=int(i_l/100)-int(time_f/100)
            i_l=(i_l-time_f-40*time_t_hour)*10000
            
            splitsleeptime.extend([i_f, i_l])
            
        #print(splitsleeptime, splitsleeptime_real)
        print(bucket,keypath)
        s3.download_file(bucket, keypath, '/tmp/input_file.mp3')
        #s3r.Object(bucket,keypath).download_file('/tmp/input_file.mp3')

        sound=AudioSegment.from_mp3('/tmp/input_file.mp3')
        #sound=AudioSegment.from_file('/tmp/input_file.mp3', format='mp3')
        
        
        # merge sleep audio file _YW
        merge_sleep_sound = AudioSegment.empty()
        for j in range(0,len(splitsleeptime),2):
            merge_sleep_sound += sound[splitsleeptime[j]*6:splitsleeptime[j+1]*6]
        #merge_sleep_sound.export('/tmp/output_merge_audio.mp3', format="mp3")
        
        for i in range(len(merge_sleep_sound)//(1000*60)):
            split_audio = merge_sleep_sound[i*1000*60:(i+1)*1000*60]
            split_audio.export('/tmp/sage_file'+str(i)+'.wav', format="wav")
            s3r.Object('sagemaker-tired','sleep_wav_file/'+ key+'.'+str(i)+'.wav').put(Body=open('/tmp/sage_file'+str(i)+'.wav','rb')) # YW
        # end _YW
        
        for j in range(0,len(splitsleeptime),2):
            splitsound=sound[splitsleeptime[j]*6:splitsleeptime[j+1]*6]
            splitsound.export('/tmp/output_file.mp3', format="mp3")
            
            #check last audio file 
            if (j+2)==len(splitsleeptime):
                s3r.Object(bucket,'preprocessed/'+key+'.'+str(splitsleeptime_real[j])+str(splitsleeptime_real[j+1])+'Z.mp3').put(Body=open('/tmp/output_file.mp3','rb'))
                #s3.upload_file('/tmp/output_file.mp3',bucket, 'preprocessed/'+key+'.'+str(splitsleeptime_real[j])+str(splitsleeptime_real[j+1])+'Z.mp3')
            else:
                s3r.Object(bucket,'preprocessed/'+key+'.'+str(splitsleeptime_real[j])+str(splitsleeptime_real[j+1])+'.mp3').put(Body=open('/tmp/output_file.mp3','rb'))
                #s3.upload_file('/tmp/output_file.mp3',bucket, 'preprocessed/'+key+'.'+str(splitsleeptime_real[j])+str(splitsleeptime_real[j+1])+'.mp3')

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('ADDED TO DATABASE')
    }