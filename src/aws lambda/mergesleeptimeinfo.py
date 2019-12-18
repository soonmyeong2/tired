import json
import boto3
from boto3.dynamodb.conditions import Key

def check(response, table, course_end_time):
    total=[]
    updateb=False
    item=[]
    
    #splitsleeptime 불러오기
    for i in response['Items']:
        sstitem=i['splitsleeptime']
        
        for j in sstitem:
            time=j
            time=int(time)
        
            #sleeptime이 9999면 강의끝시간으로 변경
            if (int(time)%10000) == 9999:
                time-=(9999-course_end_time)
                updateb=True
            
            item.append(time)
            total.append(time)
            
        if updateb:
            table.update_item(
                Key={
                    'key':i['key'],
                    'email':i['email']
                },
                UpdateExpression="set sleeptime = :s, splitsleeptime = :l",
                ExpressionAttributeValues={
                    ':s':i['sleeptime'],
                    ':l':item
                },
                ReturnValues="UPDATED_NEW"
            )
            updateb=False
        item=[]
            
    return total
        
def sleeptimemerge(total):
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
        
    print(event)
    print(message)
    #coursekey CSE000_191125.13301415.mp3
    key=key_path[-26:-13]
    course_end_time=int(key_path[-8:-4])
    
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('tired-sleeptime')
    
    response=table.query(
        KeyConditionExpression=Key('key').eq(key)
    )
    
    #9999 예외처리, 전체 수면시간 list 생성
    sst_total=check(response, table, course_end_time)
    #전체 수면시간 merge
    sst_merge=sleeptimemerge(sst_total)
    
    table_merge=dynamodb.Table('tired-sleeptimemerge')
    table_merge.put_item(
        Item={
            'key':key,
            'sleeptime':sst_merge,
            'key_path':key_path
        })
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('ADDED TO DATABASE')
    }