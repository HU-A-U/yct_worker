# -*- coding:utf-8 -*-

import datetime
import sqlsoup

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
# SURL = "mysql+pymysql://cic_admin:159357a@{}:{}/cic_splinter?charset=utf8&autocommit=true".format(MYSQL_HOST, MYSQL_PORT)
SURL = "mysql+pymysql://root:mysql@{}:{}/proxy?charset=utf8&autocommit=true".format(MYSQL_HOST, MYSQL_PORT)
db = sqlsoup.SQLSoup(SURL)

class Save_to_sql():

    def __init__(self,db_name,sentry=None):
        '''db_name(product 和 analysis)'''

        #表名称
        self.db_name = db_name

        self._sentry = sentry

        #连接对应的表
        self.table = db.entity(db_name)


    #插入一条新的记录
    def insert_new(self,infodata):
        # create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        #根据表名，拼接参数进行存库
        new_set = {}
        if self.db_name == 'product':
            if type(infodata) != str:
                infodata = str(infodata)

            new_set = {
                'pickled_data': infodata,
                # 'create_time': create_time,
            }
        elif self.db_name == 'analysis':
            new_set.update(infodata)
            # new_set['create_time'] = create_time
        try:
            the_set = self.table.insert(**new_set)
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()

        return the_set.id

    def find_data(self,id):
        product_data = self.table.filter_by(id=id).one()
        return product_data

    #插入一条账套信息
    def init_zt(self,ztname,finished_time='',status=''):
        start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 不重复插入字段名称
        if self.zt_table.filter_by(ztname=ztname, site=self.site).count():
            zt = self.zt_table.filter_by(ztname=ztname, site=self.site).one()
            zt.finished_time = finished_time
            zt.start_time = start_time
            zt.status = status
        else:
            new_set = {
                'ztname':ztname,
                'site':self.site,
                'start_time':start_time,
                'finished_time':finished_time,
                'status':status
            }
            # 定义字段的名称
            zt = self.zt_table.insert(**new_set)
            try:
                db.commit()
            except Exception as e:
                if self._sentry:
                    self._sentry.captureException()
                db.rollback()

        return zt


    def update_zt_status(self,zt,msg):
        '''更新账套'''
        zt.status = str(msg)

        try:
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()


    def update_zt_finised_time(self,zt):

        finished_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        zt.finished_time = str(finished_time)

        try:
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()


    def init_infoname(self,info_name):

        #不重复插入字段名称
        if self.infoname_table.filter_by(infoname=info_name,site=self.site).count():
            infoname = self.infoname_table.filter_by(infoname=info_name, site=self.site).one()
        else:
            # 定义字段的名称
            infoname = self.infoname_table.insert(infoname=info_name,site=self.site)
            try:
                db.commit()
            except Exception as e:
                if self._sentry:
                    self._sentry.captureException()
                db.rollback()

        return infoname

    def find_zt(self,ztList):
        pass


if __name__ == '__main__':
    sql = Save_to_sql('kungeek', '12345678')
    sql.init_zt('我的公司',status='start')
