# your_project/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config # Keep this if you are using 'decouple.config' for ARVAN_ACCESS_KEY. If not, remove 'decouple' import and 'config' calls.
from celery.schedules import crontab


BASE_DIR = Path(__file__).resolve().parent.parent

# --- Fix 1: Load environment variables only once from .env file ---
load_dotenv(os.path.join(BASE_DIR, '.env'))


ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')

if ENVIRONMENT == 'production':
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT', '5432'),
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
# --- Fix 2: Ensure DEBUG is correctly converted to a boolean ---
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
# --- Fix 3: Clean ALLOWED_HOSTS list from empty strings ---
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',

    # Your custom apps
    'user',
    'sms',
    'Email',
    'report_app',
    'comment_app',
    'section',

    # Third-party apps
    'jdatetime',
    'django_jalali',
    'django_ckeditor_5',
    'storages',
    'django_celery_beat',
    'django_celery_results',
    'import_export',
    'adminsortable2',

    # Allauth related apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # 'templates', # Removed (not a Django app)
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
    'social_django.middleware.SocialAuthExceptionMiddleware', # Keep if you are using python-social-auth
]


ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'report_app.context_processors.unread_messages_count',
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

# --- Changed TIME_ZONE to Asia/Tehran as requested ---
TIME_ZONE = 'Asia/Tehran'

USE_I18N = True
# USE_L10N= True # Removed (deprecated in Django 4.0+)
USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, 'static_root') # Changed to static_root for clarity
STATIC_URL = 'static/'


AUTH_USER_MODEL = 'user.CustomUser' # Ensure this is defined only once

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


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
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true' # Ensure boolean conversion
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

SMS_IR_API_KEY = os.getenv("SMS_IR_API_KEY")
SMS_IR_LINE_NUMBER = os.getenv("SMS_IR_LINE_NUMBER")
SMS_IR_TEMPLATE_ID = os.getenv("SMS_IR_TEMPLATE_ID") # Corrected env var name


# --- Fix 14: Ensure LOGS_DIR is defined BEFORE the LOGGING dictionary ---
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} ({name}:{lineno}) ▶ {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_all_logs': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'all_project.log'), # LOGS_DIR used here
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file_all_logs'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'INFO',
            'propagate': False,
        },
        'user': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'comment_app': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'report_app': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'website': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'Email': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'sms': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'file_all_logs'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}


ARVAN_ACCESS_KEY = config("ARVAN_ACCESS_KEY") # Keep if using decouple, else change to os.getenv
ARVAN_SECRET_KEY = config("ARVAN_SECRET_KEY") # Keep if using decouple, else change to os.getenv
ARVAN_BUCKET = config("ARVAN_BUCKET")         # Keep if using decouple, else change to os.getenv
ARVAN_ENDPOINT = config("ARVAN_ENDPOINT")     # Keep if using decouple, else change to os.getenv


REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB_CELERY = int(os.getenv('REDIS_DB_CELERY', 0)) # For Celery broker
REDIS_DB_CACHE = int(os.getenv('REDIS_DB_CACHE', 1)) # For Django cache

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_CELERY}"
CELERY_RESULT_BACKEND = 'django-celery-results'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran' # Consistent with Django's TIME_ZONE
CELERY_ENABLE_UTC = True

CELERY_BEAT_SCHEDULE = {
    'send-good-evening-email-daily': {
        'task': 'user.tasks.send_good_evening_email_task', # Correct task path
        'schedule': crontab(hour=15, minute=0), # 15:00 UTC = 18:00 Khartoum time (UTC+3)
        'args': (),
        'kwargs': {},
        'options': {'queue': 'default'}
    },
}


# --- Fix 15: Corrected CACHES configuration (no duplicate backends) ---
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_CACHE}",
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

# REDIS_HOST, REDIS_PORT, REDIS_DB are now handled by REDIS_DB_CELERY and REDIS_DB_CACHE

# TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates'] # Redundant as it's defined in TEMPLATES list above.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', '|', 'imageUpload', 'undo', 'redo'],
    },
}