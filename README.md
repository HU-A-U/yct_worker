# yct_worker

###启动命令

docker run -e QUEUE=to_product --name worker_p -d daocloud.io/huhuhuhu/yct_worker

docker run -e QUEUE=to_analysis --name worker_a -d daocloud.io/huhuhuhu/yct_worker

docker run -e QUEUE=to_consume --name worker_c -d daocloud.io/huhuhuhu/yct_worker

###开启flower后台监控

celery flower --broker=amqp://cic_admin:JYcxys@3030@47.102.218.137:5672/yct