import json
import boto3
from urllib.parse import unquote

def lambda_handler(event, context):
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    bucket_name = message['Records'][0]['s3']['bucket']['name']
    key_path = message['Records'][0]['s3']['object']['key']
    
    #tired-bucket/에 업로드 되었을 때만
    if bucket_name!='tired-bucket' or key_path[:3]=='raw' or key_path[:3]=='pre':
        return{
            'statusCode': 200,
            'body': json.dumps('Not Applicable')
        }
        
    #CSE000_191125yemi0750@gmail.com.txt
    key=key_path[:13]
    #@ converted to %40 error
    email=unquote(key_path[13:-4])
    
    #수업내용 하이라이팅
    #html 변수에 html content 저장
    html="<html><head></head><body><h1>피곤하쥬?에서 전송한 이메일입니다.</h1><p>본문: 가나다라마바사아자차카타파하가나</p><p>키워드: 가나</p></body></html>"
    
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('tired-email')
    table.put_item(
        Item={
            'key':key,
            'email':email,
            'content':html
        })
        
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
