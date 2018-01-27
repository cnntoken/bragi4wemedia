# -*- coding: utf-8 -*-


from django.contrib import auth
from django.views.generic import View

from corelib.verification.models import VerificationCode
from corelib.response import RESPONSE_OK
from accounts.models import User
from accounts.helpers import jump2media_page
from accounts.exception import (UserNotExist, HasLogin, EmailHasUsed, VerficationCodeUnusable,
        HasPassword, HasNoPassword, OldPasswordError, EmailNotExist)
from corelib.async_mail import send_verification_mail, send_reset_password_mail

class AuthView(View):

    def gen_username(self, email):
        return User.gen_email_username(email)

class LoginView(AuthView):

    def post(self, request):
        if not request.user.is_anonymous():
            raise HasLogin
        email = request.DATA.get('email')
        password = request.DATA.get('password')
        if not email or not password:
            raise UserNotExist
        email = email.lower().strip()
        user = auth.authenticate(username=self.gen_username(email), password=password)
        if not user:
            raise UserNotExist
        if not user.is_active:
            raise UserNotExist
        auth.login(request, user)
        return {'msg': str(request.user.id), 'redirect': jump2media_page(user)}
