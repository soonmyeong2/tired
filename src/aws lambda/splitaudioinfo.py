import json
import io
import boto3
from pydub import AudioSegment
        
def lambda_handler(event, context):
    
    s3=boto3.client('s3')
    bucket='tired-bucket'
    key_path='raw/CSE000_191125.13301410.mp3'
    key=key_path[-26:-13]
    time=int(key_path[-12:-4])
    time_f=int(time/10000)
    time_l=int(time%10000)
    
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('tired-sleeptimemerge')
    
    response=table.get_item(Key={"key":key})
    sleeptime=response['Item']['sleeptime']
    splitsleeptime=[]
    splitsleeptime_real=[]

    for i in sleeptime:
        i_f=int(i/10000)
        i_l=int(i%10000)
        splitsleeptime_real.extend([i_f, i_l])

        #save class period
        time_t_hour=int(i_f/100)-int(time_f/100)
        i_f=(i_f-time_f-40*time_t_hour)*10000
        time_t_hour=int(i_l/100)-int(time_f/100)
        i_l=(i_l-time_f-40*time_t_hour)*10000

        splitsleeptime.extend([i_f, i_l])
    
    s3.download_file(bucket, key_path, '/tmp/input_file.mp3')
    sound=AudioSegment.from_mp3('/tmp/input_file.mp3')
    for i in range(0,len(splitsleeptime),2):
        splitsound=sound[splitsleeptine[i]:splitsleeptime[i+1]]
        splitsound.export('/tmp/output_file.mp3', format="mp3")
        s3.Object(bucket, 'preprocessed/file'+i+'.mp3').put('/tmp/output_file.mp3')
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('ADDED TO DATABASE')
    }