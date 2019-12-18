import requests
import json
from datetime import datetime, timedelta


class tiredDB_API:
    def __init__(self, course_key, email, sleep_times):

        with open('API_key.json') as json_file:
            API_data = json.load(json_file) #key, URL

        self.key = API_data["key"]
        self.URL = API_data["URL"]
        
        self.course_key = course_key
        self.email = email
        self.sleep_times = sleep_times
        
        self.data = {
            "key": self.course_key + str(datetime.now().year).replace("20", "_") + str(datetime.now().month).rjust(2, '0') + str(datetime.now().day).rjust(2, '0'),
            "sleeptime": self.sleep_times,
            "email": self.email
            }
        self.headers = {
            'x-api-key': self.key,
            'Content-Type': 'application/json'
            }


    def post(self):
        res = requests.post(self.URL, headers=self.headers, data=json.dumps(self.data))
        '''
        if res.status_code == '429':
            for _ in range(5):
                res = requests.post(self.URL, headers=self.headers, data=json.dumps(self.data))
                sleep(10)
        '''
                
        print(res.status_code, res.reason)
