# -*- coding: utf-8 -*-

from articles.serializers import ArticleSyncSerializer
from articles.consts import STATUS_FAILED
from notifications import utils as notify_utils
from articles import processor as article_processor

def check_validate_info(article):
    sync_data = ArticleSyncSerializer(article).data
    _, _, validate_info = article_processor.check_usable_status(sync_data, article.language)
    return validate_info

def batch_check_validate_info(articles, lang):
    articles_data = [ArticleSyncSerializer(article).data for article in articles]
    _, _, validate_infos = article_processor.batch_check_usable_status(articles_data, lang)
    return validate_infos

def check_need_auto_fail(validate_info):
    duplicated = validate_info.get('duplicated')
    if duplicated:
        return True, 'The article has duplicated content with others.'
    sensitive = validate_info.get('sensitive')
    if sensitive:
        score = validate_info.get('sens_score')
        if score == 1:
            return True, 'The article contains sensitive content.'
    return False, ''

def auto_fail_article(article, reason):
    notify_utils.create_failed_notification(article, reason)
    article.status = STATUS_FAILED
    article.revision = True
    article.check_reason = reason
    article.check_reason_type = -1
