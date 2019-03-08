# -*- coding:utf-8 -*-
import datetime
import sqlsoup
from handle_data.celery_config import SURL

db = sqlsoup.SQLSoup(SURL)

class Save_to_sql():

    def __init__(self,table_name,sentry=None):
        '''table_name(product 和 analysis)'''

        #表名称
        self.table_name = table_name

        self._sentry = sentry

        #连接对应的表
        self.table = db.entity(table_name)


    #插入一条新的原始记录
    def insert_new(self,infodata):

        #根据表名，拼接参数进行存库
        new_dict = {}
        the_set = None
        if self.table_name == 'product':
            if type(infodata) != str:
                infodata = str(infodata)
            new_set = {
                'pickled_data': infodata,
            }
            # the_set = self.table.insert(**new_set)
        elif self.table_name == 'yctformdata':
            to_server = infodata.get('to_server')
            web_name = infodata.get('web_name')
            methods = infodata.get('methods')
            registerAppNo = infodata.get('registerAppNo')
            if self.table.filter_by(to_server=to_server, web_name=web_name, methods=methods, registerAppNo=registerAppNo).count():
                the_set = self.table.filter_by(to_server=to_server, web_name=web_name, methods=methods,registerAppNo=registerAppNo).one()
                #删除原有的记录，插入一条新的记录
                db.delete(the_set)

                # the_set.parameters = infodata.get('parameters')
                # the_set.product_id = infodata.get('product_id')
                # the_set.time_circle = infodata.get('time_circle')
            # else:
            new_dict.update(infodata)
        try:
            the_set = self.table.insert(**new_dict)
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()

        return the_set.id


    def find_data(self,product_id):
        product_data = self.table.filter_by(id=product_id).one()
        return product_data



if __name__ == '__main__':
    sql = Save_to_sql('analysis')

    datainfo = {'product_id': '0.47646533351534726',
                'methods': 'POST',
                'web_name': 'yct',
                'to_server': 'http://yct.sh.gov.cn/yct_other/tax/saveInputTax4',
                'time_circle': '2019-03-05 13:13:13',
                'customer_id':'',
                'parameters': '{"step": "5", "yctAppNo": "d57ddd3ade3a414a844db854ca9dcdc3", "checkbox_lpr": "on", "wbjhYctFplyrxxList[0].yctAppNo": "d57ddd3ade3a414a844db854ca9dcdc3", "wbjhYctFplyrxxList[0].lprlx": "3", "lprxm0": "3", "wbjhYctFplyrxxList[0].lprxm": "\u738b\u521a", "wbjhYctFplyrxxList[0].lprzjzl": "201", "wbjhYctFplyrxxList[0].lprzjhm": "310114199003078514", "wbjhYctFplyrxxList[0].lprlxdh": "17719784267", "checkbox_fpzl": "on", "wbjhYctFphdsqxxList[0].yctAppNo": "d57ddd3ade3a414a844db854ca9dcdc3", "wbjhYctFphdsqxxList[0].fpzlDm": "131005151060", "sjfwsdm": "", "ptfpzgxeje": "", "zyfpzgxeje": "", "defpljje": "20"}',
                'anync': ''}

    sql.insert_new(datainfo)
