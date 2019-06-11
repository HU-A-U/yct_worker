# -*- coding:utf-8 -*-
import rpyc
from handle_data.celery_config import rpyc_host,rpyc_port

class rpycSer():
    '''
    自定义vnc连接的上下文管理器
    '''
    def __init__(self):
        self.host = rpyc_host
        self.port = rpyc_port

    def __enter__(self):
        '''
        建立rpyc连接
        :return:返回连接对象
        '''
        self.conn = rpyc.connect(self.host, self.port)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        关闭rpyc连接
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        '''
        self.conn.close()