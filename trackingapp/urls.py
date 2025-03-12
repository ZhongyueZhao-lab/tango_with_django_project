#################################################################
# 文件: trackingapp/urls.py
#################################################################
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    home_view,
    register_view,
    custom_login_view,
    verify_mfa_view,

    dashboard_admin_view,
    dashboard_teacher_view,
    dashboard_student_view,
    role_dashboard_redirect_view,

    manage_courses_view,
    manage_course_detail_view,

    announcement_list_view,
    announcement_detail_view,
    create_announcement_view,
    edit_announcement_view,
    delete_announcement_view,

    attendance_list_view,
    mark_attendance_view,
    generate_qr_code_view,
    scan_qr_code_view,
    checkin_view,

    grade_report_view,
    system_report_view,

    profile_view,

    # 新增功能
    system_settings_view,
    export_report_view,
    import_grades_view,
    teacher_analysis_view,
)

urlpatterns = [
    # 主页 + 注册/登录/登出 + MFA
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('verify-mfa/', verify_mfa_view, name='verify_mfa'),

    # 角色Dashboard
    path('dashboard/', role_dashboard_redirect_view, name='dashboard'),
    path('admin-dashboard/', dashboard_admin_view, name='dashboard_admin'),
    path('teacher-dashboard/', dashboard_teacher_view, name='dashboard_teacher'),
    path('student-dashboard/', dashboard_student_view, name='dashboard_student'),

    path('profile/', profile_view, name='profile'),

    # 课程管理
    path('courses/', manage_courses_view, name='manage_courses'),
    path('courses/<int:course_id>/', manage_course_detail_view, name='manage_course_detail'),

    # 公告管理
    path('announcements/', announcement_list_view, name='announcement_list'),
    path('announcements/create/', create_announcement_view, name='create_announcement'),
    path('announcements/<int:pk>/', announcement_detail_view, name='announcement_detail'),
    path('announcements/<int:pk>/edit/', edit_announcement_view, name='edit_announcement'),
    path('announcements/<int:pk>/delete/', delete_announcement_view, name='delete_announcement'),

    # 考勤管理
    path('attendance/', attendance_list_view, name='attendance_list'),
    path('attendance/mark/<int:course_id>/', mark_attendance_view, name='mark_attendance'),
    path('attendance/qr/<int:course_id>/', generate_qr_code_view, name='generate_qr'),
    path('attendance/qr/scan/<str:code>/', scan_qr_code_view, name='scan_qr_code'),
    path('checkin/', views.checkin_view, name='checkin'),

    # 成绩报告
    path('grade-report/<int:course_id>/', grade_report_view, name='grade_report'),

    # 系统报告
    path('system-report/', system_report_view, name='system_report'),

    path('system-settings/', system_settings_view, name='system_settings'),
    path('export-report/', export_report_view, name='export_report'),
    path('import-grades/<int:course_id>/', import_grades_view, name='import_grades'),
    path('teacher-analysis/', teacher_analysis_view, name='teacher_analysis'),
]
