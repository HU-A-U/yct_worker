# -*- coding:utf-8 -*-
'''创建任务'''
import datetime
import json
import random
import pickle
import time
from handle_data import celery_app
from urllib.parse import urlencode

from handle_data.celery_config import REDIS_HOST,REDIS_PORT
from handle_data.save_to_mysql import Save_to_sql
import redis

#建立redis连接池
redis_pool = redis.ConnectionPool(host=REDIS_HOST,port=REDIS_PORT)
r = redis.Redis(connection_pool=redis_pool)

@celery_app.task(name='to_product')
def to_product(data_str):
    '''生产数据'''
    if not data_str:
        return
    # 将原始pickled的数据存入reids中
    #随机生成一个数字，作为name
    name = str(random.random())
    value = data_str
    r.set(name,value,ex=3600)

    # 插入一条记录
    # save_to_product = Save_to_sql('product')
    # product_id = save_to_product.insert_new(data_str)

    #根据返回的id res1，对数据进行解析，返回解析后的数据res2
    to_analysis.apply_async(args=[name], retry=True, queue='to_analysis',immutable=True)


@celery_app.task(name='to_analysis')
def to_analysis(name):
    '''解析数据'''

    # 根据id获取数据进行解析
    # find_product_data = Save_to_sql('product')
    # product_data = find_product_data.find_data(name)

    #从redis中获取值
    data_bytes = r.get(name)
    data_str = data_bytes.decode(encoding='utf-8')
    # 进行数据解析
    analysis_data = Analysis_data(data_str,name)

    if not analysis_data:
        return

    # #将解析后的数据res2，插入数据库
    to_consume.apply_async(args=[analysis_data], retry=True, queue='to_consume')


@celery_app.task(name='to_consume')
def to_consume(data):
    '''消费数据'''
    # 将解析完的数据进行存库
    save_to_analysis = Save_to_sql('analysis')
    if data:
        save_to_analysis.insert_new(data)

    return data

def Analysis_data(data_str,name):
    #数据解析
    # pickled_data = data_str.pickled_data
    data_dict = pickle.loads(eval(data_str))
    #过滤 js,css,png,gif,jpg 的数据
    for end_name in ['.js','.css','.png','.jpg','.gif']:
        if end_name in data_dict.get('to_server'):
            return

    request = data_dict.get('request')
    parameters_dict = {}
    try:
        form = request.urlencoded_form
        if form :
            for item in form.items():
                parameters_dict[item[0]] = item[1]
        else:
            return
    except Exception as e:
        parameters_dict = {}

    parameters = json.dumps(parameters_dict)
    analysis_data = {
        'product_id':name,
        'methods':request.method,
        'web_name':data_dict.get('web_name'),
        'to_server':data_dict.get('to_server'),
        'time_circle':data_dict.get('time_circle'),
        'customer_id':data_dict.get('customer_id'),
        'parameters':parameters,
        'anync':'', #todo:同步异步请求
    }

    return analysis_data

if __name__ == '__main__':
    # res = to_product.apply_async(args=(1, 2), routing_key='product')
    # print(res.status)
    to_analysis('0.6844667690124796')

    # res = to_product('{"a":"qwe"}')
    # print(res.get())
