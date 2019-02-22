# -*- coding:utf-8 -*-
'''调用celery任务'''

from handle_data.tasks import *

#插入一条pickle后的数据，返回记录的id
res1 = to_product.apply_async(args=(2,3),retry=True,queue='to_product')
#根据返回的id，对数据进行解析，返回解析后的数据
res2 = to_consume.apply_async(args=(res1.get(),4),retry=True,queue='to_consume')
#将解析后的数据，插入数据库
res3 = to_analysis.apply_async(args=(res2.get(),7),retry=True,queue='to_analysis')


print(res1.get())
print(res2.get())
print(res3.get())
