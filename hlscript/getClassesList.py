import requests
from bs4 import BeautifulSoup
import re
import json

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

global s, k
k = requests.session()
s = requests.session()


sep = k.post(url="http://sep.ucas.ac.cn/slogin", data=persondict, headers=headers, timeout=10) 
jwxk = k.get('http://sep.ucas.ac.cn/portal/site/226/821')

Identitycode = re.findall(r'Identity=(.*)', jwxk.text)[0]

jl = k.get('http://jwxk.ucas.ac.cn/login?Identity=' + Identitycode, headers = headers)
cookies =k.cookies.get_dict()


# https://jwxk.ucas.ac.cn/subject/humanityLecture
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

    # print(pageInfo)

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
        # print(len(currentPageLecturesTag))

    # print(classList)
    return classList

    



A = search(cookies = cookies, headers = headers, session = s)
print(A)
