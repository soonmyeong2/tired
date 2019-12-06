import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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
