# -*- coding:utf-8 -*-
'''celery配置'''
'''启动命令'''
# celery -A handle_data worker -l info -Q to_product  -P eventlet 生产数据

# celery -A handle_data worker -l info -Q to_analysis -P eventlet 解析数据

# celery -A handle_data worker -l info -Q to_consume -P eventlet  消费数据

# mitmdump -s start_script.py

# celery flower --broker=amqp://guest:guest@localhost:5672/test 开启flower后台监控
# celery flower --broker=amqp://cic_admin:JYcxys@3030@192.168.1.152:5672/yct
# celery flower --broker=amqp://cic_admin:JYcxys@3030@47.102.218.137:5672/yct

from raven import Client

cli = Client('https://6bc40853ade046ebb83077e956be04d2:d862bee828d848b6882ef875baedfe8c@sentry.cicjust.com//5')


rpyc_host = '127.0.0.1'
# rpyc_host = '116.228.76.162'
rpyc_port = 12233

SURL = "mysql+pymysql://cic_admin:TaBoq,,1234@192.168.1.170:3306/yct_proxy?charset=utf8&autocommit=true"
# SURL = "mysql+pymysql://cic_admin:159357a@192.168.10.11:3306/yct_proxy?charset=utf8&autocommit=true"
# SURL = "mysql+pymysql://root:GHys1234&,><@!@192.168.10.246:3306/yct_proxy?charset=utf8&autocommit=true"

# REDIS_HOST = 'aliyun_redis'
# REDIS_PORT = 6379

REDIS_HOST = '192.168.20.245'
REDIS_PORT = 16379


# RABBITMQ_HOST = '172.19.79.104'
# RABBITMQ_HOST = '127.0.0.1'
RABBITMQ_HOST = '47.102.218.137'
RABBITMQ_PORT = 5672


# 注意，celery4版本后，CELERY_BROKER_URL改为BROKER_URL
from kombu import Queue, Exchange

BROKER_URL = 'amqp://cic_admin:JYcxys@3030@{}:{}/yct'.format(RABBITMQ_HOST,RABBITMQ_PORT)
# BROKER_URL = 'amqp://cic_admin:JYcxys@3030@{}:{}/newprocy-yuanqu01'.format(RABBITMQ_HOST,RABBITMQ_PORT)
# BROKER_URL = 'amqp://test:test@127.0.0.1:5672/test'
# 指定结果的接受地址
CELERY_RESULT_BACKEND = 'redis://{}:{}/15'.format(REDIS_HOST,REDIS_PORT)
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/15'
# celery worker的并发数，默认是服务器的内核数目,也是命令行-c参数指定的数目
CELERYD_CONCURRENCY = 4
#指定导入的任务模块
CELERY_IMPORTS = (
    'handle_data.tasks'
)

# 设置默认的队列名称，如果一个消息不符合其他的队列就会放在默认队列里面，如果什么都不设置的话，数据都会发送到默认的队列中
CELERY_DEFAULT_QUEUE = "default"
# 设置详细的队列 exchange_type有三种类型，分别是 direct topic fanout 参考https://blog.51cto.com/linuxnewstar/1884437
'''
1. fanout: 广播式，它不需要指定路由就会把所有发送到该Exchange的消息路由到所有与它绑定的Queue中
2. direct:该类型的Exchange路由规则很简单，它会把消息路由到那些binding_key与routing_key完全匹配的Queue中
3. topic:该类型的Exchange在匹配规则上进行了扩展，它与direct类型的Exchage相似，也是将消息路由到binding key与routing_key相匹配的Queue中，但这里的匹配规则有些不同，它约定

    routing key为一个句点号“. ”分隔的字符串（我们将被句点号“. ”分隔开的每一段独立的字符串称为一个单词），如“*.task.*”、"*.*.email"、“*.add”

    binding key与routing key一样也是句点号“. ”分隔的字符串

    binding key中可以存在两种特殊字符“*”与“#”，用于做模糊匹配，其中“*”用于匹配一个单词，“#”用于匹配多个单词（可以是零个）
'''
CELERY_QUEUES = {
    "default": {  # 这是上面指定的默认队列
        "exchange": "default",
        "routing_key": "default",
        "exchange_type": "direct",
    },
    "to_create": {  # 这是一个to_product队列 凡是to_product开头的routing key都会被放到这个队列
        "routing_key": "create",
        "exchange": "create",
        "exchange_type": "direct",
    },
    "to_analysis": {  # 设置扇形交换机
        "routing_key": "analysis",
        "exchange": "analysis",
        "exchange_type": "direct",
    },
    "to_save": {  # 设置扇形交换机
        "routing_key": "save",
        "exchange": "save",
        "exchange_type": "direct",
    },
}

# 给不同的任务设置不同的routers，将任务消息存放到对应的queue
CELERY_ROUTES = {
    'handle_data.tasks.to_create': {'queue': 'to_create', 'routing_key': 'create'},
    'handle_data.tasks.to_analysis': {'queue': 'to_analysis', 'routing_key': 'analysis'},
    'handle_data.tasks.to_save': {'queue': 'to_save', 'routing_key': 'save'},
}


''''
# 指定任务序列化方式
CELERY_TASK_SERIALIZER = 'msgpack'
# 指定结果序列化方式
CELERY_RESULT_SERIALIZER = 'msgpack'
# 任务过期时间,celery任务执行结果的超时时间
CELERY_TASK_RESULT_EXPIRES = 60 * 20
# 指定任务接受的序列化类型.
CELERY_ACCEPT_CONTENT = ["msgpack"]
# 任务发送完成是否需要确认，这一项对性能有一点影响
CELERY_ACKS_LATE = True
# 压缩方案选择，可以是zlib, bzip2，默认是发送没有压缩的数据
CELERY_MESSAGE_COMPRESSION = 'zlib'
# 规定完成任务的时间,在5s内完成任务，否则执行该任务的worker将被杀死，任务移交给父进程
CELERYD_TASK_TIME_LIMIT = 5  
# celery worker 每次去rabbitmq预取任务的数量
CELERYD_PREFETCH_MULTIPLIER = 4
# 每个worker执行了多少任务就会死掉，默认是无限的
CELERYD_MAX_TASKS_PER_CHILD = 40
'''
