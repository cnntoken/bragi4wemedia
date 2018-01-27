# -*- coding: utf-8 -*-

import datetime
from mongoengine import NotUniqueError

from django.views.generic import View

from corelib import time as time_utils
from corelib.views import BaseView
from corelib.exception.common import ParamError
from corelib.requests import StatPagerMixin, gen_page_query_params, gen_current_page_items, gen_page_query_order_modified_time
from corelib.response import RESPONSE_OK, gen_page_response
from corelib.consts import INDIA_TIME_DELTA
from corelib.utils import dingtalk

from media.exception import (HasOwnMedia, InvalidMediaInfoUpdateFrequence,
        InvalidUpdateMediaField, MediaNameDuplicated, AnnouncementNotExist,
        MediaBankInfoNotExist, MediaPanNumRelatedTooMuch, MediaAccountWithDrawInProccessing,
        MediaAccountWithDrawNotInTime, MediaPanIsBlack, MediaPcodeNotExist)
from media.models import MediaAccount, Announcement, WithDraw, WeeklyMediaIncome, Bonus, MediaPromotionUser, MediaPromotionLog
from media.mixin import CheckDuplicatedTitleMixin
from media.serializers import (MediaSettingInfoSerializer, AnnouncementSerializer, WithDrawSerializer,
        WeeklyIncomeSerializer, BonusSerializer, PromotionUserSerializer, PromotionLogSerializer, MediaNameGenerator)
from media.consts import (VERIFY_STATUS_PASSED, VERIFY_STATUS_FAILED, VERIFY_STATUS_SUBMITTED,
        ANN_STATUS_USABLE, UNMODIFIABLE_FIELDS, NEED_REVERIFIED_FIELDS, WD_STATUS_SUMBMITTED,
        UNFORMATTED_TITLE_BLACKLIST, MEDIA_GRADE_C, MEDIA_WITHDRAW_TIME, MEDIA_INTERNSHIP_DAILY_SUBMIT_LIMIT,
        ANN_TYPE_GUIDE, ANN_TYPE_MAPPING, MEDIA_PROMOTION_BONUS_AMOUNT, MEDIA_CHANGE_SETTING_TIME)
from statistics import utils as stat_utils


class MediaView(CheckDuplicatedTitleMixin, View):

    def post(self, request):
        media = request.user.get_related_media_account()
        if media:
            raise HasOwnMedia
        data = request.DATA
        if not data:
            raise ParamError
        for field in data:
            if field not in UNMODIFIABLE_FIELDS and field not in NEED_REVERIFIED_FIELDS:
                raise ParamError
        user_pan_no = data.get('user_pan_no')
        title = data.get('title')
        if not user_pan_no:
            raise ParamError
        if not title:
            raise ParamError
        reach_limit = MediaAccount.check_pan_no_reach_limit(user_pan_no)
        if reach_limit:
            raise MediaPanNumRelatedTooMuch
        is_black_pan_no = MediaAccount.check_pan_no_is_black(user_pan_no)
        if is_black_pan_no:
            raise MediaPanIsBlack
        unformatted_title = self.check_duplicated_title(title)
        promotion_code = data.get('pcode')
        del data['pcode']
        try:
            pcode_owner = MediaPromotionUser.get_pcode_owner_media(promotion_code)
        except MediaPcodeNotExist:
            pcode_owner = None
        try:
            now = datetime.datetime.utcnow()
            media = MediaAccount.objects.create(user_id=str(request.user.id),
                    verified_status=VERIFY_STATUS_SUBMITTED,
                    share_percent=50, valid_duration=7,
                    grade=MEDIA_GRADE_C,
                    unformatted_title=unformatted_title,
                    daily_submit_limit=MEDIA_INTERNSHIP_DAILY_SUBMIT_LIMIT,
                    is_internship=True,
                    create_at=now,
                    **data)
            if pcode_owner:
                MediaPromotionLog.gen_promotion_log(str(media.id), str(pcode_owner.media_id), promotion_code)
        except NotUniqueError:
            raise MediaNameDuplicated
        return RESPONSE_OK

class MediaWithDrawStat(BaseView):
    def get(self, request):
        return self.media_account.withdraw_stat()


CARD_USABLE_FIELDS = ['card_name', 'id_card_no', 'pan_card_no', 'bank']

BANKCARD_WITHDRAW_BASE_LINE = 10000

class MediaWithDraw(StatPagerMixin, BaseView):
    def post(self, request):
        data = request.DATA
        india_now = time_utils.get_india_now()
        if india_now.day > MEDIA_WITHDRAW_TIME['upper'] or india_now.day < MEDIA_WITHDRAW_TIME['lower']:
            raise MediaAccountWithDrawNotInTime
        if not data:
            raise ParamError
        amount = float(data.get('amount', 0))
        if self.media_account.has_paytm():
            if amount <= 0:
                raise ParamError
        else:
            if amount <= BANKCARD_WITHDRAW_BASE_LINE:
                raise ParamError
        total_revenue = self.media_account.total_revenue or 0
        total_withdraw = self.media_account.total_withdraw or 0
        _, _, total_balance = MediaAccount.calc_balance(total_revenue, total_withdraw)
        if amount > total_balance:
            raise ParamError
        payment_info = self.media_account.payment_info
        if not payment_info or not all(payment_info.values()):
            raise MediaBankInfoNotExist
        MediaAccount.objects(id=str(self.media_account.id)).update(inc__total_withdraw=amount)
        now = datetime.datetime.utcnow()
        with_draw = WithDraw.objects.create(media_id=str(self.media_account.id), user_id=str(request.user.id),
                payment_info=payment_info, amount=amount, create_at=now, status=WD_STATUS_SUMBMITTED)
        self.media_account = MediaAccount.objects(id=str(self.media_account.id)).first()
        withdraw_stat = self.media_account.withdraw_stat()
        withdraw_stat['id'] = str(with_draw.id)
        return withdraw_stat

    def get(self, request):
        page_params, order, reverse, count = gen_page_query_params(request)
        start_time, end_time, count = self.process_get_params(request)
        start_time -= INDIA_TIME_DELTA
        end_time -= INDIA_TIME_DELTA
        params = {'media_id': self.media_id, 'create_at__gte': start_time, 'create_at__lt': end_time}
        params.update(page_params)
        withdraws, has_next_page = gen_current_page_items(WithDraw, params, order, reverse, count)
        return gen_page_response([WithDrawSerializer(wd).data for wd in withdraws],
                has_next_page)


class MediaPaymentInfo(BaseView):

    def get(self, request):
        return self.media_account.payment_info

    def put(self, request):
        if self.media_account.withdraw_in_processing():
            raise MediaAccountWithDrawInProccessing
        data = request.DATA
        if not data:
            raise ParamError

        for field in data:
            value = data.get(field)
            if value is None:
                continue
            self.media_account.payment_info[field] = value
        self.media_account.save()
        return RESPONSE_OK


class MediaSettings(CheckDuplicatedTitleMixin, BaseView):

    def get(self, request):
        return MediaSettingInfoSerializer(self.media_account).data

    def put(self, request):
        data = request.DATA
        if not data:
            raise ParamError
        if not self.media_account.verify_passed:
            raise ParamError

        if not self.media_account.last_modified_at:
            last_modified_at = self.media_account.id.generation_time
        else:
            last_modified_at = self.media_account.last_modified_at

        import pytz
        last_modified_at = last_modified_at.replace(tzinfo=pytz.UTC)
        now = datetime.datetime.utcnow()
        deadline = (now - datetime.timedelta(seconds=MEDIA_CHANGE_SETTING_TIME)).replace(tzinfo=pytz.UTC)
        if last_modified_at >= deadline:
            raise InvalidMediaInfoUpdateFrequence

        for field in data:
            if field in UNMODIFIABLE_FIELDS:
                raise InvalidUpdateMediaField

        for field in data:
            if field not in NEED_REVERIFIED_FIELDS:
                raise InvalidUpdateMediaField
        title = data.get('title')
        if title:
            self.check_duplicated_title(title)
        for key in NEED_REVERIFIED_FIELDS:
            value = data.get(key)
            value = value if value else getattr(self.media_account, key, None)
            setattr(self.media_account, 'new_%s' % key, value)
        self.media_account.info_update = True
        self.media_account.last_modified_at = now
        self.media_account.save()
        return RESPONSE_OK

class MediaCheckInfoView(CheckDuplicatedTitleMixin, View):
    def post(self, request):
        data = request.DATA
        if not data:
            raise ParamError
        title = data.get('title')
        if title:
            unformatted_title = self.check_duplicated_title(title)
        user_pan_no = data.get('user_pan_no')
        if user_pan_no:
            reach_limit = MediaAccount.check_pan_no_reach_limit(user_pan_no)
            if reach_limit:
                raise MediaPanNumRelatedTooMuch
            is_black_pan_no = MediaAccount.check_pan_no_is_black(user_pan_no)
            if is_black_pan_no:
                raise MediaPanIsBlack
        return RESPONSE_OK

class MediaIncomes(StatPagerMixin, BaseView):

    def get(self, request):
        page_params, order, reverse, count = gen_page_query_params(request)
        start_time, end_time, count = self.process_get_params(request)
        params = {'site_url': self.media_account.site_url, 'start_date__gte': str(start_time.date()),
                'end_date__lt': str(end_time.date())}
        params.update(page_params)
        weekly_incomes, has_next_page = gen_current_page_items(WeeklyMediaIncome, params, order, reverse, count)
        return gen_page_response([WeeklyIncomeSerializer(wi).data for wi in weekly_incomes],
                has_next_page)


class MediaStatisticsView(BaseView):

    def get(self, request):
        syncing_finished = stat_utils.has_showing_data_synced()
        if not syncing_finished:
            return {
                    'fans_count': None, 'read_count': None, 'total_revenue': None,
                    'revenue_update_date': None
                }

        follow_count, read_count = stat_utils.get_rt_media_showable_data(str(self.media_account.id))

        return {
                'fans_count': follow_count, 'read_count': read_count,
                'total_revenue': round(stat_utils.normalize_count(self.media_account.total_revenue), 2),
                'revenue_update_date': self.media_account.revenue_update_date
            }

class PlatformAnnouncement(BaseView):
    def get(self, request):
        params = {}
        type = int(request.GET.get('type') or 0)
        if not type in ANN_TYPE_MAPPING:
            raise ParamError
        params['type'] = type
        page_params, order, reverse, count = gen_page_query_order_modified_time(request, 20)
        params['status'] = ANN_STATUS_USABLE
        params.update(page_params)
        announcements, has_next_page = gen_current_page_items(Announcement, params, order, reverse, count)
        return gen_page_response([AnnouncementSerializer(ann).data for ann in announcements], has_next_page)

class AnnouncementDetailsView(BaseView):
    def get(self, request, ann_id):
        ann = Announcement.objects(id=ann_id, status=ANN_STATUS_USABLE).first()
        if not ann:
            raise AnnouncementNotExist
        return AnnouncementSerializer(ann).data

class MediaBonus(StatPagerMixin, BaseView):
    def get(self, request):
        page_params, order, reverse, count = gen_page_query_params(request)
        start_time, end_time, count = self.process_get_params(request)
        start_time -= INDIA_TIME_DELTA
        end_time -= INDIA_TIME_DELTA
        params = {'media_id': self.media_id, 'create_at__gte': start_time, 'create_at__lt': end_time}
        params.update(page_params)
        bonus, has_next_page = gen_current_page_items(Bonus, params, order, reverse, count)
        return gen_page_response([BonusSerializer(bn).data for bn in bonus],
                has_next_page)


class PromotionView(BaseView):

    def get(self, request):
        media = request.user.get_related_media_account()
        mpu = MediaPromotionUser.objects(media_id=str(media.id)).first()
        if not mpu:
            raise MediaPcodeNotExist
        return PromotionUserSerializer(mpu).data

class PromotionLogView(BaseView):

    def get(self, request):
        media = request.user.get_related_media_account()
        params = {}
        page_params, order, reverse, count = gen_page_query_params(request, 20)
        params['father_media_id'] = str(media.id)
        params.update(page_params)
        mpls, has_next_page = gen_current_page_items(MediaPromotionLog, params, order, reverse, count)
        wrap_medianame = MediaNameGenerator(mpls)
        return gen_page_response([wrap_medianame(PromotionLogSerializer(mpl)).data for mpl in mpls], has_next_page)
