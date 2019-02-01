# -*- coding:utf-8 -*-
from mitmproxy import addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
from yct_database import Mysql
import threading
from full_extract import Extract
import pickle
import time
# from data_config import Config
from threading import Timer
from aliyun.log.logitem import LogItem
from aliyun.log import ListLogstoresRequest
from aliyun.log.logclient import LogClient
from aliyun.log.putlogsrequest import PutLogsRequest
signal=0
'''登录相关账号'''
endpoint = 'https://cn-shanghai.log.aliyuncs.com'       # 选择与上面步骤创建Project所属区域匹配的Endpoint
accessKeyId = 'LTAIVP2aFIcUAwHa'    # 使用您的阿里云访问密钥AccessKeyId
accessKey = 'TowF0ivIWJjc78HCRJBZ4915rJhOxS'      # 使用您的阿里云访问密钥AccessKeySecret
project = 'cic-test'        # 上面步骤创建的项目名称
logstore = 'cic-test-logstore'       # 上面步骤创建的日志库名称
topic = ""
source = ""
# 重要提示：创建的logstore请配置为4个shard以便于后面测试通过
# 构建一个client
client = LogClient(endpoint, accessKeyId, accessKey)
extract=Extract()
'''查找项目'''
res = client.list_project()
all_project=res.get_projects()
for alone_project in all_project:
    if project in alone_project['projectName']:
        break
else:
    '''创建项目'''
    client.create_project(project, "{}测试用例".format(project))
'''查找日志库'''
request = ListLogstoresRequest(project)
res = client.list_logstores(request)
for alone_logstore in res.get_logstores():
    if logstore in alone_logstore:
        break
else:
    '''创建日志库'''
    res = client.create_logstore(project, logstore, ttl=30, shard_count=4)

def my_product(data):
    '''生产数据'''
    import os
    os._exit(0)
    logitemList = []
    contents=[('big_data',str(data))]
    logItem = LogItem()
    logItem.set_time(time.time())
    logItem.set_contents(contents)
    logitemList.append(logItem)
    req2 = PutLogsRequest(project, logstore, topic, source, logitemList)
    res2 = client.put_logs(req2)
    res2.log_print()
    global signal
    signal=1

def my_customer():
    '''消费数据'''
    listShardRes = client.list_shards(project, logstore)
    for shard in listShardRes.get_shards_info():
        '''读取上1.4秒写入的数据全部读取出来'''
        shard_id = shard["shardID"]
        start_time = int(time.time() - 2.2)
        end_time = start_time + 2.2
        res = client.get_cursor(project, logstore, shard_id, start_time)
        res.log_print()
        start_cursor = res.get_cursor()
        res = client.get_cursor(project, logstore, shard_id, end_time)
        end_cursor = res.get_cursor()
        while True:
            loggroup_count = 1  # 每次读取5个包
            res = client.pull_logs(project, logstore, shard_id, start_cursor, loggroup_count, end_cursor)
            container = res.get_loggroup_json_list()
            if container:
                logs = container[0]['logs']
                if logs:
                    for log in logs:
                        big_data=log['big_data']
                        data_packet=pickle.loads(eval(big_data))
                        important_info = extract.xpath_request(data_packet)
                        if not important_info:
                            continue
                        elif  'success_png' in important_info:
                            continue
                        mysql=Mysql(database='yct_server', datatable=['yct_1'])
                        print(important_info,'\n------------------------------------------------\n')
                        mysql.inquire_data(info=important_info)
            next_cursor = res.get_next_cursor()
            if next_cursor == start_cursor:
                break
            start_cursor = next_cursor

def customer_group():
    '''协同消费者模式'''
    global signal
    print(signal)
    if signal:
        signal = 0
        default_ = threading.Thread(target=my_customer)
        default_.start()
        default_.join()
    global timer
    timer = Timer(1, customer_group)
    timer.start()
customer_group()
# with open(file='./xxx.txt',encoding='utf-8',mode='r') as fol:
#     xx=fol.read()
#     fol.close()
# my_product(data=xx)

# res = client.get_logstore('cic-test', 'cic-test-logstore')
# res.log_print()