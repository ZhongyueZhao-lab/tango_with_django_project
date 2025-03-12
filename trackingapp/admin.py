#################################################################
# 文件: trackingapp/admin.py
#################################################################
from django.contrib import admin
from .models import User, Course, Announcement, AttendanceRecord, Grade, LoginLog

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'email', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'teacher', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'is_global', 'created_at', 'valid_until')
    list_filter = ('is_global', 'created_at')
    search_fields = ('title', 'creator__username')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status')
    list_filter = ('course', 'date', 'status')
    search_fields = ('student__username', 'course__code')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'homework_score', 'exam_score', 'practice_score', 'total_score')

@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time')
    list_filter = ('login_time',)
    search_fields = ('user__username',)
