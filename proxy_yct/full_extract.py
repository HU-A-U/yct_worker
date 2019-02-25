# -*- coding:utf-8 -*-
import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
# import hashlib
'''这里会根据给定的账号，然后通过捕捉时间和捕捉url每次从数据库中去覆盖。'''
# true=''
path='D:\data_bag_pickle'
class Extract():
    def __init__(self):
        from data_config import Config
        self.YCT_TASK=Config.YCT_TASK
    def xpath_request(self,res):
        '''解请求包'''
        key_res=self.catch_url(res)
        if not key_res:
            return None
        elif 'success_png' in key_res:
            return key_res
        else:
            return self.parse_reqsponse(key_res)
    def catch_url(self,res):
        '''捕捉指定的url'''
        web_name=res['web_name']
        if web_name=='yct':
            catch_url=self.YCT_TASK['catch_url']
            catch_pic=self.YCT_TASK['catch_pic']
            print('我是to_server',res['to_server'],'\n\n')
            if catch_pic in res['to_server']:
                customer_id_jpg = 'yzm_yct'
                pic_path = r'D:\data_pic\{}.png'.format(customer_id_jpg)
                try:
                    with open(pic_path, 'wb') as f:
                        f.write(res['response'].content)
                        f.close()
                except Exception as e:
                    import os
                    os._exit(0)
                return 'success_png:{}'.format(pic_path)
            for catch in catch_url:
                if catch in res['to_server']:
                    res['to_server']=catch        #<----转化成md5值
                    return res
    # def md5_x(self,catch):
    #     '''MD5值处理'''
    #     m2 = hashlib.md5()
    #     m2.update(catch.encode("utf-8"))
    #     return m2.hexdigest()
    def parse_reqsponse(self,key_res):
    #     '''根据请求的实体获取正确的响应内容'''
        content=''
        response=key_res['response']
        headers=dict(response.headers)
        state_code=response.status_code
        if '404' in str(state_code):
            return None
        if headers.get('Content-Length',''):
            content_length=int(headers['Content-Length'])
            if not content_length:
                return None
        elif not headers.get('Content-Type',''):
            return None
        content_type=headers['Content-Type']
        if content_type.startswith('application/json'):
            content=response.text
        elif content_type.startswith('text/html'):
            content=response.text
        elif content_type.startswith('text/plain;charset=UTF-8'):
            content=response.text
        # elif content_type.startswith('image/'):
        #     content=str(response.content)
        elif content_type.startswith('text/javascript'):
            return None
        elif content_type.startswith('text/css'):
            return None
        else:
            print(content_type,'错了')
        # self.res['content']=content
        # self.res['content_type']=content_type
        return  self.parse_request(key_res)
    def parse_request(self,key_res):
        '''根据请求头获取相关数据
        #method:表单
        #type:post
        #async:true
        #content_type:jpeg
        '''

        '''
        根据请求头获取相关数据的accept_encoding
        '''
        key_res['async']='false'
        request=key_res['request']
        key_res['type']=request.method
        headers=dict(request.headers)
        if not headers.get('Content-Type',''):
            return None
        if headers.get('X-Requested-With',''):
            key_res['async']='true'
        if 'application/x-www-form-urlencoded' in headers.get('Content-Type',''):
            key_res['method']='form'
            key_res['parameter']=str(dict(key_res['request'].urlencoded_form))
        elif 'application/json' in headers.get('Content-Type',''):
            key_res['method']='json'
            key_res['parameter']=key_res['request'].get_text()
        # else:
        #     key_res['method']='text'
        #     key_res['parameter']=key_res['request'].get_text()
            # print(headers.get('Content-Type',''))
            # import os
            # os._exit(0)
        key_res.pop('request','')
        key_res.pop('response','')
        return key_res