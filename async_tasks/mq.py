# -*- coding: utf-8 -*-

from celery import Celery

import sys, os
from os.path import dirname, realpath
from raven import Client
from raven.contrib.celery import register_signal

sys.path.append(dirname(dirname(realpath(__file__))))

from corelib.store import init_connection
from bragi.settings import RAVEN_CONFIG

def init_mq():
    mq = Celery('async_tasks')
    mq.config_from_object('async_tasks.settings')
    return mq

init_connection()
client = Client(RAVEN_CONFIG['dsn'])
register_signal(client)

task_mq = init_mq()
