#################################################################
# 文件: student_tracking_system/settings.py
#################################################################
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

#通过环境变量加载 SECRET_KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-please_replace_with_your_own_secret_key')

DEBUG = True

ALLOWED_HOSTS = []

import pymysql
pymysql.install_as_MySQLdb()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'trackingapp',  # 注册自定义app
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'student_tracking_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'trackingapp', 'templates')],
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

WSGI_APPLICATION = 'student_tracking_system.wsgi.application'

# 数据库使用MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mydatabase',
        'USER': 'zhongyuezhao',
        'PASSWORD': '123456',
        'HOST': '130.209.157.51',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',  # 让 MySQL 支持 utf8mb4 编码
        },
    }
}

# 使用自定义User模型 8
AUTH_USER_MODEL = 'trackingapp.User'

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 静态文件
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'trackingapp', 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email 配置：使用 QQ 邮箱 SMTP 服务器
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

# QQ邮箱配置
EMAIL_HOST_USER = '2082393264@qq.com'
EMAIL_HOST_PASSWORD = 'hdiimrnidrzmcjbh'

# 让登录后跳转到主页
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

INSTALLED_APPS += ["dbbackup"]  # 添加 dbbackup

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": "/Users/zhaozhongyue/Desktop/backup"}


