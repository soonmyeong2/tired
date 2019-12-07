import json
import boto3
from urllib.parse import unquote

def lambda_handler(event, context):
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    bucket_name = message['Records'][0]['s3']['bucket']['name']
    key_path = message['Records'][0]['s3']['object']['key']
    #@ converted to %40 error
    key_path=unquote(key_path)
    
    #tired-bucket/에 업로드 되었을 때만
    if (bucket_name!='tired-bucket') or (key_path[:3]=='raw') or (key_path[:3]=='pre'):
        print('out')
        return{
            'statusCode': 200,
            'body': json.dumps('Not Applicable')
        }
        
    if(key_path[-4:]=='json'):
        #CSE000_191125yemi0750@gmail.com.json
        key=key_path[:13]
        email=key_path[13:-5]
    elif(key_path[-3:]=='txt'):
        #CSE000_191125yemi0750@gmail.com.txt
        key=key_path[:13]
        email=key_path[13:-4]
    else:
        print('out')
        return{
            'statusCode': 200,
            'body': json.dumps('Not Applicable')
        }
    
    s3=boto3.client('s3')
    bucket='tired-bucket'
    print('/tmp/'+key_path)
    s3.download_file(bucket, key_path, '/tmp/'+key_path)
    
    #수업내용 하이라이팅
    with open('/tmp/'+key_path, encoding='utf-8') as json_file:
        dodo = json.load(json_file)

    k = "<html><head><meta charset=""utf-8""></head><body><div style=""width:600px;word-break:break-all;word-wrap:break-word;"">"
    for do in dodo["results"]["items"]:

        c = do["alternatives"]
        if float(dict(c[0])["confidence"])< 0.4:
            k+=" <U>" + dict(c[0])["content"] + "</U>"
        else:
            k+=" "+dict(c[0])["content"]

        if dict(c[0])["content"]==".":
            k+= "<br>"
    k+="</div></body></html>"

    #html 변수에 html content 저장
    html=k
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
