import json
import os
import boto3
from pydub import AudioSegment
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def splitlist(sst,realtime):
    total_sleep=[]
    realtime_f=int(realtime/10000)
    realtime_l=int(realtime%10000)
    
    #splitsleeptime 불러오기
    for i in sst:
        time=int(i)
        time_f=int(time/10000)
        time_l=int(time%10000)
        
        time_t_hour=int(time_f/100)-int(realtime_f/100)
        time_f=(time_f-realtime_f-40*time_t_hour)*10000
        time_t_hour=int(time_l/100)-int(realtime_f/100)
        time_l=(time_l-realtime_f-40*time_t_hour)*10000
        
        total_sleep.append(time_f)
        total_sleep.append(time_l)
            
    total_sleep.sort()
    return total_sleep

def lambda_handler(event, context):
    #https://docs.aws.amazon.com/ko_kr/ses/latest/DeveloperGuide/examples-send-using-sdk.html
    
    SENDER="tired <projecttired@gmail.com>"
    AWS_REGION="us-west-2"
    CHARSET="UTF-8"
    
    for i in event['Records']:
        type=i['eventName']
        if type != 'INSERT':
            return{
               'body':json.dumps('NOT INSERT')
            }
            
        newImage=i['dynamodb']['NewImage']
        key=newImage['key']['S']
        email=newImage['email']['S']
        content=newImage['content']['S']
        
        RECIPIENT=email
        SUBJECT="피곤하쥬? 필기노트/강의코드: "+key
        BODY_HTML=content
        
        client=boto3.client('ses',region_name=AWS_REGION)
        
        msg=MIMEMultipart('mixed')
        msg['Subject']=SUBJECT
        msg['From']=SENDER
        msg['To']=RECIPIENT
        
        msg_body=MIMEMultipart('alternative')
        
        html_part=MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
        msg_body.attach(html_part)
        msg.attach(msg_body)
        
        
        db=boto3.resource('dynamodb')
        s3=boto3.client('s3')
        table=db.Table('tired-sleeptime')
        dbresponse=table.get_item(
            Key={
                'key':key,
                'email':email
            }
        )
        
        #to get s3 keypath
        delimiter = '/raw'
        max_keys = 300
        raw_key_path=""
        response = s3.list_objects(Bucket='tired-bucket', Delimiter=delimiter, MaxKeys=max_keys)
        for content in response.get('Contents'):
            #raw/CSE000_191125.13321333.mp3
            if(content.get('Key')[:17]=='raw/'+key):
                raw_key_path=content.get('Key')
        print(raw_key_path)
        ssst=splitlist(dbresponse['Item']['splitsleeptime'],int(raw_key_path[-12:-4]))
        s3.download_file('tired-bucket', raw_key_path, '/tmp/input_file.mp3')
        sound=AudioSegment.from_mp3('/tmp/input_file.mp3')
        
        splitsound=sound[ssst[0]*6:ssst[1]*6]
        print((ssst[0]*6), (ssst[1]*6))
        splitsound.export('/tmp/output_file.mp3', format="mp3")
        ATTACHMENT="/tmp/output_file.mp3"
        att=MIMEApplication(open(ATTACHMENT, 'rb').read())
        att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
        msg.attach(att)
        
        try:
            response=client.send_raw_email(
                Source=SENDER,
                Destinations=[RECIPIENT],
                RawMessage={
                    'Data':msg.as_string(),
                })
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent!")
            
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Email sent!'),
        'event':event
    }
