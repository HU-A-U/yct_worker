# -*- coding:utf-8 -*-
'''创建任务'''

import time

from handle_data import celery_app
from save_to_mysql import Save_to_sql
from celery import group

@celery_app.task(name='to_product')
def to_product(x,y):
    '''生产数据'''
    time_circle=time.time()
    info={'web_name':'yct','time_circle':time_circle,'parameter':str(data)}
    mysql_log = Save_to_sql(site='yct_server', datatable=['yct_1_log'])
    mysql_log.insert_new(info=info)
    r = x+y
    print('a计算结果%s'%str(r))

    return x+y

@celery_app.task(name='to_consume')
def to_consume(x,y):
    '''消费数据'''
    r = x-y
    print('b计算结果%s'%str(r))

    return x-y

@celery_app.task(name='to_analysis')
def to_analysis(x,y):
    '''解析数据'''
    r = x * y * 2
    print('c计算结果%s' % str(r))

    return x * y * 2


if __name__ == '__main__':
    res = to_product.apply_async(args=(1, 2),routing_key='product')
    print(res.status)