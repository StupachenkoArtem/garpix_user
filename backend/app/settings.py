"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path
from environs import Env

from garpix_auth.settings import EMAIL_CONFIRMATION_EVENT, EMAIL_CONFIRMATION_EVENT_ITEM  # noqa
from garpix_auth.settings import PHONE_CONFIRMATION_EVENT, PHONE_CONFIRMATION_EVENT_ITEM  # noqa
from garpix_auth.settings import EMAIL_RESTORE_PASSWORD_EVENT, EMAIL_RESTORE_PASSWORD_EVENT_ITEM  # noqa
from garpix_auth.settings import PHONE_RESTORE_PASSWORD_EVENT, PHONE_RESTORE_PASSWORD_EVENT_ITEM  # noqa

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

SITE_URL = os.getenv('SITE_URL')

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'public', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'public', 'media')

TEMPLATES_PATH = os.path.join(BASE_DIR, '..', 'frontend', 'templates')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..', 'frontend', 'static'),
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', True)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'user',
    'garpix_auth',
    'garpix_qa',
    'ckeditor',
    'celery',
    # for auth
    'rest_framework',
    'rest_framework.authtoken',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
    'drf_multiple_model',
    'drf_spectacular',
    # for notify
    'fcm_django',
    'garpix_notify',
    'solo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            TEMPLATES_PATH
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env.int('POSTGRES_PORT'),
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# garpix_auth

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'garpix_auth.rest.authentication.MainAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    )
}

AUTHENTICATION_BACKENDS = (
    # Only your social networks
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.facebook.FacebookAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    # Django
    'rest_framework_social_oauth2.backends.DjangoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details'
)

# GARPIX_ACCESS_TOKEN_TTL_SECONDS = 86400  # 24 hours
GARPIX_ACCESS_TOKEN_TTL_SECONDS = 0  # infinity
# GARPIX_ACCESS_TOKEN_TTL_SECONDS = 86400 * 14  # 14 days
GARPIX_REFRESH_TOKEN_TTL_SECONDS = 0  # infinity

MIGRATION_MODULES = {
    'garpix_auth': 'app.migrations.garpix_auth',
    'garpix_notify': 'app.migrations.garpix_notify',
}


NOTIFY_EVENTS = {}

NOTIFY_EVENTS.update(PHONE_CONFIRMATION_EVENT_ITEM)
NOTIFY_EVENTS.update(EMAIL_CONFIRMATION_EVENT_ITEM)

NOTIFY_EVENTS.update(PHONE_RESTORE_PASSWORD_EVENT_ITEM)
NOTIFY_EVENTS.update(EMAIL_RESTORE_PASSWORD_EVENT_ITEM)

CHOICES_NOTIFY_EVENT = [(k, v['title']) for k, v in NOTIFY_EVENTS.items()]

GARPIX_CONFIRM_CODE_LENGTH = 6
GARPIX_TIME_LAST_REQUEST = 1
GARPIX_CONFIRM_PHONE_CODE_LIFE_TIME = 5  # in minutes
GARPIX_CONFIRM_EMAIL_CODE_LIFE_TIME = 2  # in days

GARPIX_USE_PREREGISTRATION_PHONE_CONFIRMATION = False

GARPIX_USE_PREREGISTRATION_EMAIL_CONFIRMATION = False

GARPIX_USER_USERSESSION_MIXIN = "user.models.user_session_mixin.UserSessionMixin"

AUTH_USER_MODEL = 'user.User'

# ckeditor

CKEDITOR_UPLOAD_PATH = ''

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'width': '100%',
    },
}