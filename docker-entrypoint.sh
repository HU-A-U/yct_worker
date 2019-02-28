
celery multi start to_product -A handle_data worker -l info -Q to_product
celery multi start to_analysis -A handle_data worker -l info -Q to_analysis
celery multi start to_consume -A handle_data worker -l info -Q to_consume

/usr/local/bin/mitmdump -s /code/start_script.py