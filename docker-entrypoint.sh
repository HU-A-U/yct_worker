#!/bin/sh
set -e

if [ "$QUEUE" = "$P_QUEUE" ]; then
	celery -A handle_data.celery_app worker -l info -Q to_product --uid 13
elif [ "$QUEUE" = "$A_QUEUE" ]; then
	celery -A handle_data.celery_app worker -l info -Q to_analysis --uid 13
elif [ "$QUEUE" = "$C_QUEUE" ]; then
	celery -A handle_data.celery_app worker -l info -Q to_consume --uid 13
else
	exit 1
fi
