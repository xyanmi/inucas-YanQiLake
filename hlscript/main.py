import json
import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime

import time

global s,k

'''
Get class list info
'''

with open('list.csv', 'r') as csv_list:
    reader = csv.reader(csv_list, delimiter=',')
    # 遍历reader对象，打印每一行数据
    classes = []
    for row in reader:
        classes.append(
            {
                'lectureId': row[0],
                'communicationAddress': row[1],
                'subjectType': '2'
            }
        )


'''
Set Headers: If no headers, session will be permitted.
'''
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
}


'''
Open Json file: get the information
'''

with open('./config.json', 'r') as config_file:
    config = json.load(config_file)

usermode = int(config['user-info']['login-mod'])
cookies = config['user-info']['cookies']
persondict = config['user-info']['userinfo']
persondict['loginFrom'] = ''
persondict['sb'] = 'sb'

# persondict['pwd'] = '1'




limit_date = config["limit-time"]
limit_date_time = datetime(
    int(limit_date['year']),
    int(limit_date['month']),
    int(limit_date['day']),
    int(limit_date['hour']),
    int(limit_date['min']),
    int(limit_date['second'])
                           )


s = requests.session()
k = requests.session()

# Try to login, if there is error, exit the program.
sep = k.post(url="http://sep.ucas.ac.cn/slogin", data=persondict, headers=headers, timeout=10) 

message = '''Don't try again without verifying and changing the information!!!
An error has occurred in the personal information.
Please ensure that your username and password are correct.
Passwords are only supported in encoded format. You can obtain the encoded password using our reference guide.
        '''
if(len(re.findall(r'title="课程网站"', sep.text)) == 0):
    raise Exception(message)


def add(class_dict, cookies, headers):
    global s, k

    if(usermode == 1): # use person dict to login
        try:
            sep = k.post(url="http://sep.ucas.ac.cn/slogin", data=persondict, headers=headers, timeout=10) 
            jwxk = k.get('http://sep.ucas.ac.cn/portal/site/226/821')

            Identitycode = re.findall(r'Identity=(.*)', jwxk.text)[0]
            
            jl = k.get('http://jwxk.ucas.ac.cn/login?Identity=' + Identitycode, headers = headers)
            cookies =k.cookies.get_dict()
        except BaseException:
            print(message)



    result = s.post(url = 'http://jwxk.ucas.ac.cn/subject/toSign', headers = headers, cookies = cookies, data = class_dict)
    b = BeautifulSoup(result.text, 'lxml')
    data = result.content
    if data == b"success":
        return("sucess")
    elif data == b"exits":
        return("exits")
    elif data == b"conflict":
        return("time conflict")
    elif (data == b"dail"):
        return("fail")
    elif (data == b"countFail"):
        return("Count Full")
    else:
        return data

for i in classes:
        info = add(i, cookies, headers)
        print(info)

# j = 1
# while True:
#     print(f'{j}-th test:')
#     for i in classes:
#         info = add(i, cookies, headers)
#         print(info)
#     j += 1

# while True:
#     delta = limit_date_time - datetime.today()
#     if(abs(delta.seconds) < 4):
#         for i in classes:
#             info = add(i, cookies, headers)
#             print(info)
