# -*- coding: utf-8 -*-

import json

import os.path
from contextlib import contextmanager

import logbook
from logbook import (exception, info, TimedRotatingFileHandler)
from raven.contrib.django.raven_compat.models import sentry_exception_handler

from bragi import settings

logbook.set_datetime_format("local")
bubble = settings.DEBUG

error_path = os.path.join(settings.LOG_DIR, 'error.log')
access_path = os.path.join(settings.LOG_DIR, 'access.log')
task_path = os.path.join(settings.LOG_DIR, 'task.log')

err_handler = TimedRotatingFileHandler(error_path, date_format='%Y-%m-%d', bubble=True)
access_handler = TimedRotatingFileHandler(access_path, date_format='%Y-%m-%d', bubble=True)
task_handler = TimedRotatingFileHandler(task_path, date_format='%Y-%m-%d', bubble=True)

def log_task(record):
    with task_handler:
        info(record)

def log_access(record):
    with access_handler:
        info(record)

def log_error(record):
    with err_handler:
        info(record)

def log2sentry():
    try:
        sentry_exception_handler()
    except:
        pass

def log_exception(record, **kwargs):
    msg = json.dumps(record) if isinstance(record, dict) else record
    msg = '`'.join(map(str, record))
    with err_handler:
        exception(msg)

    try:
        sentry_exception_handler(extra={'msg': str(msg)}, **kwargs)
    except:
        pass
