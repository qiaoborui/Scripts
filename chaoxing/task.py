"""
/*
签到领现金，每日2毛～5毛
可互助，助力码每日不变，只变日期
@感谢 小小 提供脚本雏形
活动入口：京东APP搜索领现金进入
更新时间：2021-06-07
已支持IOS双京东账号,Node.js支持N个京东账号
脚本兼容: QuantumultX, Surge, Loon, JSBox, Node.js
============Quantumultx===============
[task_local]
#签到领现金
2 0-23/4 * * * jd_cash.js, tag=签到领现金, img-url=https://raw.githubusercontent.com/Orz-3/mini/master/Color/jd.png, enabled=true
================Loon==============
[Script]
cron "2 0-23/4 * * *" script-path=jd_cash.js,tag=签到领现金
===============Surge=================
签到领现金 = type=cron,cronexp="2 0-23/4 * * *",wake-system=1,timeout=3600,script-path=jd_cash.js
============小火箭=========
签到领现金 = type=cron,script-path=jd_cash.js, cronexpr="2 0-23/4 * * *", timeout=3600, enable=true
 */
Author:str.
Description:超星学习通作业提醒
crontab : 30 * * * *
tag:学习通作业提醒

"""
import base64
import configparser
import json
import re
import os
import time
import hashlib
import requests
import sys
from lxml import etree
from requests.sessions import session
import functools
print = functools.partial(print, flush=True)

config= configparser.ConfigParser()

global currClass
currClass = 0

def setConf(username:str,section:str,option:str,value:str):
    '''在指定section中添加变量和变量值'''
    try:
        config.add_section(section)
    except configparser.DuplicateSectionError:
        sss = ("Section already exists")
        # print(sss)
    config.set(section,option,value)
    config.write(open(f'./config/{username}_config.ini', "w"))


def login(username, password):
    url = 'http://passport2.chaoxing.com/fanyalogin'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Referer': r'http://passport2.chaoxing.com/login?fid=&newversion=true&refer=http%3A%2F%2Fi.chaoxing.com'
    }

    data = {
        'fid': -1,
        'uname': username,
        'password': base64.b64encode(password.encode()).decode(),
        'refer': r'http%253A%252F%252Fi.chaoxing.com',
        't': True,
        'forbidotherlogin': 0
    }
    global session
    session = requests.session()
    session.post(url, headers=headers, data=data)


def getClass():
    url = 'http://mooc1-2.chaoxing.com/visit/courses'
    headers = {
        'User-Agent':  "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        'Referer': r'http://i.chaoxing.com/'
    }
    res = session.get(url, headers=headers)

    if res.status_code == 200:
        class_HTML = etree.HTML(res.text)
        i = 0
        global course_dict
        course_dict = {}

        for class_item in class_HTML.xpath("/html/body/div/div[2]/div[3]/ul/li[@class='courseItem curFile']"):
            try:
                class_item_name = class_item.xpath("./div[2]/h3/a/@title")[0]
                if(class_item.xpath("./div[2]/p/@style")[0] != 'color:#0099ff'):
                    i += 1
                    course_dict[i] = [class_item_name, "https://mooc1-1.chaoxing.com{}".format(
                        class_item.xpath("./div[1]/a[1]/@href")[0]) + '&ismooc2=1']
            except:
                pass
    else:
        print("error:课程处理失败")
        

def Qsend(bark:str,msg:str):
    print(msg)
    
    res = (requests.get(f'{bark}/学习通作业提醒📝/📍{msg}?icon=https://android-artworks.25pp.com/fs08/2021/11/12/7/110_c8f9ad377bab14bc4ebf17b3eabf1d37_con.png&level=timeSensitive&group=Chaoxing&sound=typewriters').text)
    
    print(res)
    res = json.loads(res)
    if res['code'] == 200:
        print('推送成功')
        
    else:
        print('推送失败')
        


def getWork(url: str,username:str,bark:str):
    headers = {
        'User-Agent':  "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        'Referer': 'http://mooc1-1.chaoxing.com/'
    }
    course_url = session.get(url, headers=headers, stream=True).url
    course_data = session.get(course_url, headers=headers)
    # 获取 work enc
    course_html = etree.HTML(course_data.text)
    enc = (course_html.xpath(
        "//*[@id='workEnc']/@value")[0])
    # 获取 work url
    list_url = course_url.replace('https://mooc2-ans.chaoxing.com/mycourse/stu?', 'https://mooc1.chaoxing.com/mooc2/work/list?').replace('courseid', 'courseId').replace('clazzid', 'classId')
    list_url = list_url.split("enc=")[0] + 'enc=' +  enc
    work_data = session.get(list_url, headers=headers)
    work_html = etree.HTML(work_data.text)
    workDetail = work_html.xpath('/html/body/div/div/div/div[2]/div[2]/ul/li')
    # 检测是否有作业未完成
    if workDetail:
        name = course_dict[currClass][0]
        print(name)
        
        for workID in workDetail:
            statu = (workID.xpath("./div[2]/p[@class='status']/text()")[0])
            work = (workID.xpath("./div[2]/p[@class='overHidden2 fl']/text()")[0])
            if(statu == '未交'):
                if workID.xpath("./div[@class='time notOver']"):
                    workid = re.search(r'workId=(\d*)&',workID.xpath("@data")[0]).group(1)
                    time = (workID.xpath(
                        "./div[@class='time notOver']/text()")[1]).replace('\n', '').replace('\r', '').replace(' ','')
                    print(name+work+time)
                    #
                    hour = re.match(r'剩余(\d*)小时', time).group(1)
                    for num in 72,48,24,12,10,8,6,5,4,3,2,1,0:
                        if config.has_option(str(num), workid) == False and int(hour) <= num:
                            setConf(username,str(num),workid,'1')
                            Qsend(bark,name + ' ' + work + ' ' + time)
                            break

def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    #print(m.hexdigest())
    return m.hexdigest()

if __name__ == '__main__':
    print(time.asctime( time.localtime(time.time()) ))
    timestamp = str(round(time.time() * 1000))
    r = requests.get("https://r5eeSMNI.api.lncldglobal.com/1.1/classes/Chaoxing",headers={
    'X-LC-Id':os.getenv('appid'),
    'X-LC-Sign':md5( timestamp + os.getenv("appkey") )+","+timestamp},timeout=None).json()
    userList = r['results']
    for dict in userList:
        username = dict['username']
        print('用户“{}”开始--------------------{}'.format(username,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
        
        password = dict['passwd']
        bark = dict['bark']
        config.read(f'./config/{username}_config.ini')
        login(username,password)
        getClass()
        for currClass in course_dict:
            getWork(course_dict[currClass][1],username,bark)
        currClass=0
        print(f'用户{username}结束-----------------------\n')
        
