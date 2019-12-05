import json
import boto3

def lambda_handler(event, context):
    
    key=event['key']
    sleeptime=event['sleeptime']
    email=event['email']
    
    sst=list(map(int,sleeptime.split('/')))
    
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('tired-sleeptime')
    
    table.put_item(
        Item={
            'key': key,
            'sleeptime': sleeptime,
            'email': email,
            'splitsleeptime':sst
        })
        
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('ADDED TO DATABASE')
    }
