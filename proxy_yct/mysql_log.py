'''直接使用mysql存储数据'''
# -*- coding:utf-8 -*-
import pymysql
import re
import traceback
import os

from logger_logging import get_log
logger = get_log().config_log()
DATABASE_RE = re.compile("'(.*?)'", re.DOTALL)
class Mysql_log():
    def __init__(self,database,datatable):
        '''自定义数据库,自定义数据表'''
        from data_config import Config
        self.yct_task = Config().YCT_TASK
        self.datatable = datatable
        self.database = database
        # self.info=info
        self.login_sqlsever()
    def login_sqlsever(self):
        '''登录sqlsever'''
        try:
            if self.yct_task:
                self.pymysqlinfo = eval(os.environ['YCT_TASK'])
                self.connection = pymysql.connect(host=self.pymysqlinfo['host'], user=self.pymysqlinfo['root'],
                                                  password=self.pymysqlinfo['root'], port=self.pymysqlinfo['port'],
                                                  charset='utf-8', use_unicode=True)
            else:
                self.connection = pymysql.connect(host="localhost", user="root", password="root", charset="utf8",
                                                  use_unicode=True,
                                                  )
            self.inquire = self.connection.cursor()  # 新建查询
            self.inquire.execute('show databases;')  # 查询语句,获得所有数据库
            databases = str(self.inquire.fetchall())  # 执行查询
            if self.database not in DATABASE_RE.findall(databases):
                self.connection.autocommit(True)  # 自动提交事务
                self.inquire.execute('create DATABASE %s' % (self.database))
            self.operator()
            if self.pymysqlinfo:
                self.connection = pymysql.connect(host=self.pymysqlinfo['host'], user=self.pymysqlinfo['root'],
                                                  password=self.pymysqlinfo['root'], charset='utf-8', use_unicode=True,database=self.database,port=self.pymysqlinfo['port'])
            else:
                self.connection = pymysql.connect(host="localhost", user="root", password='root', charset="utf8",use_unicode=True,
                                                  database=self.database)
            self.inquire = self.connection.cursor()
        except pymysql.OperationalError as e:
            logger.error('[SQLSEVER OPERATIONAL ERROR]:%s', traceback.print_exc())
            os._exit(0)
        except pymysql.InterfaceError as e:
            logger.error('[SQLSEVER INTERFACE ERROR]:%s', traceback.print_exc())
            os._exit(0)
        except Exception as e:
            logger.error('[OTHER SQLSEVER ERROR]:%s', traceback.print_exc())
    def insert_data(self,info):
        '''查询在major中查Name，如果有不插入到rank中'''
        '''需要自定义插入数据'''
        try:
            self.inquire.executemany(
                "INSERT INTO {} VALUES (%s,%s,%s)".format(self.datatable[0])
                , [(info['web_name'],
                    info['time_circle'],
                    info['parameter']
                    )])
            self.connection.commit()
            return 'success'
        # except pymysql.err.InterfaceError as e:
        except Exception as e:
            self.connection.rollback()
            logger.error('[OTHER SQLSEVER ERROR]:%s', traceback.print_exc())
    def match_table(self,info):
        '''查找数据'''
        try:
            self.inquire.execute('select parameter from %s where web_name ="%s" AND time_circle="%s";' % (
            self.datatable[0], info['web_name'], info['time_circle']))
            parameter = self.inquire.fetchone()[0]
            return parameter
        except Exception as e:
            raise e
        # print(parameter)
    def create_table(self):
        '''需要手动修改表的字段'''
        try:
            self.inquire.execute('create table %s('
                                 'web_name VARCHAR(20),'
                                 'time_circle VARCHAR (20),'
                                 'parameter MEDIUMTEXT)default charset = utf8;'
                                 %(self.datatable[0]))
        except pymysql.ProgrammingError as e:
            logger.error('[DATABALE PROGRAMMING ERROR]%s', traceback.print_exc())
            os._exit(0)
        self.connection.commit()
        # self.operator()
    def fetch_one_math(self):
        '''提取最后保存的一条数据'''
        try:
            self.inquire.execute('select * from %s order by time_circle desc limit 1;'%(self.datatable[0]))
            parameter=self.inquire.fetchone()
        except Exception as e:
            self.connection.rollback()
            logger.error('[DATABALE FETCH_ONE_MATH ERROR]%s', traceback.print_exc())
            # os._exit(0)
        else:
            return parameter[-1]
    def fetchall_match(self,info):
        '''获取所有符合的数据并去重'''
        self.inquire.execute('select parameter from %s where customer_id ="%s" AND to_server="%s";'%(self.datatable[0],info['customer_id'],info['to_server']))
        parameter=self.inquire.fetchall()
        set_data=[]
        for i in parameter:
            set_data.append(i[0])
        set_data=set(set_data)
    def drop_datatable(self):
        '''删除数据表'''
        for i in self.datatable:
            self.inquire.execute('drop table {}'.format(i))
        self.operator()
    def operator(self):
        '''关闭数据库'''
        # self.connection.commit()
        self.inquire.close()
        self.connection.close()
# with open(file='./store.txt',mode='r') as folder:
#     content=folder.read()
# print(content)
# import time
# time_circle=time.time()
# print(time_circle)
# info={'web_name':'yct','time_circle':1548643122.80251,'parameter':'火影忍者'}




# a=Mysql_log(database='yct_server',datatable=['yct_1_log'])
# a.create_table()
# a.drop_datatable()
# a.match_table(info
# a.match_table()
# x=a.fetch_one_math()
# print(x)
# a.insert_data(info=info)
# a.create_table()
