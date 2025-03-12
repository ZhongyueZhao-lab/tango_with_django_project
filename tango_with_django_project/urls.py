#################################################################
# 文件: student_tracking_system/urls.py
#################################################################
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('trackingapp.urls')),
]
