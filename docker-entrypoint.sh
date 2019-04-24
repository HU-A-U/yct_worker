#!/bin/sh
set -e

if [ "$QUEUE" = "$P_QUEUE" ]; then
	celery -A handle_data worker -l info -Q to_product
elif [ "$QUEUE" = "$A_QUEUE" ]; then
	celery -A handle_data worker -l info -Q to_analysis
elif [ "$QUEUE" = "$C_QUEUE" ]; then
	celery -A handle_data worker -l info -Q to_consume
else
	exit 1
fi
