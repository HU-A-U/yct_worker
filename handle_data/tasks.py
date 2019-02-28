# -*- coding:utf-8 -*-
'''创建任务'''
import datetime
import json
import pickle
import time
from handle_data import celery_app
from urllib.parse import urlencode
from handle_data.save_to_mysql import Save_to_sql
from celery import group


@celery_app.task(name='to_product')
def to_product(data_str):
    '''生产数据'''
    # 将原始数据进行pickle
    # res = pickle.dumps(json.loads(data_bag))
    # print(res)
    # 插入一条记录
    save_to_product = Save_to_sql('product')
    product_id = save_to_product.insert_new(data_str)

    return product_id


@celery_app.task(name='to_analysis')
def to_analysis(product_id):
    '''解析数据'''

    # 根据id获取数据进行解析
    find_product_data = Save_to_sql('product')
    product_data = find_product_data.find_data(product_id)

    # 进行数据解析
    analysis_data = Analysis_data(product_data,product_id)


    return analysis_data

@celery_app.task(name='to_consume')
def to_consume(data):
    '''消费数据'''

    # 将解析完的数据进行存库
    save_to_analysis = Save_to_sql('analysis')
    if data:
        save_to_analysis.insert_new(data)

    return 'ok'

def Analysis_data(data,product_id):
    #数据解析
    pickled_data = data.pickled_data
    data_dict = pickle.loads(eval(pickled_data))
    #忽略 js,css,png,gif,jpg 的数据
    for end_name in ['.js','.css','.png','.jpg','.gif']:
        if end_name in data_dict.get('to_server'):
            return {}

    request = data_dict.get('request')
    response = data_dict.get('response')
    try:
        form = request.urlencoded_form
        parameters = urlencode(form)
    except Exception as e:
        parameters = ''

    analysis_data = {
        'product_id':product_id,
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
    to_analysis(940)
