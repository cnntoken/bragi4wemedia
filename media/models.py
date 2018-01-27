# -*- coding: utf-8 -*-

import random
import re
import datetime
import math
from hashlib import md5

from mongoengine import NotUniqueError
from corelib.store import (Document, StringField, DictField, BooleanField,
        DateTimeField, IntField, ListField, FloatField)
from corelib import time as time_utils

from media.consts import (VERIFY_STATUS_PASSED, VERIFY_STATUS_FAILED,
        VERIFY_STATUS_SUBMITTED, VERIFY_STATUS_SUSPEND, MEDIA_GRADE_A,
        MEDIA_GRADE_P, WD_STATUS_SUMBMITTED, MEDIA_INTERNSHIP_ARTICLE_NUM,
        MEDIA_PROMOTION_NEWBIE_STATUS, MEDIA_PROMOTION_BANNED_STATUS,
        MEDIA_PROMOTION_NORMAL_STATUS, MEDIA_PROMOTION_BONUS_AMOUNT,
        MEDIA_PROMOTION_NOTIFICATION_BANNED_TYPE, MEDIA_AMDIN_OPERATE_LIMIT_POST_CONTENT_TEMPL,
        MEDIA_AMDIN_OPERATE_TYPE_LIMIT_POST)
from media import utils as media_utils
from media.exception import MediaPcodeNotExist, MediaPromotionCreateFail, MediaPcodeNotAllowable

from articles.models import Article
from articles.consts import STATUS_PUBLISHED

from notifications import utils as notify_utils

MULTI_SPACES_PATTERN = re.compile('\s{2,}')
PROMOTION_CODE_CAND = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a',
        'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
        'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


class MediaAccount(Document):
    verified_status = IntField()
    info_update = BooleanField()
    lang_synced_status_mapping = DictField()

    title = StringField()
    unformatted_title = StringField()
    description = StringField()
    icon = StringField()

    new_title = StringField()
    new_description = StringField()
    new_icon = StringField()

    user_id = StringField()
    user_pan_no = StringField()
    user_real_name = StringField()
    user_email = StringField()
    user_phone = StringField()
    user_location_address = StringField()
    user_location_city = StringField()
    user_location_state = StringField()
    user_pin_code = StringField()
    last_modified_at = DateTimeField()

    checked_at = DateTimeField()
    updated_at = DateTimeField()
    create_at = DateTimeField()
    checker_email = StringField()
    updated_email = StringField()
    check_reason = StringField()

    valid_duration = IntField()
    share_percent = IntField()
    total_revenue = FloatField()
    revenue_update_date = StringField()
    total_withdraw = FloatField()

    payment_info = DictField()

    daily_submit_limit = IntField()
    limit_end_at = DateTimeField()
    limit_reason = StringField()
    suspend_reason = StringField()
    # NOTE: india time zone

    grade = IntField()
    remark = StringField()
    is_internship = BooleanField()

    @classmethod
    def check_pan_no_reach_limit(cls, user_pan_no):
        count = cls.objects(user_pan_no=user_pan_no).count()
        if count >= 3:
            return True
        return False

    @classmethod
    def check_pan_no_is_black(cls, user_pan_no):
        black_pan_no = PancardBlackList.objects(user_pan_no=user_pan_no)
        return bool(black_pan_no)

    def withdraw_stat(self):
        total_revenue, total_withdraw, total_balance = MediaAccount.calc_balance(self.total_revenue or 0,
                self.total_withdraw or 0)
        return dict(total_revenue=('%.2f'%total_revenue), total_withdraw=('%.2f'%total_withdraw),
                total_balance=('%.2f'%total_balance))

    @classmethod
    def calc_balance(cls, revenue, withdraw):
        def decimal_floor(num):   # 小数向下取整函数
            ret = (math.floor(num*100))/100.0
            if ret > num: # 避免极端情况，产生的数据错误
                return ret-0.01
            return ret

        def decimal_ceil(num):  # 小数向上取整函数
            ret = (math.ceil(num*100))/100.0
            if ret < num:
                return ret+0.01
            return ret

        if revenue - withdraw > 1: # 在两个数距离较大的时候，被减数向下取整，减数向上取整
            _revenue = decimal_floor(revenue)
            _withdraw = decimal_floor(withdraw)
            if _withdraw != withdraw: # 避免withdraw为零的时候，出现0.01的情况，造成用户感知明显
                _withdraw += 0.01
        else:  # 在两个数距离较小时，被减数和减数都向下取整，避免减数大于被减数的情况出现
            _revenue = decimal_floor(revenue)
            _withdraw = int(withdraw*100)/100.0

        _balance = (_revenue - _withdraw)
        return _revenue, _withdraw, decimal_floor(_balance)

    def can_auto_pass(self):
        if self.grade == MEDIA_GRADE_A:
            return not 5 == random.randint(0, 9)

        if self.grade == MEDIA_GRADE_P:
            return not 1 == random.randint(0, 1)
        return False

    def judge_pass_internship(self):
        pass_article_count = Article.objects(media_id=str(self.id), status=STATUS_PUBLISHED).count()
        return pass_article_count >= (MEDIA_INTERNSHIP_ARTICLE_NUM - 1)

    def limit_media(self, request, limit_days, daily_limit, limit_reason):
        limit_end_time = time_utils.get_india_now() + datetime.timedelta(int(limit_days))
        self.limit_end_at = datetime.datetime(limit_end_time.year,
                limit_end_time.month, limit_end_time.day)
        self.limit_reason = limit_reason
        self.daily_submit_limit = daily_limit
        self.save()
        notify_utils.create_media_limit_notification(self)
        content = MEDIA_AMDIN_OPERATE_LIMIT_POST_CONTENT_TEMPL % (daily_limit, limit_days)
        MediaAdminOperateLog.generate_log(request, str(self.id), MEDIA_AMDIN_OPERATE_TYPE_LIMIT_POST, content)
        mpu = MediaPromotionUser.objects(media_id=str(self.id)).first()
        mpu.banned_promotion_user()


    @property
    def verify_passed(self):
        return self.verified_status == VERIFY_STATUS_PASSED

    @property
    def verify_failed(self):
        return self.verified_status == VERIFY_STATUS_FAILED

    @property
    def verify_submitted(self):
        return self.verified_status == VERIFY_STATUS_SUBMITTED

    @property
    def verify_suspend(self):
        return self.verified_status == VERIFY_STATUS_SUSPEND

    @property
    def site_url(self):
        return media_utils.gen_site_url(self.id)

    @classmethod
    def gen_unformatted_title(cls, title):
        unformatted_title = title.strip().lower()
        return MULTI_SPACES_PATTERN.sub(' ', unformatted_title)

    def add_submit_log(self, article_id):
        try:
            MediaSubmitArticleLog.objects.create(media_id=str(self.id),
                article_id=article_id, date=str(time_utils.get_india_now().date()))
        except NotUniqueError:
            return

    @property
    def is_under_limit(self):
        if not self.limit_end_at:
            return False
        now = time_utils.get_india_now()
        if now > self.limit_end_at:
            return False
        return True

    @property
    def under_limit_date(self):
        if not self.is_under_limit:
            return
        if not self.limit_end_at:
            return None
        return self.limit_end_at.strftime('%Y-%m-%d %H:%M')

    def check_reached_submit_limit(self):
        if not self.is_under_limit:
            return False
        daily_submit_count = MediaSubmitArticleLog.objects(media_id=str(self.id),
                date=str(time_utils.get_india_now().date())).count()
        return daily_submit_count >= self.daily_submit_limit

    def check_internship_submit_limit(self, article_id=None):
        if not self.is_internship:
            return False
        if article_id:
            article_submit_count = MediaSubmitArticleLog.objects(media_id=str(self.id),
                    article_id=str(article_id)).count()
            if article_submit_count > 0:
                return False
        daily_submit_count = MediaSubmitArticleLog.objects(media_id=str(self.id),
                date=str(time_utils.get_india_now().date())).count()
        return daily_submit_count >= self.daily_submit_limit

    def withdraw_in_processing(self):
        count = WithDraw.objects(media_id=str(self.id), status=WD_STATUS_SUMBMITTED).count()
        return not count == 0

    def has_paytm(self):
        return self.payment_info and 'paytm_account' in self.payment_info


class MediaSubmitArticleLog(Document):
    media_id = StringField()
    article_id = StringField()
    date = StringField()

class Announcement(Document):
    title = StringField()
    content = StringField()
    published_at = DateTimeField()
    modified_at = DateTimeField()
    user_id = StringField()
    user_email = StringField()
    status = IntField()
    type = IntField()

class WithDraw(Document):
    user_id = StringField()
    media_id = StringField()
    amount = FloatField()
    payment_info = DictField()
    create_at = DateTimeField()
    status = IntField()
    operator_id = StringField()
    operator_email = StringField()
    operate_at = DateTimeField()

class WeeklyMediaIncome(Document):
    start_date = StringField()
    end_date = StringField()
    revenue = FloatField()
    site_url = StringField()

class Bonus(Document):
    amount = FloatField()
    type = IntField()
    reason = StringField()
    create_at = DateTimeField()
    operator_id = StringField()
    operator_email = StringField()
    media_id = StringField()

class PancardBlackList(Document):
    user_pan_no = StringField()

class MediaAdminOperateLog(Document):
    media_id = StringField()
    operator_id = StringField()
    operate_type = IntField()
    operate_at = DateTimeField()
    operate_content = StringField()
    operator_email = StringField()

    @classmethod
    def generate_log(cls, request, media_id, operate_type, operate_content):
        now = datetime.datetime.utcnow()
        MediaAdminOperateLog.objects.create(media_id=media_id, operator_id=str(request.user.id),
            operate_type=operate_type, operate_at=now,
            operate_content=operate_content, operator_email=request.user.email)

class MediaPromotionUser(Document):
    media_id = StringField()
    media_join_at = DateTimeField()
    banned_at = StringField()
    status = IntField()
    promotion_code = StringField()
    time_reached = BooleanField()
    read_reached = BooleanField()
    no_banned = BooleanField()

    @classmethod
    def gen_pcode(cls):
        pcode = None
        for x in xrange(3):
            code = cls.gen_promotion_code()
            mpc = cls.objects(promotion_code=code).first()
            if mpc:
                continue
            pcode = code
            break
        return pcode

    @classmethod
    def gen_promotion_code(cls):
        chars = []
        for x in xrange(6):
            chars.append(random.choice(PROMOTION_CODE_CAND))
        return ''.join(chars)

    @classmethod
    def gen_promotion_user(cls, media_id):
        now = datetime.datetime.utcnow()
        pcode = cls.gen_pcode()
        mpu = cls.objects.create(media_id=media_id, media_join_at=now,
                    status=MEDIA_PROMOTION_NEWBIE_STATUS, promotion_code=pcode, time_reached=False,
                    read_reached=False, no_banned=True)
        return mpu

    def banned_promotion_user(self):
        if self.status == MEDIA_PROMOTION_NORMAL_STATUS:
            media = MediaAccount.objects.with_id(self.media_id)
            notify_utils.create_media_promotion_notification(media, MEDIA_PROMOTION_NOTIFICATION_BANNED_TYPE)
        self.status = MEDIA_PROMOTION_BANNED_STATUS
        now = str(datetime.datetime.utcnow().date())
        self.banned_at = now
        self.no_banned = False
        self.save()
        mpls = MediaPromotionLog.objects(get_bonus=False, father_media_id=self.media_id)
        mpls.update(set__is_banned=True, set__modified_at=now)

    def judge_to_normal(self):
        return self.time_reached and self.read_reached and self.no_banned

    @classmethod
    def get_pcode_owner_media(cls, pcode):
        mpu = cls.objects(promotion_code=pcode).first()
        if not mpu:
            raise MediaPcodeNotExist
        if mpu.status != MEDIA_PROMOTION_NORMAL_STATUS:
            raise MediaPcodeNotAllowable
        return mpu

class MediaPromotionLog(Document):
    media_id = StringField()
    father_media_id = StringField()
    promotion_code = StringField()
    get_bonus = BooleanField()
    get_bonus_at = DateTimeField()
    bonus_amount = FloatField()
    start_at = DateTimeField()
    is_banned = BooleanField()
    modified_at = DateTimeField()

    @classmethod
    def gen_promotion_log(cls, media_id, father_media_id, promotion_code):
        now = datetime.datetime.utcnow()
        try:
            mpl = cls.objects.create(media_id=str(media_id), father_media_id=father_media_id, promotion_code=promotion_code,
                    get_bonus=False, bonus_amount=MEDIA_PROMOTION_BONUS_AMOUNT, start_at=now, is_banned=False, modified_at=now)
        except NotUniqueError:
            raise MediaPromotionCreateFail


class PartnerToken(Document):
    partner_key = StringField()
    partner_secret = StringField()
    domain = StringField()
    site_name = StringField()

    @classmethod
    def generate_token(cls, domain, site_name):
        token = cls.objects(domain=domain).first()
        if not token:
            m = md5(domain)
            partner_key = m.hexdigest()
            m = md5(site_name)
            partner_secret = m.hexdigest()
            token = cls.objects.create(domain=domain, site_name=site_name,
                    partner_key=partner_key, partner_secret=partner_secret)
        return {
                'secret': token.partner_secret,
                'key': token.partner_key
                }
