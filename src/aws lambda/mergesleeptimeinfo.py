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
    
    bucket_name=event['Records'][0]['s3']['bucket']['name']
    key_path=event['Records'][0]['s3']['object']['key']
    if bucket_name!='tired-bucket' or key_path[:3]=='pre':
        return{
            'statusCode': 200,
            'body': json.dumps('Not Applicable')
        }
        
    key=key_path[-19:-13]
    
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
            'sleeptime':sstmerge
        })
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('ADDED TO DATABASE'),
        'response':response
    }
