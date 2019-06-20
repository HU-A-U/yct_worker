# -*- coding:utf-8 -*-
import datetime
from handle_data.celery_config import SURL
from raven import Client
cli = Client('https://6bc40853ade046ebb83077e956be04d2:d862bee828d848b6882ef875baedfe8c@sentry.cicjust.com//5')

import sqlsoup
try:
    db = sqlsoup.SQLSoup(SURL)
except Exception as e:
    cli.captureException()

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
        to_server = infodata.get('to_server')
        methods = infodata.get('methods')
        etpsName = infodata.get('etpsName')
        customer_id = infodata.get('customer_id')
        registerAppNo = infodata.get('registerAppNo')
        if 'yct' not in to_server: #一窗通之外的数据不存库
            return
        if 'http://yct.sh.gov.cn/bizhallnz_yctnew/search' in to_server: #查询数据的不存库
            return

        try:
            if self.table.filter_by(to_server=to_server, methods=methods,registerAppNo=registerAppNo,customer_id=customer_id).count():
                # 已存在的记录直接更新
                self.table.filter_by(to_server=to_server, methods=methods,registerAppNo=registerAppNo,customer_id=customer_id).update(infodata)
                if to_server == 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info':
                    #对于已经存在的公司，每次修改暂存，就整体更新一次公司名称包括股东主要成员信息，同步用户修改后的公司名称
                    upinfo = {'etpsName':etpsName,'isSynchronous':'0'}
                    self.table.filter_by(registerAppNo=registerAppNo).update(upinfo)
                    yctAppNo = infodata.get('yctAppNo')
                    self.table.filter_by(yctAppNo=yctAppNo).update(upinfo)
                db.commit()
                return
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()
            return


        # 不存在就，直接插入一条新纪录
        new_dict.update(infodata)
        try:
            self.table.insert(**new_dict)
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()
            raise e

        if to_server != 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info':
            # 每次更新将apply_form记录的isSynchronous字段，置为0
            URL = 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info'
            try:
                if self.table.filter_by(to_server=URL, pageName='apply_form',registerAppNo=registerAppNo).count():
                    self.table.filter_by(to_server=URL, pageName='apply_form', registerAppNo=registerAppNo).update({'isSynchronous':'0'})
                    db.commit()
            except Exception as e:
                if self._sentry:
                    self._sentry.captureException()
                db.rollback()
                raise e

        if to_server == 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info':
            # 更新股东form或成员form的yctAppNo和etpsName
            try:
                investor_url = 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/save'
                member_url = 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_save_member'
                update_info = {'yctAppNo': new_dict.get('yctAppNo', ''), 'etpsName': new_dict.get('etpsName', '')}
                self.table.filter_by(to_server=investor_url, registerAppNo=registerAppNo, pageName='gdform').update(update_info)
                self.table.filter_by(to_server=member_url, registerAppNo=registerAppNo, pageName='memberform').update(update_info)
                db.commit()
            except Exception as e:
                if self._sentry:
                    self._sentry.captureException()
                db.rollback()
        return


    def del_set(self,infodata):
        '''
        根据customer_id 删除对应的一条记录
        :param customer_id: 股东对应的号码/主要成员对应的号码
        :return:
        '''
        to_server = infodata.get('to_server')
        pageName = infodata.get('pageName')
        registerAppNo = infodata.get('registerAppNo','')
        customer_id = infodata.get('customer_id')
        # 删除指定股东或成员的记录
        try:
            the_set = None
            if 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/delete' in to_server:
                the_set = self.table.filter_by(pageName=pageName,registerAppNo=registerAppNo,customer_id=customer_id).one()
            elif 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_delete_member' in to_server:
                # 删除成员的请求里没有AppNo，根据customer_id进行筛选
                the_set = self.table.filter_by(pageName=pageName,customer_id=customer_id).one()
            db.delete(the_set)
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()

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
