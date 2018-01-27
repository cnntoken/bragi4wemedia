# -*- coding: utf-8 -*-

import datetime

from corelib.store import (Document, StringField, DictField, DateTimeField,
        ListField, IntField, BooleanField)

from corelib.consts import LANG_DOMAIN_MAPPING
from articles.consts import ARTICLE_SUBMIT_LIMIT

class Article(Document):

    media_id = StringField()
    title = StringField()
    content = StringField()
    top_images = ListField(DictField())
    related_images = ListField(DictField())
    youtube_video_ids = ListField(StringField())
    online_url = StringField()
    online_seq_id = IntField()
    cover_type = IntField()
    words_count = IntField()

    status = IntField()
    category = StringField()
    keywords = ListField(StringField())
    language = StringField()

    published_at = DateTimeField()
    last_modified_at = DateTimeField()
    submited_at = DateTimeField()
    takedown_at = DateTimeField()
    deleted_at = DateTimeField()
    last_op_at = DateTimeField()

    checked_at = DateTimeField()
    checker_email = StringField()
    checker = StringField()
    check_reason = StringField()
    check_reason_type = IntField()

    submit_times = IntField()

    revision = BooleanField()

    porn_score = IntField()

    @property
    def source_url(self):
        return 'mpa_%s' % str(self.id)

    def get_media(self):
        m = getattr(self, '_media', None)
        if m:
            return m
        from media.models import MediaAccount
        m = MediaAccount.objects.with_id(self.media_id)
        self._media = m
        return m

    def gen_online_url(self):
        if not self.online_url:
            return None
        domain = LANG_DOMAIN_MAPPING.get(self.language)
        if not domain:
            domain = 'newsdog.today'
        return 'http://%s%s' % (domain, self.online_url)

    def check_reached_submit_limit(self):
        return self.submit_times >= ARTICLE_SUBMIT_LIMIT

class ArticleAdminOperateLog(Document):
    article_id = StringField()
    operator_id = StringField()
    operate_type = IntField()
    operate_at = DateTimeField()
    operator_email = StringField()
    media_id = StringField()
    limit_post_times = IntField()

    @classmethod
    def generate_log(cls, request, article_id, operate_type, media_id=None, limit_post_times=None):
        now = datetime.datetime.utcnow()
        if media_id:
            media_id = str(media_id)
        ArticleAdminOperateLog.objects.create(article_id=article_id, operator_id=str(request.user.id),
                operate_type=operate_type, operate_at=now, operator_email=request.user.email,
                media_id=media_id, limit_post_times=limit_post_times)
