import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv
from celery.schedules import crontab



BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')

if ENVIRONMENT == 'production':
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE'),
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT'),
        }
    }
else:
    # لوکال با SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.environ.get('SQLITE_DB_NAME', 'db.sqlite3'),
        }
    }




SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'user',
    'jdatetime',
    'django_jalali',
    'django_ckeditor_5',
    'storages',
    'django_celery_beat',
    'django_celery_results',
    'import_export',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'templates',
    'report_app',
    'comment_app',
    'django.contrib.humanize' ,
    'section',
    'adminsortable2',
    'ckeditor',
    'django_pwned_passwords',

]


CRON_CLASSES = [
    'user.cron.EveningGreetingCronJob',
]


SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'website.middleware.rate_limit.RateLimitMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]



ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # این خط بسیار مهم است
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'report_app.context_processors.unread_message_count',

            ],
        },
    },
]





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




LANGUAGE_CODE = 'fa'

TIME_ZONE =  'Africa/Khartoum'

USE_I18N = True

USE_L10N= True

USE_TZ = True




STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = 'static/'



AUTH_USER_MODEL = 'user.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]




GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


SITE_ID = 1



SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True')== 'True'
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# توکن امن با نصب پکیج itsdangerous


SMS_IR_API_KEY = os.getenv("SMS_IR_API_KEY")
SMS_IR_LINE_NUMBER = os.getenv("SMS_IR_LINE_NUMBER")
SMS_IR_TEMPLATE_ID = os.getenv("SMS_IR_TEMPLATE_ID")


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = Path('/home/fhmmeuob/public_html/ftm.erfann31dev.ir/logs')
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'simple': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
    },

    'handlers': {
        'user_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'user.log'),
            'formatter': 'simple',
        },
        'report_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'report_app.log'),
            'formatter': 'simple',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'comment_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'comment_app.log'),
            'formatter': 'simple',
        },
        'section_file': {
             'level': 'INFO',
             'class': 'logging.FileHandler',
             'filename': str(LOG_DIR / 'section_app.log'),
            'formatter': 'simple',
        },
        'ratelimit_file': {
            'level': 'INFO',  # یا DEBUG اگر می‌خوای لاگ‌های دقیق‌تر ثبت شه
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'ratelimit.log'),
            'formatter': 'simple',
        },
        'moderator_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'moderator_admin.log'),  # مسیر فایل لاگ
            'formatter': 'simple',
        },
        'email_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'email.log'),  # مطمئن شو این مسیر وجود داره
            'formatter': 'simple',
        },

    },

    'loggers': {
        'user': {
            'handlers': ['user_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'report': {
            'handlers': ['report_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'comment': {
             'handlers': ['comment_file'],
             'level': 'INFO',
             'propagate': False,
        },
        'section': {
            'handlers': ['section_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'ratelimit': {
            'level': 'INFO',  # یا DEBUG
            'handlers': ['ratelimit_file'],
            'propagate': False,
        },
        'moderator_admin': {
            'handlers': ['moderator_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['email_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}



ARVAN_ACCESS_KEY = config("ARVAN_ACCESS_KEY")
ARVAN_SECRET_KEY = config("ARVAN_SECRET_KEY")
ARVAN_BUCKET = config("ARVAN_BUCKET")
ARVAN_ENDPOINT = config("ARVAN_ENDPOINT")

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-celery-results'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran'
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULE = {
    'send-good-evening-email-daily': {
        'task': 'your_app.tasks.send_good_evening_email_task', # مسیر کامل تسک شما
        'schedule': crontab(hour=15, minute=0), # 15:00 UTC = 18:00 Khartoum (UTC+3)
        'args': (),
        'kwargs': {},
        'options': {'queue': 'default'}
    },
}





CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # دیتابیس ۱
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False

LOGIN_REDIRECT_URL = "/home"


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    }
}

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']

AUTH_USER_MODEL = 'user.CustomUser'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
