# -*- coding:utf-8 -*-
import typing
import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
import pickle
import time
from handle_data.main import handle_data

#建立redis连接池
import redis
from handle_data.celery_config import REDIS_HOST,REDIS_PORT
redis_pool = redis.ConnectionPool(host=REDIS_HOST,port=REDIS_PORT)
r = redis.Redis(connection_pool=redis_pool)

filter_info={'http_connect':['sh.gov.cn']}
class classification_deal:
    '''定义一个基类通过配置处理消息'''
    def filter_deal(self,flow):
        pass
    def other_dealdatabag(self,flow):
        pass
    def yct_dealdatabag(self,flow):
        pass
    def run_celery(self,data):
        pass


class Proxy(classification_deal):
    # HTTP lifecycle
    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        """
            An HTTP CONNECT request was received. Setting a non 2xx response on
            the flow will return the response to the client abort the
            connection. CONNECT requests and responses do not generate the usual
            HTTP handler events. CONNECT requests are only valid in regular and
            upstream proxy modes.
        """
    def requestheaders(self, flow: mitmproxy.http.HTTPFlow):
        """
            HTTP request headers were successfully read. At this point, the body
            is empty.
        """
        '''读取请求头内容'''

    def request(self, flow: mitmproxy.http.HTTPFlow):
        """
            The full HTTP request has been read.
        """
        # request_header=eval(dict(flow.request.headers)['request_header'])
        '''获取请求详细信息'''
        rel_addr = flow.client_conn.address[0].split(':')[-1]
        acc_addr = r.get(rel_addr).decode(encoding='utf-8') if isinstance(r.get(rel_addr),bytes) else r.get(rel_addr)
        if acc_addr != 'pass':
            flow.response = mitmproxy.http.HTTPResponse.make(404)

    def responseheaders(self, flow: mitmproxy.http.HTTPFlow):
        """
            HTTP response headers were successfully read. At this point, the body
            is empty.
        """
        '''读取响应头内容'''

    def response(self, flow: mitmproxy.http.HTTPFlow):
        """
            The full HTTP response has been read.
        """
        # response_header = eval(dict(flow.response.headers)['response_header'])
        # # '''解码图片'''
        # # if flow.response.headers['Content-Type'].startswith('image/'):
        # #     with open(r'C:\Users\xh\proxy_yct\csdn-kf.png', 'wb') as f:
        # #         f.write(flow.response.content)
        # connect = filter_info['http_connect']
        # data_dict = {}
        # for i in connect:
        #    if i in flow.request.host:
        #        data_dict = self.yct_dealdatabag(flow)
        #        break
        #    else:
        data_dict = self.other_dealdatabag(flow)
        #        break
        pickled = pickle.dumps(data_dict)
        data_str = str(pickled)
        self.run_celery(data_str)

    def other_dealdatabag(self,flow):
        data_bag = {}
        # data_bag['client_address'] = flow.client_conn.address
        data_bag['request'] = flow.request
        data_bag['time_circle'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data_bag['web_name'] = flow.request.host
        # data_bag['refer']=flow.request.headers.get('Referer','')
        data_bag['to_server'] = flow.request.url
        data_bag['response'] = flow.response
        return data_bag

    def yct_dealdatabag(self,flow):
        data_bag = {}
        # data_bag['client_address'] = flow.client_conn.address
        data_bag['request'] = flow.request
        data_bag['time_circle'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data_bag['web_name'] = 'yct'
        # data_bag['refer']=flow.request.headers.get('Referer','')
        data_bag['to_server'] = flow.request.url
        data_bag['response'] = flow.response
        return data_bag


    def run_celery(self,data_str):
        #这个地方调用任务to_product
        handle_data(data_str)
        # folder=open(r'D:\data_bag_pickle\{}.pkl'.format(time.time()),mode='wb')
        # pickle.dump(data_bag,folder)
        # folder.close()

        # print(res)


    def error(self, flow: mitmproxy.http.HTTPFlow):
        """
            An HTTP error has occurred, e.g. invalid server responses, or
            interrupted connections. This is distinct from a valid server HTTP
            error response, which is simply a response with an HTTP error code.
        """

    # TCP lifecycle
    def tcp_start(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP connection has started.
        """

    def tcp_message(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP connection has received a message. The most recent message
            will be flow.messages[-1]. The message is user-modifiable.
        """

    def tcp_error(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP error has occurred.
        """

    def tcp_end(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP connection has ended.
        """

    # Websocket lifecycle
    def websocket_handshake(self, flow: mitmproxy.http.HTTPFlow):
        """
            Called when a client wants to establish a WebSocket connection. The
            WebSocket-specific headers can be manipulated to alter the
            handshake. The flow object is guaranteed to have a non-None request
            attribute.
        """

    def websocket_start(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has commenced.
        """

    def websocket_message(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            Called when a WebSocket message is received from the client or
            server. The most recent message will be flow.messages[-1]. The
            message is user-modifiable. Currently there are two types of
            messages, corresponding to the BINARY and TEXT frame types.
        """

    def websocket_error(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has had an error.
        """

    def websocket_end(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has ended.
        """

    # Network lifecycle
    def clientconnect(self, layer: mitmproxy.proxy.protocol.Layer):
        """
            A client has connected to mitmproxy. Note that a connection can
            correspond to multiple HTTP requests.
        """

    def clientdisconnect(self, layer: mitmproxy.proxy.protocol.Layer):
        """
            A client has disconnected from mitmproxy.
        """

    def serverconnect(self, conn: mitmproxy.connections.ServerConnection):
        """
            Mitmproxy has connected to a server. Note that a connection can
            correspond to multiple requests.
        """

    def serverdisconnect(self, conn: mitmproxy.connections.ServerConnection):
        """
            Mitmproxy has disconnected from a server.
        """

    def next_layer(self, layer: mitmproxy.proxy.protocol.Layer):
        """
            Network layers are being switched. You may change which layer will
            be used by returning a new layer object from this event.
        """

    # General lifecycle
    def configure(self, updated: typing.Set[str]):
        """
            Called when configuration changes. The updated argument is a
            set-like object containing the keys of all changed options. This
            event is called during startup with all options in the updated set.
        """

    def done(self):
        """
            Called when the addon shuts down, either by being removed from
            the mitmproxy instance, or when mitmproxy itself shuts down. On
            shutdown, this event is called after the event loop is
            terminated, guaranteeing that it will be the final event an addon
            sees. Note that log handlers are shut down at this point, so
            calls to log functions will produce no output.
        """

    def load(self, entry: mitmproxy.addonmanager.Loader):
        """
            Called when an addon is first loaded. This event receives a Loader
            object, which contains methods for adding options and commands. This
            method is where the addon configures itself.
        """

    def log(self, entry: mitmproxy.log.LogEntry):
        """
            Called whenever a new log entry is created through the mitmproxy
            context. Be careful not to log from this event, which will cause an
            infinite loop!
        """

    def running(self):
        """
            Called when the proxy is completely up and running. At this point,
            you can expect the proxy to be bound to a port, and all addons to be
            loaded.
        """

    def update(self, flows: typing.Sequence[mitmproxy.flow.Flow]):
        """
            Update is called when one or more flow objects have been modified,
            usually from a different addon.
        """
