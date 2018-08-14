#!/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import requests
import time
import datetime
import shutil

#collectFile
def collectFile(path):
    filetype = ['php', 'phtml', 'inc', 'php3', 'php4', 'php5', 'war', 'jsp', 'jspx', 'asp', 'aspx', 'cer', 'cdx', 'asa', 'ashx', 'asmx', 'cfm']
    print("开始收集扫描文件")
    os.system('rm -rf SFtmp && mkdir SFtmp')
    os.system('rm -rf SFWebshell.zip')
    for root, dirs, files in os.walk(path):
        for filename in files:
            if(os.path.splitext(filename)[1][1:] in filetype):
                shutil.copyfile(os.path.join(root, filename), './SFtmp/'+root.replace('/', '^')+filename)
    print("开始打包文件内容")
    os.system('zip SFWebshell.zip ./SFtmp/*')
    print("打包成功")
    '''
    collectFileCommand = 'find . -regex ".*\(php\)"|xargs -i cp {} ./tmp/'
    os.system(collectFileCommand)
    os.system('zip SFwebshell.zip ./tmp/*')
    '''
#sendfile
def sendFile():
    sendFileCommand = 'curl https://scanner.baidu.com/enqueue -F archive=@SFwebshell.zip'
    r = os.popen(sendFileCommand).read()
    url = json.loads(r)['url']
    return url
#AnalysisResult
def analysisData(url):
    start_time = datetime.datetime.now()
    time.sleep(10)
    r = requests.get(url).text[:-1]
    print("test_url:"+url)
    json_r = json.loads(r)[0]
    while(int(json_r['total']) != int(json_r['scanned'])):
        time.sleep(5)
        print('----scanned:'+str(json_r['scanned']))
        r = requests.get(url).text[:-1]
        json_r = json.loads(r)[0]
    duration = (datetime.datetime.now() - datetime.datetime.now()).seconds
    print("total:"+str(json_r['total']))
    print("detected:"+str(json_r['detected']))
    print("Webshell is :")
    for item in json_r['data']:
        if(item['descr'] is not None):
            print(item['path'])
    total = json_r['total']
    detected = json_r['detected']
    result = json_r['data']
    reporterData(start_time, duration, total, detected, result)
    
#Reporter
def reporterData(start_time, duration, total, detected, result):
    reporter = '''
        <html>
    <head>
        <meta charset="utf-8">
        <title>SFWebShell查杀报告</title>
    </head>
    <body>
        <h1>SFWebShell查杀报告</h1>
        <strong>扫描开始时间:</strong>
        {{ start_time }}
        <br />
        <strong>扫描时长:</strong>
        {{ duration }}
        <br />
        <strong>扫描文件数:</strong>
        {{ total }}
        <br />
        <strong>检测可疑文件数:</strong>
        {{ detected }}
        <br />
        <br />
        <table>
            <tr>
                <th>文件名</th>
                <th>描述</th>
            </tr>
            {{ scan_result }}
        </table>
    </body>
</html>
    '''
    scan_result = ""
    for item in result:
        if(item['descr'] is not None):
            scan_result += "<tr><td>{}</td><td>{}</td></tr>".format(item['path'], item['descr'])
    reporter = reporter.replace("{{ start_time }}", str(start_time)).replace("{{ duration }}", str(duration)).replace("{{ total }}", str(total)).replace("{{ detected }}", str(detected)).replace("{{ scan_result }}", scan_result)
    with open('SFWebshell.html', 'w') as f:
        f.write(reporter)
    print('WebShell scan finished')

collectFile()
analysisData(sendFile())
os.system('rm -rf SFwebshell.zip')
