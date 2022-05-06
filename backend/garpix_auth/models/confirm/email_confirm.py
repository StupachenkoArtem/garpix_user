import string
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text

from rest_framework import serializers

from garpix_notify.models import Notify
from garpix_utils.string import get_random_string

GARPIX_CONFIRM_CODE_LENGTH = getattr(settings, 'GARPIX_CONFIRM_CODE_LENGTH', 6)
GARPIX_CONFIRM_EMAIL_CODE_LIFE_TIME = getattr(settings, 'GARPIX_CONFIRM_EMAIL_CODE_LIFE_TIME', 6)
GARPIX_TIME_LAST_REQUEST = getattr(settings, 'GARPIX_TIME_LAST_REQUEST', 1)


class UserEmailConfirmMixin(models.Model):
    """
    Миксин для подтверждения email после регистрации
    """
    is_email_confirmed = models.BooleanField(default=False, verbose_name="Email подтвержден")
    email_confirmation_code = models.CharField(max_length=15, verbose_name='Код подтверждения email',
                                               blank=True, null=True)
    new_email = models.EmailField(blank=True, null=True, verbose_name="Новый email")

    # Подтверждение после регистрации

    def send_email_confirmation_code(self, email=None):
        User = get_user_model()

        if not email:
            email = self.email

        anybody_have_this_email = User.objects.filter(email=email, is_email_confirmed=True).count() > 0

        if not anybody_have_this_email.exists() or anybody_have_this_email == self:
            confirmation_code = get_random_string(GARPIX_CONFIRM_CODE_LENGTH, string.digits)

            self.email = self.new_email
            self.email_confirmation_code = confirmation_code

            Notify.send(settings.EMAIL_CONFIRMATION_EVENT, {
                'confirmation_code': confirmation_code
            }, email=email)

            return {"result": True}

        return {"result": False, "message": "User with such email already exists"}

    def check_email_confirmation_code(self, email_confirmation_code):

        time_is_up = (datetime.now(
            timezone.utc) - self.updated_at).days > GARPIX_CONFIRM_EMAIL_CODE_LIFE_TIME

        if time_is_up:
            return {"result": False, "message": "Code has expired"}

        if self.email_confirmation_code != email_confirmation_code:
            return {"result": False, "message": "Code is incorrect"}

        self.is_email_confirmed = True
        self.email = self.new_email
        self.save()
        return {"result": True}

    class Meta:
        abstract = True


class UserEmailPreConfirmMixin(models.Model):
    """
    Миксин для подтверждения email до регистрации
    """
    is_email_confirmed = models.BooleanField(default=False, verbose_name="Email подтвержден")
    email_confirmation_code = models.CharField(max_length=255, verbose_name="Код подтверждения email", blank=True,
                                               null=True)
    token = models.CharField(max_length=40, verbose_name="Токен", blank=True,
                             null=True)
    email_code_send_date = models.DateTimeField(auto_now=True, verbose_name="Дата изменения", blank=True, null=True)
    new_email = models.EmailField(blank=True, null=True, verbose_name="Новый email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    # Подтверждение до регистрации c помощью кода:
    @classmethod
    def send_confirmation_code(cls, email):
        User = get_user_model()

        anybody_have_this_email = User.objects.filter(email=email, is_email_confirmed=True).count() > 0
        if not anybody_have_this_email:
            email_confirmation_instance = cls.objects.filter(email=email).first() or cls(email=email)
            confirmation_code = get_random_string(GARPIX_CONFIRM_CODE_LENGTH, string.digits)

            if not email_confirmation_instance.updated_at or email_confirmation_instance.updated_at + timedelta(
                    minutes=GARPIX_TIME_LAST_REQUEST) < datetime.now(
                email_confirmation_instance.email_code_send_date.tzinfo):
                email_confirmation_instance.email = email
                email_confirmation_instance.email_confirmation_code = confirmation_code
                email_confirmation_instance.token = uuid4()

                Notify.send(settings.EMAIL_CONFIRMATION_EVENT, {
                    'confirmation_key': confirmation_code
                }, email=email)

                try:
                    email_confirmation_instance.clean()
                except ValidationError as e:
                    return serializers.ValidationError(e)
                email_confirmation_instance.check_date = datetime.now(timezone.utc)
                email_confirmation_instance.save()
                email_confirmation_instance.username = 'not_confirmed_user_' + f'{email_confirmation_instance.id}'
                email_confirmation_instance.save()
                return {"result": True}
            else:
                return {"result": False, "message": _(f"Не прошло {GARPIX_TIME_LAST_REQUEST} мин с последней отправки")}

        return {"result": False, "message": _("Пользователь с таким email уже зарегистрирован")}

    @classmethod
    def check_confirmation_code(cls, email, email_confirmation_code):
        email_confirmation_instance = cls.objects.filter(email=email,
                                                         email_confirmation_code=email_confirmation_code).first()

        if not email_confirmation_instance:
            return {"result": False, "message": _("Неверный код или email")}

        time_is_up = (datetime.now(
            email_confirmation_instance.email_code_send_date.tzinfo) - email_confirmation_instance.email_code_send_date).seconds / 60 > GARPIX_CONFIRM_EMAIL_CODE_LIFE_TIME

        if time_is_up:
            return {"result": False, "message": _("Код недействителен. Запросите повторно")}

        email_confirmation_instance.is_email_confirmed = True
        email_confirmation_instance.save()
        return {"result": True}

    @classmethod
    def check_confirmation(cls, email, user):
        """
         Метод проверяет, подтвержден ли email пользователем
         """
        if cls.objects.filter(email=email, is_email_confirmed=True, token=user.token).first():
            return True
        return False

    class Meta:
        abstract = True
