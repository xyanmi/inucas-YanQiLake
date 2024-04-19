import tkinter as tk

import json
import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime

import time


global s, k, cookies,count,state

def inf(index, data):
    if data == b"success":
        return(f"第{index+1}课程预约成功！")
    elif data == b"existLecture":
        return(f"第{index+1}课程已经存在！")
    elif data == b"conflict":
        return(f"第{index+1}课程时间冲突！")
    elif (data == b"fail"):
        return(f"第{index+1}课程无法报名！")
    elif (data == b"countFail"):
        return(f"第{index+1}课程人数已满！")
    elif (data == b'reserveTimeFail'):
        return(f"第{index+1}课程选课时间错误！")
    else:
        return f"第{index+1}课程未知错误！"



'''
get the information of classes
'''
def search(cookies, headers, session):

    '''
    Get the page information: the numbers of pages, current page and the numbers of all classes / lecture
    '''
    result = session.post(url = 'https://jwxk.ucas.ac.cn/subject/humanityLecture', headers = headers, cookies = cookies)
    soup = BeautifulSoup(result.text, 'lxml')

    pageInfoTag = soup.find_all('div', attrs={'class':'bn-info'})[0]
    pageInfo = re.findall(r'\d+', pageInfoTag.text)
    pageInfo = {
        'classesNums': int(pageInfo[0]),
        'currentPage': int(pageInfo[1]),
        'pageNums': int(pageInfo[2])
    }


    classList = []
    for page in range(1, pageInfo['pageNums'] + 1):
        data = {
            'pageNum': str(page)
        }
        result = session.post(url = 'https://jwxk.ucas.ac.cn/subject/humanityLecture', headers = headers, cookies = cookies, data = data)
        soup = BeautifulSoup(result.text, 'lxml')

        currentPageLecturesTag = soup.find_all('tr')
        currentPageLecturesTag.pop(0)
        for class_line in currentPageLecturesTag:
            class_dict = {
                'lecture-name':'',
                'period':'',
                'lecture-time':'',
                'object':'',
                'speaker':'',
                'lecture-id':''
            }
            currentInfo = re.findall(r'<td>(.*)</td\>', str(class_line))
            lid = re.findall(r'<a href="/subject/(.*)/humanityView"', str(class_line))[0]

            class_dict['lecture-name'] = currentInfo[0]
            class_dict['period'] = currentInfo[1]
            class_dict['lecture-time'] = currentInfo[2]
            class_dict['object'] = currentInfo[3]
            class_dict['speaker'] = currentInfo[4]
            class_dict['lecture-id'] = lid

            classList.append(class_dict)

    return classList
    

def showclasses(classBox):
    global cookies, s
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    classBox.delete(0, tk.END)
    if(len(cookies) <= 1):
        classBox.insert(tk.END, 'Error for login!')
    else:
        classList = search(cookies= cookies, headers= headers, session=s)
        
        for lecture in classList:
            classBox.insert(tk.END,f"{lecture['lecture-name']}  {lecture['period']}   {lecture['lecture-time']}   {lecture['speaker']}   预约中")

def loginInSep(username, password, personnel, messaageClient):

    global cookies

    k = requests.session()

    personnel['userName'] = username.get()
    personnel['pwd'] = password.get()

    messaageClient.delete(1.0,tk.END)
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    sep = k.post(url="http://sep.ucas.ac.cn/slogin", data=personnel, headers=headers, timeout=10) 

    message = '''Don't try again without verifying and changing the information!!!
An error has occurred in the personal information.Please ensure that your username and password are correct.Passwords are only supported in encoded format. You can obtain the encoded password using our reference guide.
            '''
    if(len(re.findall(r'title="课程网站"', sep.text)) == 0):
        messaageClient.insert(tk.INSERT, message + '\n')
        cookies = k.cookies.get_dict()
        return False
    else:
        messaageClient.insert(tk.INSERT, 'Login susscessful!')
        jwxk = k.get('http://sep.ucas.ac.cn/portal/site/226/821')

        Identitycode = re.findall(r'Identity=(.*)', jwxk.text)[0]
        jl = k.get('http://jwxk.ucas.ac.cn/login?Identity=' + Identitycode, headers = headers)
        cookies = k.cookies.get_dict()
        return True
    
def sign(classListBox, messageClient):
    global cookies, s, k
    
    message = '''Don't try again without verifying and changing the information!!!
An error has occurred in the personal information.Please ensure that your username and password are correct.Passwords are only supported in encoded format. You can obtain the encoded password using our reference guide.
            '''
    
    index = classListBox.curselection()

    try:
        sep = k.post(url="http://sep.ucas.ac.cn/slogin", data=persondict, headers=headers, timeout=10) 
        jwxk = k.get('http://sep.ucas.ac.cn/portal/site/226/821')

        Identitycode = re.findall(r'Identity=(.*)', jwxk.text)[0]
        
        jl = k.get('http://jwxk.ucas.ac.cn/login?Identity=' + Identitycode, headers = headers)
        cookies =k.cookies.get_dict()
    except BaseException:
        messageClient.insert(tk.INSERT, message + '\n')
        cookies = k.cookies.get_dict()

    classList = search(cookies= cookies, headers= headers, session=s)


    for i in index:
        class_dict = {
            'lectureId': classList[i]['lecture-id'],
            'communicationAddress': classList[i]['lecture-time'],
            'subjectType': '2'
        }

        result = s.post(url = 'http://jwxk.ucas.ac.cn/subject/toSign', headers = headers, cookies = cookies, data = class_dict)
        b = BeautifulSoup(result.text, 'lxml')
        data = result.content

        print(data)

        message__ = inf(i, data)
        messageClient.insert(tk.INSERT, message__ + '\n')


    
    





s = requests.session()
k = requests.session()
count = 0
state = False

'''
Set Headers: If no headers, session will be permitted.
'''
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
}


'''
get some information in config file
'''
with open('./config.json', 'r') as config_file:
    config = json.load(config_file)

usermode = int(config['user-info']['login-mod'])
cookies = config['user-info']['cookies']
persondict = config['user-info']['userinfo']
persondict['loginFrom'] = ''
persondict['sb'] = 'sb'

# sep = k.post(url="http://sep.ucas.ac.cn/slogin", data=persondict, headers=headers, timeout=10) 
# jwxk = k.get('http://sep.ucas.ac.cn/portal/site/226/821')

# Identitycode = re.findall(r'Identity=(.*)', jwxk.text)[0]

# jl = k.get('http://jwxk.ucas.ac.cn/login?Identity=' + Identitycode, headers = headers)
# cookies =k.cookies.get_dict()





root_window = tk.Tk()

root_window.title('UCAS人文讲座报名工具')
root_window.geometry('1000x600')
root_window.iconbitmap('./favicon.ico')
root_window["background"] = "white"

'''
Login Window
'''

username_var = tk.StringVar()
password_var = tk.StringVar()

# En=Entry(root,textvariable=e).pack()
# #对象值设定
# e.set('Entry')

username_text = tk.Label(root_window, text="用户名", bg="white", fg="black", font=('宋体',13,))
password_text = tk.Label(root_window, text="密  码", bg = 'white', fg="black", font=('宋体',13,))
username = tk.Entry(root_window, bd = 2, width=32, font=('Times',11,),textvariable=username_var)
password = tk.Entry(root_window, bd = 2, width=32, font=('Times',11,),textvariable=password_var)


# username['height'] = 2


username_text.place(x=680, y=35)
username.place(x=750, y=35)
password_text.place(x=680, y=75)
password.place(x=750, y=75)


username_var.set(persondict['userName'])
password_var.set(persondict['pwd'])

persondict['userName'] = username.get()
persondict['pwd'] = password.get()


# print(username.get())


'''
classes Window
'''  
classInfoMargin = tk.Label(root_window, text="                       课程名称                                     学时               时间              主讲人         状态   ", bg="white", fg="black")
classListBox=tk.Listbox(root_window, selectmode=tk.MULTIPLE, width = 90, bd = 2, height = 27)

classInfoMargin.place(x = 20, y = 30)
classListBox.place(x = 20, y = 60)

getclassbtn = tk.Button(root_window, text="获取", font=('宋体', 12,), command=lambda : showclasses(classListBox))
getclassbtn.place(x = 840, y = 115)





message_box = tk.Text(root_window, height = 27, width = 43, bd = 2)
message_box.place(x = 670, y = 195)


login = tk.Button(root_window, text="登录", font=('宋体', 12,), command=lambda : loginInSep(username, password, persondict, message_box))
login.place(x = 780, y = 115)



def go(classListBox, messageClient):
    global count,state
    

    #to get ...
    # while True:
    #     count += 1
    #     messageClient.delete(1.0,tk.END)
    #     messageClient.insert(tk.INSERT, f'{count}次预约结果，请等待\n')
    #     sign(classListBox, messageClient)
    print(1)


    count += 1
        
    messageClient.delete(1.0,tk.END)
    messageClient.insert(tk.INSERT, f'{count}次预约结果，请等待\n')
    sign(classListBox, messageClient)



def t():
    global state

    state = not state

signbtn = tk.Button(root_window, text="             预约              ", font=('宋体', 12,), command = t)
signbtn.place(x=700, y=155)

def loop():
    if(state):
        go(classListBox, message_box)
        
    return root_window.after(100, loop)

loop()

root_window.mainloop()