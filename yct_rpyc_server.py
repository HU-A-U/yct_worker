#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import time
from rpyc import Service
from rpyc.utils.server import ThreadedServer
from save_to_sql import Save_to_sql
# from raven import Client
# cli = Client('https://6bc40853ade046ebb83077e956be04d2:d862bee828d848b6882ef875baedfe8c@sentry.cicjust.com//5')

class SaveService(Service):
    # 对于服务端来说， 只有以"exposed_"打头的方法才能被客户端调用，所以要提供给客户端的方法都得加"exposed_"
    def exposed_save_sql(self,data_str):
      #将数据保存到数据库
        try:
            # save_to_analysis = Save_to_sql('yctformdata')
            print(type(data_str))
            if data_str:
                print(data_str)
                infodata = json.loads(data_str)
                is_del = infodata.pop('delete_set')
                print(is_del)
                if is_del: #判断是否删除记录
                    # save_to_analysis.del_set(infodata)
                    pass
                else:
                    # save_to_analysis.insert_new(infodata)
                    pass
                return data_str
            else:
                return json.dumps({'msg':'nodata'})
        except Exception as e:
            # cli.captureException()
            print(e)
            # return e

s=ThreadedServer(service=SaveService,port=12233,auto_register=False,protocol_config={'allow_pickle':True})
s.start()