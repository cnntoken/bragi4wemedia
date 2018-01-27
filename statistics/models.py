# -*- coding: utf-8 -*-

from corelib.store import (Document, StringField, DictField, BooleanField, IntField,
        FloatField)

class DailyArticle(Document):
    date = StringField()
    online_seq_id = IntField()
    lang = StringField()
    rec_count = IntField()
    read_count = IntField()
    uclick_count = IntField() # user unique read count
    share_count = IntField()
    comment_count = IntField()
    favorite_count = IntField()

class RealTimeArticle(Document):
    online_seq_id = IntField()
    lang = StringField()
    rec_count = IntField()
    read_count = IntField()
    share_count = IntField()
    comment_count = IntField()
    favorite_count = IntField()

class RealTimeMedia(Document):
    lang = StringField()
    site_url = StringField()
    follow_count = IntField()
    read_count = IntField()

class DailyMedia(Document):
    lang = StringField()
    date = StringField()
    rec_count = IntField()
    read_count = IntField()
    uclick_count = IntField()
    share_count = IntField()
    comment_count = IntField()
    mp_fans_count = IntField()
    new_count = IntField()
    site_url = StringField()
    live_article_count = IntField()
    extra_rec_count = IntField()
    extra_read_count = IntField()
    extra_uclick_count = IntField()

class DailyTotalRevenue(Document):
    date = StringField()
    total_revenue = FloatField()

class DailyMpBenefit(Document):
    lang = StringField()
    date = StringField()
    site_url = StringField()
    revenue = FloatField()
    checked_revenue = FloatField()
    checking_status = IntField()

class RevenuePercent(Document):
    lang = StringField()
    category = StringField()
    revenue_rate = FloatField()

class DailyMpArticleBenefit(Document):
    date = StringField()
    lang = StringField()
    online_seq_id = IntField()
    category = StringField()
    site_url = StringField()
    uclick = StringField()
    share_percent = FloatField()
    revenue_rate = FloatField()
    unit_price = FloatField()
    revenue = FloatField()
    checking_status = IntField()
