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
    job_list = []
    last_job =''
    for content in response.get('Contents'):
        if(content.get('Key')[:26] == key_path[:26]): 
            job_obj = content.get('Key') 
            transcribe = boto3.client('transcribe')
            #preprocessed/CSE000_191125.13321333Z.mp3
    #CSE000_191125.13321333
            job_name=job_obj[13:-4]
            if(job_name[-1]!='Z'): # Z로 안끝나는 job이름들을 일단 리스트에 넣어줌(Z를 맨 마지막으로 넣는작업)
                job_list.append(job_name)
            elif(job_name[-1] == 'Z'):
                last_job = job_name
                break
            #job_uri = "s3://"+bucket_name+"/preprocessed/"+job_obj+".mp3"
            job_uri = "s3://"+bucket_name+ "/" +job_obj
            transcribe.start_transcription_job(
            TranscriptionJobName= job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='mp3',
            OutputBucketName='tired-bucket',
            LanguageCode='ko-KR'
    )
    
    for j in job_list: # 리스트의 job들의 진행상태를 순차적으로 test
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=j)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                print(j, ': ', status['TranscriptionJob']['TranscriptionJobStatus']) 
                break #complete든 failed든 끝난 상태이므로 while문 빠져나가고 다시 for문으로
            print(j, ': ', status['TranscriptionJob']['TranscriptionJobStatus']) # 안끝났을때 진행상태 출력
            time.sleep(5) # 5초 후 다시 체크
    transcribe = boto3.client('transcribe')
    job_uri = "s3://"+bucket_name+"/preprocessed/"+last_job+".mp3"
    #job_uri = "s3://"+bucket_name+"/preprocessed/"+last_job+".mp3"
    print(last_job, job_uri)
    transcribe.start_transcription_job(
        TranscriptionJobName = last_job,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',
        OutputBucketName='tired-bucket',
        LanguageCode='ko-KR'
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=last_job)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            print(last_job, ': ', status['TranscriptionJob']['TranscriptionJobStatus']) 
            break #complete든 failed든 끝난 상태이므로 while문 빠져나가고 다시 for문으로
        print(last_job, ': ', status['TranscriptionJob']['TranscriptionJobStatus']) # 안끝났을때 진행상태 출력
        time.sleep(5)
     #TODO implement
    return { # 위의 for문에서 마지막 job(Z들어간 job)이 끝났을 경우 return 
        'statusCode': 200,
        'body': json.dumps('TRANSCRIPTION JOB ENDED')
    }
