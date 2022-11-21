#!/bin/sh

alembic upgrade head
celery -A worker.tasks worker -P threads