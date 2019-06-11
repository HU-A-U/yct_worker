#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
from rpyc import Service
from rpyc.utils.server import ThreadedServer
from save_to_sql import Save_to_sql
from raven import Client
cli = Client('https://6bc40853ade046ebb83077e956be04d2:d862bee828d848b6882ef875baedfe8c@sentry.cicjust.com//5')

class SaveService(Service):
    # 对于服务端来说， 只有以"exposed_"打头的方法才能被客户端调用，所以要提供给客户端的方法都得加"exposed_"
    def exposed_save_sql(self,infodata):
      #将数据保存到数据库
        try:
            save_to_analysis = Save_to_sql('yctformdata')
            if infodata:
                is_del = infodata.pop('delete_set')
                if is_del: #判断是否删除记录
                    save_to_analysis.del_set(infodata)
                else:
                    save_to_analysis.insert_new(infodata)
                return infodata
            else:
                return 'nodata'
        except Exception as e:
            cli.captureException()

s=ThreadedServer(service=SaveService,port=12233,auto_register=False)
s.start()