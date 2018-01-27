# -*- coding: utf-8 -*-

from notifications.models import Notification
from notifications.consts import (TYPE_ARTICLE_PASSED, TYPE_ARTICLE_FAILED,
        TYPE_ARTICLE_SUSPENDED, TYPE_MEDIA_BONUS, CONTENT_TMPL_TYPE_MAPPING,
        BN_TYPE_TMPL_MAPPING, TYPE_CUSTOM, TYPE_MEDIA_LIMIT, MEDIA_LIMIT_CONTENT_TMPL,
		MEDIA_INFO_UPDATE_PASSED, MEDIA_INFO_UPDATE_FAIELD, MEDIA_PROMOTION_BANNED_NOTIFICATION_MAPPING,
        TYPE_MEDIA_PROMOTION, ARTICLE_CHANGE_CATEGORY_TMPL, TYPE_ARTICLE_CHANGE_CATEGORY,
        MEDIA_COMMENT_PERMISSION, TYPE_MEDIA_COMMENT_PERMISSION)

def create_passed_notification(article):
    content_tmpl = CONTENT_TMPL_TYPE_MAPPING[TYPE_ARTICLE_PASSED]
    content = content_tmpl % article.title
    Notification.create_notification(article.media_id, TYPE_ARTICLE_PASSED, content)

def create_failed_notification(article, reason):
    content_tmpl = CONTENT_TMPL_TYPE_MAPPING[TYPE_ARTICLE_FAILED]
    content = content_tmpl % ('/management/articles/%s/' % str(article.id), article.title, reason)
    Notification.create_notification(article.media_id, TYPE_ARTICLE_FAILED, content)

def create_suspended_notification(article, reason):
    content_tmpl = CONTENT_TMPL_TYPE_MAPPING[TYPE_ARTICLE_SUSPENDED]
    content = content_tmpl % (article.title, reason)
    Notification.create_notification(article.media_id, TYPE_ARTICLE_SUSPENDED, content)

def create_bonus_notification(media_id, _type, amount, reason):
    content_tmpl = BN_TYPE_TMPL_MAPPING[_type]
    content = content_tmpl % (round(amount, 2), reason)
    Notification.create_notification(media_id, TYPE_MEDIA_BONUS, content)

def create_custom_notification(media_id, content):
    notification = Notification.create_notification(media_id, TYPE_CUSTOM, content)
    return notification.id

def create_media_limit_notification(media_account):
    content = MEDIA_LIMIT_CONTENT_TMPL % (media_account.limit_reason,
            media_account.daily_submit_limit, media_account.under_limit_date)
    Notification.create_notification(str(media_account.id), TYPE_MEDIA_LIMIT, content)

def create_media_info_update_notification(media_account, passed):
    content = MEDIA_INFO_UPDATE_PASSED if passed else MEDIA_INFO_UPDATE_FAIELD
    Notification.create_notification(str(media_account.id), TYPE_MEDIA_LIMIT, content)

def create_media_promotion_notification(media_account, _type, child_media_name=""):
    content_tmpl = MEDIA_PROMOTION_BANNED_NOTIFICATION_MAPPING[_type]
    content = content_tmpl.format(account_name=media_account.title, child_account_name=child_media_name)
    Notification.create_notification(str(media_account.id), TYPE_MEDIA_PROMOTION, content)

def create_article_change_category_notification(media_account, article_id, article_title):
    content = ARTICLE_CHANGE_CATEGORY_TMPL.format(article_id=article_id, article_title=article_title)
    Notification.create_notification(str(media_account.id), TYPE_ARTICLE_CHANGE_CATEGORY, content)

def create_media_comment_permission_notification(media_account, _type):
    content = MEDIA_COMMENT_PERMISSION[_type]
    Notification.create_notification(str(media_account.id), TYPE_MEDIA_COMMENT_PERMISSION, content)
