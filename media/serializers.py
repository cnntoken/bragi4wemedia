# -*- coding: utf-8 -*-

from corelib.serializers import Serializer
from corelib.time import datetime2india_timestr

from media.models import MediaAccount
from media.consts import UNMODIFIABLE_FIELDS, NEED_REVERIFIED_FIELDS, BN_TYPE_INC

from comments.models import CommentMediaInfo

class MediaNameGenerator(object):
    def __init__(self, objects):
        if objects:
            media_ids = [ob.media_id for ob in objects]
            medias = MediaAccount.objects(id__in=media_ids)
            self.media_name_mapping = dict((str(media.id), media.title) for media in medias)
        else:
            self.media_name_mapping = None

    def __call__(self, serializer_item):
        if self.media_name_mapping is None:
            return serializer_item
        media_name = self.media_name_mapping.get(str(serializer_item.query_set.media_id), False)
        serializer_item.query_set.media_name = media_name
        return serializer_item

class MediaCommentPermissionGenerator(object):
    def __init__(self, media_accounts):
        if media_accounts:
            media_ids = [str(media.id) for media in media_accounts]
            media_comment_infos = CommentMediaInfo.objects(media_id__in=media_ids, usable=True)
            comments_infos = set([info.media_id for info in media_comment_infos])
            self.media_permission_mapping = {str(ma.id): (str(ma.id) in comments_infos) for ma in media_accounts}
        else:
            self.media_permission_mapping = {}

    def __call__(self, serializer_item):
        comment_permission_func = lambda: self.media_permission_mapping.get(str(serializer_item.query_set.id), False)
        print comment_permission_func
        serializer_item.comment_permission = comment_permission_func
        return serializer_item

class MediaSerializer(Serializer):
    pass

class MediaCompactSyncSerializer(MediaSerializer):
    def _get_data(self):
        info = dict(
            site_url=self.query_set.site_url,
            site_name=self.query_set.title,
            media_icon=self.query_set.icon,
            valid_duration=self.query_set.valid_duration * 3600 * 24
            )
        return info

class MediaSettingInfoSerializer(MediaSerializer):

    @property
    def last_modified_time(self):
        return datetime2india_timestr(self.query_set.last_modified_at)

    @property
    def updated_time(self):
        return datetime2india_timestr(self.query_set.updated_at)

    @property
    def checked_time(self):
        return datetime2india_timestr(self.query_set.checked_at)

    def get_origin_data(self):
        origin_data = self.query_set._data
        data = {}
        for key in UNMODIFIABLE_FIELDS:
            value = origin_data.get(key)
            if value is not None:
                data[key] = value
        for key in NEED_REVERIFIED_FIELDS:
            show_key = key if not self.query_set.info_update else 'new_%s' % key
            value = origin_data.get(show_key)
            if value is not None:
                data[key] = value
        return data

    def _get_data(self):
        data = self.get_origin_data()
        data.update(dict(id=str(self.query_set.id),
            last_modified_at=self.last_modified_time,
            checked_at=self.checked_time,
            updated_at=self.updated_time))
        return data

class AdminMediaInfoSerializer(MediaSettingInfoSerializer):

    @property
    def create_time(self):
        return datetime2india_timestr(self.query_set.create_at)


    def comment_permission(self):
        pass

    def get_origin_data(self):
        origin_data = self.query_set._data
        origin_data['create_time'] = self.create_time
        origin_data.pop('create_at')
        if self.query_set.limit_end_at:
            origin_data['limit_end_at'] = self.query_set.limit_end_at.strftime('%Y-%m-%d %H:%M')
        permission = self.comment_permission()
        if not permission is None:
            origin_data['comment_permission'] = self.comment_permission()
        return origin_data

class AnnouncementSerializer(MediaSerializer):

    @property
    def published_time(self):
        return datetime2india_timestr(self.query_set.published_at)

    def _get_data(self):
        info = dict(
            id=str(self.query_set.id),
            title=self.query_set.title,
            content=self.query_set.content,
            published_at=self.published_time,
            )
        return info

class AdminAnnouncementSerializer(AnnouncementSerializer):

    @property
    def modified_time(self):
        return datetime2india_timestr(self.query_set.modified_at)

    def _get_data(self):
        data = super(AdminAnnouncementSerializer, self)._get_data()
        data['modified_at'] = self.modified_time
        data['user_email'] = self.query_set.user_email
        return data

class WithDrawSerializer(MediaSerializer):
    @property
    def create_time(self):
        return datetime2india_timestr(self.query_set.create_at)

    def _get_data(self):
        info = dict(
                id=str(self.query_set.id),
                create_at=self.create_time,
                amount=self.query_set.amount,
                status=self.query_set.status,
                )
        return info

class AdminWithDrawSerializer(WithDrawSerializer):
    @property
    def operate_time(self):
        return datetime2india_timestr(self.query_set.operate_at)

    @property
    def media_name(self):
        # TODO: multi fetch
        from media.models import MediaAccount
        ma = MediaAccount.objects.with_id(self.query_set.media_id)
        if not ma:
            return None
        return ma.title

    def _get_data(self):
        data = super(AdminWithDrawSerializer, self)._get_data()
        data['payment_info'] = self.query_set.payment_info
        data['operator_email'] = self.query_set.operator_email
        data['operate_time'] = self.operate_time
        data['media_name'] = self.media_name
        return data


class WeeklyIncomeSerializer(MediaSerializer):
    def _get_data(self):
        info = dict(
                id=str(self.query_set.id),
                start_date=self.query_set.start_date,
                end_date=self.query_set.end_date,
                revenue=self.query_set.revenue,
                )
        return info

class BonusSerializer(MediaSerializer):
    @property
    def create_time(self):
        return datetime2india_timestr(self.query_set.create_at)

    @property
    def amount(self):
        if self.query_set.type == BN_TYPE_INC:
            return round(self.query_set.amount, 2)
        return round(-1*self.query_set.amount, 2)

    def _get_data(self):
        info = dict(
                id=str(self.query_set.id),
                create_time=self.create_time,
                amount=self.amount,
                reason=self.query_set.reason,
                )
        return info

class AdminBonusSerializer(BonusSerializer):

    def _get_data(self):
        data = super(AdminBonusSerializer, self)._get_data()
        data['operator_email'] = self.query_set.operator_email
        return data

class AdminOperateLogSerializer(MediaSerializer):

    @property
    def operate_time(self):
        return datetime2india_timestr(self.query_set.operate_at)

    def _get_data(self):
        info = dict(
                id=str(self.query_set.id),
                media_id=self.query_set.media_id,
                operator_id=self.query_set.operator_id,
                operate_type=self.query_set.operate_type,
                operate_time=self.operate_time,
                operate_content=self.query_set.operate_content,
                operator_email=self.query_set.operator_email
                )
        return info

class PromotionUserSerializer(MediaSerializer):
    def _get_data(self):
        info = dict(
                id=str(self.query_set.id),
                media_id=self.query_set.media_id,
                status=self.query_set.status,
                promotion_code=self.query_set.promotion_code,
                time_reached=self.query_set.time_reached,
                read_reached=self.query_set.read_reached,
                no_banned=self.query_set.no_banned,
                )
        return info

class PromotionLogSerializer(MediaSerializer):
    def _get_data(self):
        info = dict(
                id=str(self.query_set.id),
                media_id=self.query_set.media_id,
                father_media_id=self.query_set.father_media_id,
                get_bonus=self.query_set.get_bonus,
                bonus_amount=self.query_set.bonus_amount,
                media_name=self.query_set.media_name,
                )
        return info
