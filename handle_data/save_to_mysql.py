# -*- coding:utf-8 -*-
import datetime
import sqlsoup
from handle_data.celery_config import SURL

db = sqlsoup.SQLSoup(SURL)

from raven import Client
cli = Client('https://6bc40853ade046ebb83077e956be04d2:d862bee828d848b6882ef875baedfe8c@sentry.cicjust.com//5')

class Save_to_sql():

    def __init__(self,table_name,sentry=cli):
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
        to_server = infodata.get('to_server')
        if 'yct' not in to_server: #一窗通之外的数据不存库
            return
        if to_server not in ['http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/save','http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_save_member']:
            web_name = infodata.get('web_name')
            methods = infodata.get('methods')
            registerAppNo = infodata.get('registerAppNo')
            if self.table.filter_by(to_server=to_server, web_name=web_name, methods=methods, registerAppNo=registerAppNo).count():
                # 已存在的记录直接更新
                try:
                    self.table.filter_by(to_server=to_server, web_name=web_name, methods=methods,registerAppNo=registerAppNo).update(infodata)
                    db.commit()
                except Exception as e:
                    if self._sentry:
                        self._sentry.captureException()
                    db.rollback()
                    raise e
                return

        new_dict.update(infodata)
        try:
            self.table.insert(**new_dict)
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()
            raise e
        return


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
