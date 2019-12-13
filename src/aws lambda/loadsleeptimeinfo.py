
import io
import sys
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

# 1. s3에서 preprocessed에 업로드된 해당 수업의 모든 audio file들을 transcript한 json파일을 open 및 read
# 2. dynamo DB의 tired-sleeptime table에서 각 사용자의 sleeptime 리스트로부터 수면시간들을 받아옴
# 3. 기존 저장되어있던 json파일들의 이름과 사용자의 sleeptime을 비교해서 이름을 변환하여 저장
#  -> 파일명에 사용자의 식별값이 들어가야함(key 및 email) 

def lambda_handler(event, context):
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    #tired-bucket
    bucket = message['Records'][0]['s3']['bucket']['name']
    #CSE000_191125.13321333Z.json
    course_json = message['Records'][0]['s3']['object']['key']
    #CSE000_191125
    course_key=course_json[:13]
    #tired-bucket/에 업로드 되었을 때만, 마지막 json파일(Z로 구분)인 경우만 
    if (bucket!='tired-bucket') or (course_json[:3]=='raw') or (course_json[:3]=='pre') or (course_json[:3]=='use')or (course_json[-6:-5]!='Z'):
        return{
            'statusCode': 200,
            'body': json.dumps('Not Applicable')
        }
        
    s3_obj = boto3.client('s3') # 객체를 s3로 선언
    s3r=boto3.resource('s3')
    dynamodb=boto3.resource('dynamodb') # 객체를 dynamodb로 선언
    table=dynamodb.Table('tired-sleeptime') # 테이블 선언

    response = table.scan(
        FilterExpression=Attr('key').eq(course_key) # key가 CSE000_191125인 요소들 가져옴
    )
    db_items = response['Items']
        
    max_keys = 300
    course_obj = s3_obj.list_objects(Bucket=bucket, MaxKeys=max_keys) # 버킷 내 객체들 리스팅
    for content in course_obj.get('Contents'): #content별로 sleeptime 체크, 복사
        if(content.get('Key')[:13] == course_key and content.get('Key')[-5:] == '.json'): 
            # 학수번호+날짜 일치 and 확장자명이 .json이면 더 check
            # dynamodb에서 key = 학수번호+날짜인 요소들을 가져옴
            key = content.get('Key') # content의 파일명
            s3_clientobj = s3_obj.get_object(Bucket=bucket, Key=key)
            json_data = json.loads(s3_clientobj['Body'].read().decode('utf-8'))
            json_results = json_data['results']
            json_items = json_data['results']['items']
            
            time = int(key[14:22]) #13321339
            time_f=int(time/10000) # merged파일(content)의 시작 시간 (절대시간) // 1332
            time_l=int(time%10000) # merged파일(content)의 종료 시간 (절대시간) // 1339
            for db_item in db_items: # item은 해당 수업의 사용자 각각의 데이터베이스
                email = db_item['email'] # 파일이름에 쓸 사용자이메일 지정
                sst = db_item['splitsleeptime'] # json파일 분할에 쓸 사용자 수면시간 지정 (리스트)
                #상대시간 계산. milliseconds
                filename = course_key+email+'.json' # 파일명: 학수번호/날짜/이메일.json
                #jsonfile = open('/tmp/'+filename, mode='wt') # 임시 새 json파일 open
                for i in sst: # sst 리스트에 있는 sleeptime들을 모두 제어해줘야함
                    i_f=int(i/10000) # 졸기시작한 절대시간 
                    i_l=i%10000 # 졸음 끝난 절대시간
                    time_t_hour=int(i_f/100)-int(time_f/100) # 시가 다를때 60진법 기준으로 맞춰줌
                    i_f=(i_f-time_f-40*time_t_hour)
                    time_t_hour=int(i_l/100)-int(time_f/100)
                    i_l=(i_l-time_f-40*time_t_hour)
                    start_t=i_f*60-60 # json파일 내에서 사용자의 수면시작시간(상대시간)
                    end_t=i_l*60+60 # json파일 내에서 사용자의 수면종료시간
                    json_new = {"results":{"items":[], "status":"COMPLETED"}}
                    writemore = False
                    for j in json_items: # item을 하나씩 체크
                        word_type = j.get("type")
                        if word_type == "pronunciation":
                            a = int(float(j.get("start_time")))
                            b = int(float(j.get("end_time")))
                            if start_t <= a and end_t >= b:
                                json_new['results']['items'].append(j)
                                writemore = True
                            #elif start_t > a:
                                #writemore = False
                            elif end_t < b:
                                break
                        else:
                            if writemore == True:
                                json_new['results']['items'].append(j)
                            else:
                                continue
                            
                    with open('/tmp/'+filename, 'w', encoding='utf-8') as f:
                        json.dump(json_new, f, ensure_ascii=False, indent=4)
                    #json.dump(json_new, jsonfile, ensure_ascii = False)
                    print(json_new)
                    with open('/tmp/'+filename, encoding='utf-8') as json_file:
                        dodo = json.load(json_file)
                    print(dodo)
                    s3_obj.upload_file('/tmp/'+filename, bucket, 'userjson/'+filename)
#
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
