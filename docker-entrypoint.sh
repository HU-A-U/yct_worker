celery -A handle_data.celery_app worker -l info -Q to_product
celery -A handle_data.celery_app worker -l info -Q to_analysis
celery -A handle_data.celery_app worker -l info -Q to_consume
