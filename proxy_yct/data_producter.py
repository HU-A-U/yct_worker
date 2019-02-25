# -*- coding:utf-8 -*-
from mysql_log import Mysql_log
from mysql_data import Mysql
# import threading

# import pickle
import time
# import gc
# from data_config import Config
# from threading import Timer
mysql = Mysql(database='yct_server', datatable=['yct_1'])

# signal=0
# print('出现连接异常喽')
mysql_log = Mysql_log(database='yct_server', datatable=['yct_1_log'])
def my_product(data):
    '''生产数据'''
    time_circle=time.time()
    info={'web_name':'yct','time_circle':time_circle,'parameter':str(data)}
    mysql_log = Mysql_log(database='yct_server', datatable=['yct_1_log'])
    mysql_log.insert_data(info=info)
    # import os
    # os._exit(0)
    # global signal
    # signal=1

# def my_customer():
#     '''消费数据'''
#     mysql_log = Mysql_log(database='yct_server', datatable=['yct_1_log'])
#     key_word=mysql_log.fetch_one_math()
#     data_packet=pickle.loads(eval(key_word))
#     important_info = extract.xpath_request(data_packet)
#     if not important_info:
#         return None
#     elif  'success_png' in important_info:
#         return 'success_png'
#
#     mysql.inquire_data(info=important_info)

# def customer_group():
#     '''协同消费者模式'''
#     global signal
#     if signal:
#         signal = 0
#         default_ = threading.Thread(target=my_customer)
#         default_.start()
#         default_.join()
#     global timer
#     timer = Timer(0.1, customer_group)
#     timer.start()
# customer_group()
# with open(file='./xxx.txt',encoding='utf-8',mode='r') as fol:
#     xx=fol.read()
#     fol.close()
# my_product(data=xx)

# res = client.get_logstore('cic-test', 'cic-test-logstore')
# res.log_print()