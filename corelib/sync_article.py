# -*- coding: utf-8 -*-

import datetime

from articles.utils import auto_fail_article
from articles.models import Article
from articles.consts import STATUS_SUBMITTED, STATUS_PUBLISHED
from articles.exception import ArticleSyncFailed
from articles.serializers import ArticleSyncSerializer
from articles import processor as article_processor


def sync_article(article):
    sync_data = ArticleSyncSerializer(article).data
    status, reason, data = article_processor.create_article(sync_data,
            article.language)
    if not status:
        return False, reason
    online_url = data.get('online_url')
    if online_url:
        article.online_url = online_url
    online_seq_id = data.get('online_seq_id')
    if online_seq_id:
        article.online_seq_id = online_seq_id
    return True, reason

def sync_mp_article(article):
    now = datetime.datetime.utcnow()
    article.published_at = now
    status, reason = sync_article(article)
    if not status:
        auto_fail_article(article, reason)
        article.save()
        raise ArticleSyncFailed
    article.status = STATUS_PUBLISHED
    article.save()




