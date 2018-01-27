# -*- coding: utf-8 -*-

from django_mongoengine.mongo_auth.models import User as MongoEngineUser

from corelib.store import Document, StringField, DictField, BooleanField, ListField

class User(MongoEngineUser):
    user_type = StringField()
    email_verified = BooleanField()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['user_type']

    @classmethod
    def gen_email_username(cls, email):
        return 'm_%s' % email

    def has_password(self):
        if not self.user_type == 'email' and self.email is None:
            return False
        return True

    @classmethod
    def check_joined(cls, username):
        u = cls.objects(username=username).only('id').first()
        if not u:
            return False
        return True

    def load_user_profile(self):
        up = UserProfile.objects(user_id=str(self.id)).first()
        if not up:
            return None
        self._up = up
        return up

    def create_user_profile(self, **kwargs):
        up = self.get_user_profile()
        if up is None:
            up = UserProfile(user_id=str(self.id))
        for key, value in kwargs.iteritems():
            setattr(up, key, value)
        up.save()

    def get_user_profile(self):
        up = getattr(self, '_user_profile', None)
        if up:
            return up
        up = self.load_user_profile()
        setattr(self, '_user_profile', up)
        return up

    @classmethod
    def get_user_by_email(cls, email):
        user_name = User.gen_email_username(email)
        user = cls.objects(username=user_name).first()
        return user

    def update_user_profile(self, **kwargs):
        up = self.get_user_profile()
        for key, value in kwargs.iteritems():
            setattr(up, key, value)
        up.save()

    def get_related_media_account(self, god_view=False, mid=None):
        media_account = getattr(self, '_media_account', None)
        if media_account:
            return media_account
        from media.models import MediaAccount
        if god_view and mid:
            media_account = MediaAccount.objects.with_id(mid)
        else:
            media_account = MediaAccount.objects(user_id=str(self.id)).first()
        setattr(self, '_media_account', media_account)
        return media_account

    def is_email_user(self):
        return self.user_type == 'email'

    @property
    def media_account(self):
        return self.get_related_media_account()

    @property
    def comment_permission(self):
        media = self.get_related_media_account()
        from comments.models import CommentMediaInfo
        comment_media = CommentMediaInfo.objects(media_id=str(media.id)).first()
        if comment_media and comment_media.usable:
            return True
        return False

    @property
    def account_name(self):
        media_account = self.get_related_media_account()
        if not media_account:
            if self.is_email_user():
                return self.email
            else:
                up = self.get_user_profile()
                if not up:
                    return None
                return up.accounts.get('fb', {}).get('name')
        return media_account.title

    @property
    def account_icon(self):
        media_account = self.get_related_media_account()
        if not media_account:
            return ''
        return media_account.icon

    def has_permission(self, request_path):
        if self.is_superuser:
            return True
        normalized_request_path = request_path.replace('/admin/', '').split('/')[0]
        normalized_request_path = '/admin/%s/' % normalized_request_path
        return normalized_request_path in self.permissions_list

    @property
    def permissions_list(self):
        up = self.get_user_profile()
        return up.permissions

    def set_permission(self, urls):
        self.update_user_profile(permissions=urls)

class UserProfile(Document):
    user_id = StringField()
    accounts = DictField()
    permissions = ListField(StringField())
