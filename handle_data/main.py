# -*- coding:utf-8 -*-
'''调用celery任务'''

from handle_data.tasks import *

def handle_data(data_str):

    #插入一条pickle后的数据，返回记录的id res1
    res1 = to_product.apply_async(args=[data_str],retry=True,queue='to_product')
    print(res1.get())
    #根据返回的id res1，对数据进行解析，返回解析后的数据res2
    # res2 = to_analysis.apply_async(args=[res1.get()],retry=True,queue='to_analysis')
    # print(res2.get())
    #将解析后的数据res2，插入数据库
    # res3 = to_consume.apply_async(args=[res2.get()],retry=True,queue='to_consume')
    # print(res3.get())



if __name__ == '__main__':
    data_bag = {'request':'request1111','response':'ok'}
    handle_data(data_bag)