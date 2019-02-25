# -*- coding:utf-8 -*-
import pymysql
import re
import traceback
import os
# import gc
class Mysql():
    def __init__(self,database,datatable):
        '''自定义数据库,自定义数据表'''
        from logger_logging import get_log
        from data_config import Config
        self.yct_task = Config().YCT_TASK
        self.logger = get_log().config_log()
        self.datatable = datatable
        self.database = database
        self.login_sqlsever()
    def login_sqlsever(self):
        '''登录sqlsever'''
        try:
            if self.yct_task:
                self.pymysqlinfo=eval(os.environ['YCT_TASK'])
                self.connection=pymysql.connect(host=self.pymysqlinfo['host'],user=self.pymysqlinfo['root'],password=self.pymysqlinfo['root'],port=self.pymysqlinfo['port'],charset='utf-8',use_unicode=True)
            else:
                self.connection = pymysql.connect(host="localhost", user="root", password="root", charset="utf8",use_unicode=True,
                        )
            self.inquire = self.connection.cursor()  # 新建查询
            self.inquire.execute('show databases;')  # 查询语句,获得所有数据库
            databases = str(self.inquire.fetchall())  # 执行查询
            DATABASE_RE = re.compile("'(.*?)'", re.DOTALL)
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
            self.logger.error('[SQLSEVER OPERATIONAL ERROR]:%s', traceback.print_exc())
            os._exit(0)
        except pymysql.InterfaceError as e:
            self.logger.error('[SQLSEVER INTERFACE ERROR]:%s', traceback.print_exc())
            os._exit(0)
        except Exception as e:
            self.logger.error('[OTHER SQLSEVER ERROR]:%s', traceback.print_exc())
    def insert_data(self,info):
        '''查询在major中查Name，如果有不插入到rank中'''
        '''需要自定义插入数据'''
        try:
            self.inquire.executemany(
                "INSERT INTO {} VALUES (%s,%s,%s,%s,%s,%s,%s,%s)".format(self.datatable[0])
                , [(info['web_name'],
                    info['time_circle'],
                    info['to_server'],
                    info['customer_id'],
                    info['async'],
                    info['type'],
                    info['method'],
                    info['parameter']
                    )])
            self.connection.commit()
            return 'success'
        except Exception as e:
            self.logger.error('[OTHER SQLSEVER ERROR]:%s', traceback.print_exc())
    def inquire_data(self,info):
        '''根据customer_id,to_url找到参数，如果参数是一致的不覆盖，否则覆盖这一条记录'''
        self.inquire.execute('select parameter from %s where customer_id ="%s" AND to_server="%s";'%(self.datatable[0],info['customer_id'],info['to_server']))
        parameter=self.inquire.fetchone()
        if not parameter:
            # gc.collect()
            return self.insert_data(info)
        if parameter[0] in info['parameter']:
            return 'success'
        else:
            if 'yct' in info['web_name']:
                not_over=self.yct_task['not_over']
                if info['to_server'] in not_over:
                    return self.insert_data(info)
            # gc.collect()
            return self.over_data(info)
    def over_data(self,info):
        '''覆盖记录'''
        try:
            info['parameter']=pymysql.escape_string(info['parameter'])  #对语句做转义
            self.inquire.execute('UPDATE %s SET parameter="%s",time_circle="%s" where customer_id ="%s" AND to_server ="%s"'%(
                self.datatable[0],info['parameter'],info['time_circle'],info['customer_id'],info['to_server']
            ))
            self.connection.commit()
            return 'success'
        except Exception as e:
            self.logger.error('[OVER_DATA SQLSEVER ERROR]:%s', traceback.print_exc())
            os._exit(0)
    def fetch_one_math(self):
        '''提取最有保存的一条数据'''
        try:
            self.inquire.execute('select * from %s order by time_circle desc limit 1;'%(self.datatable[0]))
            parameter=self.inquire.fetchone()
        except Exception as e:
            self.logger.error('[DATABALE FETCH_ONE_MATH ERROR]%s', traceback.print_exc())
            os._exit(0)
        else:
            return parameter[-1]
    def create_table(self):
        '''需要手动修改表的字段'''
        try:
            self.inquire.execute('create table %s('
                                 'web_name VARCHAR(20),'
                                 'time_circle VARCHAR (20),'
                                 'to_server VARCHAR(200),'
                                 'customer_id VARCHAR(20),'
                                 'async VARCHAR(10),'
                                 'type VARCHAR(10),'
                                 'method VARCHAR(10),'
                                 'parameter VARCHAR(5000))default charset = utf8;'
                                 %(self.datatable[0]))
        except pymysql.ProgrammingError as e:
            self.logger.error('[DATABALE PROGRAMMING ERROR]%s', traceback.print_exc())
            os._exit(0)
        self.connection.commit()
        # self.operator()
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

# axx = {'time_circle': '2019-01-27 11:28:56', 'web_name': 'yct', 'to_server': '/bizhallnz_yctnew/apply/save_info',
#          'customer_id': '', 'async': 'true', 'type': 'POST', 'method': 'form',
#          'parameter': str({'etpsApp.applyOrgan': '000000', 'nameId': '', 'nameAppNo': '',
#                        'registerAppNo': '0000000120190114A002', 'yctAppNo': 'faf2f26dfe7a4a40aa2e5bc42c7b8858',
#                        'loginStatus': 'LOGIN_STATUS_PORTAL_OTHER', 'useAnotherNameId': '', 'subObjId': '10',
#                        'etpsApp.etpsName': '天使是谁',
#                        'webStatusId': '5492221383442709386627214441065234298887132610371719067248708002023593308458064899711454069748000325585347675886133004123417555509097045758973964499928458748878635909688810057848913704063974968510121745056356346198127683987831986819069684797213890483036981635214176526748623712522794091796712747919963262',
#                        'etpsInfo.etpsTypeGb': '', 'etpsAppagent.applicantName': '王尧', 'etpsAppagent.telephone': '',
#                        'etpsAppagent.mobilePhone': '13564118478', 'etpsAppagent.cetfTypeGb': '1',
#                        'etpsAppagent.cetfType': '', 'etpsAppagent.cetfId': '310225199510270011',
#                        'etpsAppagent.authorizeFromDate': '', 'etpsAppagent.authorizeToDate': '',
#                        'etpsApp.declarePaper': '11', 'etpsOtherInfo.centralAddrId': '', 'etpsInfo.roomRight': '',
#                        'etpsInfo.areaOrganId': '', 'etpsInfo.areaOrganIdGb': ''
#              , 'etpsOtherInfo.centralOrderNo': '', 'etpsInfo.areaId': '', 'etpsInfo.neighborhoodId': '',
#                        'etpsInfo.roa1': '', 'etpsInfo.lane': '', 'etpsInfo.startNum': '', 'etpsInfo.endNum': '',
#                        'etpsInfo.numProperty': '', 'etpsInfo.unitNum': '', 'etpsInfo.roomNum': '', 'zmqCheckbox': 'vb',
#                        'etpsInfo.isZmq': '0', 'etpsInfo.address': '', 'etpsOtherInfo.immovablePropertyNumber': '',
#                        'etpsInfo.postcode': '', 'etpsInfo.telephone': '', 'etpsInfo.mailAddr': '',
#                        'etpsInfo.isTrdtimeLimit': '1', 'etpsInfo.tradeYears': '', 'etpsTrdInfo.trdScope': '',
#                        'VerificationTrdScopeLength': '', 'otherScopeVo.needOtherScope': 'false',
#                        'otherScopeVo.ifMajor': '', 'otherScopeVo.scopeContent': '', 'isNeedMainScope': 'no',
#                        'etpsLicenceList[0].licenceId': '-6243493', 'etpsLicenceList[0].licenceTypeId': '01',
#                        'etpsLicenceList[0].licenceNumb': '1', 'etpsLicenceList[1].licenceId': '-6243492',
#                        'etpsLicenceList[1].licenceTypeId': '07', 'etpsLicenceList[1].limitMemo': 'FB',
#                        'etpsLicenceList[1].licenceNumb': '1', 'etpsInvtNum.empNum': '', 'etpsCptl.cptlTotal': '',
#                        'VerificationInvestornumber': '', 'validInvtActl': '', 'validIsNeedModify': '',
#                        'validInvestmentSituation': '', 'investorProportion': '[]', 'isCptlTotalMatch': '',
#                        'investorList': '', 'chiefMember.id': '-726621', 'chiefMember.memberType': '0',
#                        'chiefMember.legalSign': '1', 'chiefMember.personName': '', 'chiefMember.email': '',
#                        'chiefMember.mobile': '', 'chiefMember.telephone': '', 'chiefMember.cetfTypeGb': '',
#                        'chiefMember.cetfType': '', 'chiefMember.cetfId': '', 'chiefMember.sexId': '',
#                        'chiefMember.birthdate': '', 'chiefMember.nationalityId': '', 'chiefMember.provinceId': '',
#                        'chiefProvId': '',
#                        'chiefCityId': '', 'chiefDistrictId': '', 'chiefMember.nationId': '', 'chiefMember.hdshGb': '',
#                        'chiefMember.hdshId': '', 'chiefHdshGb': '', 'etpsOtherInfo.dshMemberQty': '',
#                        'etpsOtherInfo.jshMemberQty': '', 'etpsOtherInfo.zhigongJsQty': '', 'validDS': '', 'validJS': '',
#                        'validJSZW': '', 'etpsContact.persnName': '', 'etpsContact.telephone': '',
#                        'etpsContact.certType': '', 'etpsContact.certNo': '', 'etpsContact.mobile': '',
#                        'etpsContact.mail': '', 'etpsOtherInfo.finanName': '', 'etpsOtherInfo.finanTelephone': '',
#                        'etpsOtherInfo.finanCerfType': '', 'etpsOtherInfo.finanCertNo': '',
#                        'etpsOtherInfo.finanMobile': '', 'etpsOtherInfo.finanEmail': ''})}

if __name__=="__main__":
    a=Mysql(database='yct_server',datatable=['yct_1'])
    # a.create_table()
    z=a.fetch_one_math()
    print(z)
    # a.fetchall_match(info={'customer_id':'','to_server':'/bizhallnz_yctnew/apply/member/ajax_save_member'})
# a.drop_datatable()
# a.create_table()


