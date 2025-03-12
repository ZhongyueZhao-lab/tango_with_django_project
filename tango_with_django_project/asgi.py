#################################################################
# 文件: student_tracking_system/asgi.py
#################################################################
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_tracking_system.settings')
application = get_asgi_application()
