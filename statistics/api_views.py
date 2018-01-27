# -*- coding: utf-8 -*-

import datetime
from itertools import izip

from corelib.views import BaseView
from corelib.consts import INDIA_TIME_DELTA, ONE_DAY
from corelib.requests import StatPagerMixin, gen_page_query_params, gen_current_page_items
from corelib.response import gen_page_response
from corelib.serializers import Serializer

from articles.models import Article
from articles.consts import STATUS_OFFLINE, STATUS_PUBLISHED, STATUS_ADMIN_OFFLINE
from articles.serializers import ArticleCompactStatisticSerializer

from statistics import utils as stat_utils


class StatisticsTotal(StatPagerMixin, BaseView):

    def get(self, request):
        start_time, end_time, count = self.process_get_params(request)
        params = {'site_url': self.media_account.site_url, 'date__gte': str(start_time.date()),
                'date__lt': str(end_time.date())}
        from mongoengine import context_managers
        from statistics.models import DailyMedia
        with context_managers.switch_db(DailyMedia, 'statistics') as DailyMedia:
            stats = DailyMedia.objects(**params).order_by('-id')
        if not stats:
            return {}
        show_counts, read_counts, comment_counts, article_counts = \
                izip(*((stat.rec_count, stat.uclick_count, stat.comment_count, stat.new_count) for stat in stats))
        return dict(show_count=sum(stat_utils.normalize_count(c) for c in show_counts),
                read_count=sum(stat_utils.normalize_count(c) for c in read_counts),
                comment_count=sum(stat_utils.normalize_count(c) for c in comment_counts),
                article_count=sum(stat_utils.normalize_count(c) for c in article_counts))

class StatisticsByArticle(StatPagerMixin, BaseView):

    def get(self, request):
        page_params, order, reverse, count = gen_page_query_params(request)
        start_time, end_time, count = self.process_get_params(request)
        start_time -= INDIA_TIME_DELTA
        end_time -= INDIA_TIME_DELTA
        params = {'media_id': self.media_id, 'published_at__gte': start_time,
                'published_at__lt': end_time, 'status__in': [STATUS_PUBLISHED, STATUS_OFFLINE, STATUS_ADMIN_OFFLINE]}
        params.update(page_params)
        stats, has_next_page = gen_current_page_items(Article, params, order, reverse, count)
        return gen_page_response([ArticleCompactStatisticSerializer(stat).data \
                for stat in stats], has_next_page)
