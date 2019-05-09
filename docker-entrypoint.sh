#!/bin/sh
set -e

if [ "$QUEUE" = "$C_QUEUE" ]; then
	celery -A handle_data.celery_app worker -l info -Q to_create --uid 13
elif [ "$QUEUE" = "$A_QUEUE" ]; then
	celery -A handle_data.celery_app worker -l info -Q to_analysis --uid 13
elif [ "$QUEUE" = "$S_QUEUE" ]; then
	celery -A handle_data.celery_app worker -l info -Q to_save --uid 13
else
	exit 1
fi
