import pickle
from full_extract import Extract
from mysql_log import Mysql_log
from mysql_data import Mysql
extract=Extract()
mysql = Mysql(database='yct_server', datatable=['yct_1'])
def my_customer():
    '''消费数据'''
    # while 1:
    mysql_log = Mysql_log(database='yct_server', datatable=['yct_1_log'])
    key_word=mysql_log.fetch_one_math()
    data_packet=pickle.loads(eval(key_word))
    important_info = extract.xpath_request(data_packet)
    if not important_info:
        pass
        # continue
    elif  'success_png' in important_info:
        pass
        # continue
        # return 'success_png'
    else:
        # print(important_info)
        mysql.inquire_data(info=important_info)
my_customer()
