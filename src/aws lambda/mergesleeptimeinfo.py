import json
import boto3
from boto3.dynamodb.conditions import Key

def check(response):
    
    total=[]
    for i in response['Items']:
        total.extend(i['splitsleeptime'])
    total.sort()
    result=[]
    
    mid_f=0
    mid_l=0
    
    for idx in range(len(total)):
        
        i=total[idx]
        f=int(i/10000)
        l=i%10000
        
        if idx==0 :
            mid_f=f
            mid_l=l
            continue
        
        if f>=mid_f and l<=mid_l:
            print(f)
        elif f>mid_l:
            result.append(mid_f*10000+mid_l)
            mid_f=f
            mid_l=l
        elif f>=mid_f and l>mid_l:
            mid_l=l
            
        if idx==len(total)-1:
            result.append(mid_f*10000+mid_l)
            
    return result
        
def lambda_handler(event, context):
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    bucket_name = message['Records'][0]['s3']['bucket']['name']
    key_path = message['Records'][0]['s3']['object']['key']
    
    #tired-bucket/raw/에 업로드 되었을 때만 merge
    if bucket_name!='tired-bucket' or key_path[:3]!='raw':
        return{
            'statusCode': 200,
            'body': json.dumps('Not Applicable')
        }
        
    #coursekey CSE000_191125.13301415.mp3
    key=key_path[-26:-13]
    
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('tired-sleeptime')
    
    response=table.query(
        KeyConditionExpression=Key('key').eq(key)
    )
    
    table_merge=dynamodb.Table('tired-sleeptimemerge')
    sstmerge=check(response)
        
    table_merge.put_item(
        Item={
            'key':key,
            'sleeptime':sstmerge,
            'key_path':key_path
        })
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('ADDED TO DATABASE')
    }