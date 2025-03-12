#################################################################
# 文件: trackingapp/apps.py
#################################################################
from django.apps import AppConfig

class TrackingappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trackingapp'

    def ready(self):
        import trackingapp.signals  # 用于登录日志等信号处理
