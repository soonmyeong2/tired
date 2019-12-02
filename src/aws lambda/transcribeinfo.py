from __future__ import print_function
import time
import boto3
import json

def lambda_handler(event, context):
    transcribe = boto3.client('transcribe')
    job_name = "CSE000_191125.13321333"
    job_uri = "s3://tired-bucket/preprocessed/CSE000_191125.13321333.mp3"
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
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('TRANSCRIPTION JOB RUN')
    }

