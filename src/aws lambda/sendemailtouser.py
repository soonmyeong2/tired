##강의key, user의 email, note, keyword list가 db에 저장되어 있다고 가정함.
import json
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    
    SENDER="tired <projecttired@gmail.com>"
    AWS_REGION="us-west-2"
    CHARSET="UTF-8"
    
    key="CSE000_191125"
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('tired-email')
    
    response=table.query(
        KeyConditionExpression=Key('key').eq(key)
    )
    for i in response['Items']:
        keyword=i['keyword']
        RECIPIENT=i['email']
        SUBJECT="피곤하쥬? 필기노트/강의코드: "+i['key']
        body="피곤하쥬? 에서 전송한 필기노트입니다\n"+i['notes']+"\n\n 해당 강의의 키워드: "
        for i in keyword:
            body+=i+' '
        BODY_TEXT=(body)
        client=boto3.client('ses',region_name=AWS_REGION)
    
        response=client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT
                ]
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT
                    }
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT
                }
            },
            Source=SENDER
            # ConfigurationSetName=CONFIGURATION_SET
        )
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Email sent!')
    }
