# -*- coding: utf-8 -*-

from corelib.consts import INDIA_TIME_DELTA

def datetime2india_timestr(dt):
    if not dt:
        return None
    time = dt + INDIA_TIME_DELTA
    return time.strftime('%Y-%m-%d %H:%M:%S')

def datetime2utc_timestr(dt):
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')

import datetime

def get_india_now():
    utcnow = datetime.datetime.utcnow()
    return utcnow + INDIA_TIME_DELTA

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
