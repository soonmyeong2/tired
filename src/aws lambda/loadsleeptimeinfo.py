import io
import sys
import boto3
import json

# 1. s3에서 merged-time 기준으로 transcript된 json파일을 open 및 read
# 2. dynamo DB의 tired-sleeptime table에서 각 사용자의 sleeptime 리스트로부터 수면시간들을 받아옴
# 3. transcription 내 상대시간으로 변환(단위: 초)
# 4. 사용자 수면시간 범위에 맞게 transcription을 분할해서 text파일에 써줌
#   -> 파일명에 사용자의 식별값이 들어가야함(key 및 email)

def lambda_handler(event, context):
    s3_obj = boto3.client('s3') # 객체를 s3로 선언
    s3_clientobj = s3_obj.get_object(Bucket='tired-bucket', Key='CSE000_191125.13321333.json')
    s3_clientdata = json.loads(s3_clientobj['Body'].read().decode('utf-8'))
    json_data = s3_clientdata
    #bucket='tired-bucket' # s3의 버킷을 지정: 'tired-bucket'
    key_path='CSE000_191125.13321333.json' # 경로
    key = key_path[:13]
    email = "yemi0750@gmail.com"
    time=int(key_path[-13:-5]) # sleeptime을 나타내는 부분
    time_f=int(time/10000) # 졸기 시작한 시간
    time_l=time%10000 # 졸기 끝난 시간
    
    
    json_results = json_data.get("results") # json_results:dict
    json_items = json_results.get("items")
    dynamodb=boto3.resource('dynamodb') # 객체를 dynamodb로 선언
    table=dynamodb.Table('tired-sleeptime') # 테이블 선언
    response=table.get_item(Key={"key": key, "email": email}) # table에서 key를 입력하면 아이템을 받아오고, 이를 response에 할당
    sleeptime=response['Item']['sleeptime'] # response 테이블의 한 값
    filename = key + email + ".txt"
    sst=response['Item']['splitsleeptime']
    print(sst)
    #상대시간 계산. milliseconds
    for i in sst: #sst 리스트에 있는 sleeptime들을 모두 제어해줘야함
        i_f=int(i/10000) 
        i_l=i%10000
        #split.extend([(i_f-time_f)*1000, (i_l-time_f)*1000])
        time_t_hour=int(i_f/100)-int(time_f/100)
        i_f=(i_f-time_f-40*time_t_hour)
        time_t_hour=int(i_l/100)-int(time_f/100)
        i_l=(i_l-time_f-40*time_t_hour)
        start_t=i_f*60-300
        end_t=i_l*60+300
        txtfile = open('/tmp/'+filename, mode='wt', encoding='utf-8')
        for j in json_items:
            word_type = j.get("type")
            if word_type == "pronunciation":
                a = int(float(j.get("start_time")))
                b = int(float(j.get("end_time")))
                if start_t <= a and end_t >= b:
                    alt = j.get("alternatives") 
                    cont = alt[0].get("content")
                    txtfile.write(cont + ' ')    
            else: 
                alt = j.get("alternatives") 
                cont = alt[0].get("content")
                txtfile.write(cont + ' ')
        s3_obj.upload_file('/tmp/'+filename, 'tired-bucket', filename)

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

