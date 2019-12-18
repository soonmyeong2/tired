# source code

## discription

### Lmabda func
* Post sleeptime info
- API Gateway를 통해 받은 사용자의 수면 시간을 분할하여 tired-sleeptime
db에 저장한다. 이때 13301330처럼 1분 이내로 잔 기록은 제외한다.
* Merge sleeptime info
- Key가 같으면 같은 강의라고 판단, audio파일이 업로드된 강의의 수강생
전체의 수면 시간을 병합한다. 9999로 입력된 시간은 강제종료된 것을
의미하므로, 강의 종료 절대시간으로 변환하여 저장한다.
Check: 해당 강의의 수강생의 수면 정보를 모두 불러와서, 9999인 경우
예외처리를 통해 db의 item을 갱신하고, 전체를 하나의 list에 저장한다.
Sleeptimemerge : 전체 수강생의 수면시간이 담긴 list를 받아와서 이를 병합한다.
* Split Audio file
- Db에 병합된 수면시간이 추가되면, s3에서 해당 key를 가진 음성파일을
다운로드받아서 병합된 수면시간에 따라 이를 분할, preprocessed 폴더에
저장한다. 이때 마지막 파일은 ‘Z’를 붙여 표시한다.
* Send Email to User
- 사용자별로 tired-email db에 강의 키와 email주소, html메일 내용이
업로드되면 해당 내용의 이메일에 분할된 음성 파일을 첨부하여 사용자에게
이메일을 전송한다.


## run

```
1. Git clone https://github.com/soonmyeong2/tired
2. Cd tired/src
3. Pip install –r requirement.txt
4. Put in src foleder AWS_key.json
5. Put in src/etc facelandmark.dat
[사용자 매뉴얼]
Cmd >> Python main.py course e-mail (in src folder)
…
run
….
Exit ‘q’
[강의자 매뉴얼]
Cd audio2S3/
Cmd >> python audio2S3
…
recording
….
Exit ‘q’
```
