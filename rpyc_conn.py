# -*- coding:utf-8 -*-
import rpyc

class rpycSer():
    '''
    自定义vnc连接的上下文管理器
    '''
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 12233

    def __enter__(self):
        '''
        建立rpyc连接
        :return:返回连接对象
        '''
        self.conn = rpyc.connect(self.host, self.port)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        关闭vnc连接
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        '''
        self.conn.close()


with rpycSer() as cli:
    res = cli.root.get_time(5)
    print('ss',res)
print(cli.root.get_res())