import json
import boto3
from urllib.parse import unquote

from konlpy.tag import Okt
from collections import Counter


def get_tags(text, ntags=10):
    spliter = Okt()
    # konlpy의 Twitter객체
    nouns = spliter.nouns(text)
    # nouns 함수를 통해서 text에서 명사만 분리/추출
    count = Counter(nouns)
    # Counter객체를 생성하고 참조변수 nouns할당
    return_list = []  # 명사 빈도수 저장할 변수
    for n, c in count.most_common(ntags):
        temp = {'tag': n, 'count': c}
        if len(temp['tag'])>=2 :
            return_list.append(temp)
    # most_common 메소드는 정수를 입력받아 객체 안의 명사중 빈도수
    # 큰 명사부터 순서대로 입력받은 정수 갯수만큼 저장되어있는 객체 반환
    # 명사와 사용된 갯수를 return_list에 저장합니다.
    return return_list


def lambda_handler(event, context):
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    bucket_name = message['Records'][0]['s3']['bucket']['name']
    key_path = message['Records'][0]['s3']['object']['key']
    #@ converted to %40 error
    key_path=unquote(key_path)
    key=""
    email=""
    
    #tired-bucket/userjson에 업로드 되었을 때만
    if (bucket_name!='tired-bucket') or (key_path[:8]!='userjson'):
        print('out')
        return{
            'statusCode': 200,
            'body': json.dumps('Not Applicable')
        }
        
    if(key_path[-4:]=='json'):
        #userjson/CSE000_191125aab@gmail.com.json
        key=key_path[9:22]
        email=key_path[22:-5]
        print(key, email)
    else:
        print('out')
        return{
            'statusCode': 200,
            'body': json.dumps('Not Applicable')
        }
    
    s3=boto3.client('s3')
    bucket='tired-bucket'
    print('/tmp/'+key_path[9:])
    s3.download_file(bucket, key_path, '/tmp/'+key_path[9:])
    
   
   
    #수업내용 하이라이팅
    with open('/tmp/'+key_path[9:], encoding='utf-8') as json_file:
        dodo = json.load(json_file)
    
    count = 0
    a = " "
    k = "<html><head><meta charset=""utf-8""></head><body><div style=""width:600px;word-break:break-all;word-wrap:break-word;"">"
    for do in dodo["results"]["items"]:

        c = do["alternatives"]
        

        if (dict(c[0])["content"]==".") or (dict(c[0])["content"]=="?") or (dict(c[0])["content"]=="!") :
            count+=1
            if count==2:
                count = 1
            else :
                if float(dict(c[0])["confidence"])< 0.4:
                    k+=" <U>" + dict(c[0])["content"] + "</U>"
                    a+= " "+dict(c[0])["content"]
                else:
                    k+=" "+dict(c[0])["content"]
                    a+= " "+dict(c[0])["content"]
                k+= "<br>"
                count = 1

        else :
            if float(dict(c[0])["confidence"])< 0.4:
                k+=" <U>" + dict(c[0])["content"] + "</U>"
                a+= " "+dict(c[0])["content"]
            else:
                k+=" "+dict(c[0])["content"]
                a+= " "+dict(c[0])["content"]
            count = 0
    k+="</div><br><br>-----key words-----<br>"
    noun_count = 10
    text = a
    tags = get_tags(text, noun_count)  # get_tags 함수 실행
    for tag in tags:
        noun = tag['tag']
        count = tag['count']
        k+='{} {}'.format(noun, count)
        k+="<br>"
    k+="</body></html>"
    

    
    #html="<html><head></head><body><p>Hi!</p></body></html>"
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
