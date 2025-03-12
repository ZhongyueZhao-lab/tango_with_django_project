import os
import dj_database_url
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 通过环境变量加载 SECRET_KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-please_replace_with_your_own_secret_key')

# 设置 DEBUG，默认为 False（在 Railway 设置环境变量 DEBUG=True 可启用调试模式）
DEBUG = os.environ.get("DEBUG", "False") == "True"

# 允许所有主机访问（生产环境建议使用具体域名）
ALLOWED_HOSTS = ["*"]

# 安装 MySQL 适配
import pymysql
pymysql.install_as_MySQLdb()

# 已安装的 Django 应用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'trackingapp',  # 自定义应用
    'dbbackup',  # 数据库备份
]

# 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 处理静态文件
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL 配置
ROOT_URLCONF = 'student_tracking_system.urls'

# 模板配置
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

# WSGI 配置
WSGI_APPLICATION = 'student_tracking_system.wsgi.application'

# 🚀 **数据库配置：自动检测 MySQL 或 PostgreSQL**
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'mydatabase'),
            'USER': os.environ.get('MYSQL_USER', 'zhongyuezhao'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', '123456'),
            'HOST': os.environ.get('MYSQL_HOST', '130.209.157.51'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }

# 自定义用户模型
AUTH_USER_MODEL = 'trackingapp.User'

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 语言和时区
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 🚀 **静态文件配置**
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Railway 需要 STATIC_ROOT
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'trackingapp', 'static')]

# 🚀 **邮件配置（使用环境变量存储密码）**
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = '2082393264@qq.com'
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")  # 不要硬编码密码！

# 🚀 **登录和登出跳转**
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# 🚀 **数据库备份**
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": os.environ.get("DB_BACKUP_PATH", "/Users/zhaozhongyue/Desktop/backup")}

# 🚀 **生产环境优化**
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
