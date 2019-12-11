from __future__ import print_function
import time
import boto3
import json

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    #tired-bucket
    bucket_name = message['Records'][0]['s3']['bucket']['name']

    s3_obj = boto3.client('s3')
    key_path = message['Records'][0]['s3']['object']['key']
    print(message['Records'][0]['s3']['object'])
    #preprocessed/CSE000_191125.13321333Z.mp3
    #tired-bucket/preprocessed/에 업로드 되었을 때만, 마지막 음성파일(Z로 구분)인 경우만 transcribe
    if (bucket_name!='tired-bucket') or (key_path[:3]!='pre') or (key_path[-5:-4]!='Z'):
            return{
                'statusCode': 200,
                'body': json.dumps('Not Applicable')
            }
    delimiter = '/preprocessed'
    max_keys = 300
    response = s3_obj.list_objects(Bucket='tired-bucket', Delimiter=delimiter, MaxKeys=max_keys)
    for content in response.get('Contents'):
        if(content.get('Key')[:26] == key_path[:26]): 
            job_obj = content.get('Key') 
            transcribe = boto3.client('transcribe')
            #preprocessed/CSE000_191125.13321333Z.mp3
    #CSE000_191125.13321333
            job_name=job_obj[13:-4]
            job_uri = "s3://"+bucket_name+"/"+job_obj
            transcribe.start_transcription_job(
            TranscriptionJobName= job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='mp3',
            OutputBucketName='tired-bucket',
            LanguageCode='ko-KR'
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
    print(status)
     #TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('TRANSCRIPTION JOB RUN')
    }
