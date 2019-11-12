import requests
import json


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
            "key": self.course_key,
            "sleeptime": self.sleep_times,
            "email": self.email
            }
        self.headers = {
            'x-api-key': self.key,
            'Content-Type': 'application/json'
            }


    def post(self):
        res = requests.post(self.URL, headers=self.headers, data=json.dumps(self.data))        
        print(res.status_code, res.reason)
