# -*- coding: utf-8 -*-

import datetime
from corelib import time as time_utils
from corelib.consts import ONE_DAY

ACTION_PARAM_MAPPING = {
    'next': 'id__lt',
    'prev': 'id__gt',
}

ACTION_REVERSE_PARAM_MAPPING = {
    'next': 'id__gt',
    'prev': 'id__lt',
}

ACTION_PARAM_ORDER_MODIFIED_MAPPING = {
    'next': 'modified_at__lt',
    'prev': 'modified_at__gt',
}

ACTION_REVERSE_PARAM_ORDER_MODIFIED_MAPPING = {
    'next': 'modified_at__gt',
    'prev': 'modified_at__lt',
}

ARTICLE_ACTION_PARAM_MAPPING = {
    'next': 'last_op_at__lt',
    'prev': 'last_op_at__gt',
}

ARTICLE_ACTION_REVERSE_PARAM_MAPPING = {
    'next': 'last_op_at__gt',
    'prev': 'last_op_at__lt',
}

def gen_page_query_params(request, default_count=10, query_reverse=False):
    orders_param = {
        'positive': ('id',),
        'reverse': ('-id',),
    }
    return gen_page_query_params_model(request, orders_param, gen_action_param, default_count, query_reverse)

def gen_action_param(params, query_reverse, action, read_tag):
    if query_reverse:
        action_params = ACTION_REVERSE_PARAM_MAPPING[action]
    else:
        action_params = ACTION_PARAM_MAPPING[action]
    params[action_params] = read_tag

def gen_page_query_order_modified_time(request, default_count=10, query_reverse=False):
    orders_param = {
        'positive': ('modified_at',),
        'reverse': ('-modified_at',),
    }
    return gen_page_query_params_model(request, orders_param, gen_action_param_order_modified_time, default_count, query_reverse)

def gen_action_param_order_modified_time(params, query_reverse, action, read_tag):
    from media.models import Announcement
    ann = Announcement.objects.with_id(read_tag)
    if query_reverse:
        action_params = ACTION_REVERSE_PARAM_ORDER_MODIFIED_MAPPING[action]
    else:
        action_params = ACTION_PARAM_ORDER_MODIFIED_MAPPING[action]
    params[action_params] = ann.modified_at

def gen_page_query_params_model(request, orders_param, action_func, default_count=10, query_reverse=False):
    params = {}
    order = orders_param['positive'] if query_reverse else orders_param['reverse']
    read_tag = request.GET.get('read_tag')
    count = int(request.GET.get('count', default_count))
    reverse = False
    action = request.GET.get('action', 'next')
    if action == 'prev':
        reverse = True
        order = orders_param['reverse'] if query_reverse else orders_param['positive']
    if not read_tag:
        return params, order, reverse, count
    action_func(params, query_reverse, action, read_tag)
    return params, order, reverse, count

def gen_request_ip(request):
    if "HTTP_X_REAL_IP" in request.META:
        client_ip = request.META["HTTP_X_REAL_IP"]
    else:
        client_ip = request.META["REMOTE_ADDR"]
    return client_ip

def gen_current_page_items(odm_cls, params, order, reverse, count):
    items = odm_cls.objects(**params).order_by(*order).limit(count+1)
    has_next_page = False
    items = list(items)
    if len(items) > count:
        items = items[:count]
        has_next_page = True
    if reverse:
        items = list(reversed(items))
    return items, has_next_page

def gen_article_action_param(params, query_reverse, action, read_tag):
    from articles.models import Article
    article = Article.objects.with_id(read_tag)
    if query_reverse:
        article_action = ARTICLE_ACTION_REVERSE_PARAM_MAPPING[action]
    else:
        article_action = ARTICLE_ACTION_PARAM_MAPPING[action]
    params[article_action] = article.last_op_at

def gen_article_page_query_params(request, default_count=10, query_reverse=False):
    orders_param = {
        'positive': ('last_op_at',),
        'reverse': ('-last_op_at',),
    }
    return gen_page_query_params_model(request, orders_param, gen_article_action_param, default_count, query_reverse)

class StatPagerMixin(object):

    def process_get_params(self, request):
        days = int(request.GET.get('days', 7))
        count = int(request.GET.get('count', 10))
        end_date_str = request.GET.get('end_date')
        if end_date_str:
            end_time = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
            end_time += ONE_DAY
        else:
            india_now = time_utils.get_india_now()
            end_time = datetime.datetime(india_now.year, india_now.month, india_now.day,
                    0, 0, 0)
            end_time += ONE_DAY
        start_time = end_time - datetime.timedelta(days)
        return start_time, end_time, count
