# -*- coding:utf-8 -*-
'''创建celery应用'''

#定义未来文件的绝对进口
from __future__ import absolute_import


'''启动命令'''
# celery -A handle_data worker -l info -Q to_product  -P eventlet 生产数据

# celery -A handle_data worker -l info -Q to_analysis -P eventlet 解析数据

# celery -A handle_data worker -l info -Q to_consume -P eventlet  消费数据

# celery.exe flower --broker=amqp://guest:guest@localhost:5672/test

from celery import Celery

celery_app = Celery('handle_data')#include=['handle_data.tasks']

#从celery_config.py中导入
celery_app.config_from_object('handle_data.celery_config')

if __name__ == '__main__':
    celery_app.start()