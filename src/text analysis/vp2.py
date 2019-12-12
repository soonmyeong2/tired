import json
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

with open('CSE000_191125.13321333.json', encoding='utf-8') as json_file:
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
k+="</div>"
print (k)
print ("<br><br>")
p= "key words<br>"
noun_count = 10
text = dodo["results"]["transcripts"]
tags = get_tags(text, noun_count)  # get_tags 함수 실행
for tag in tags:
    noun = tag['tag']
    count = tag['count']
    p+='{} {}\n'.format(noun, count)
print(p)
print("</body></html>")





