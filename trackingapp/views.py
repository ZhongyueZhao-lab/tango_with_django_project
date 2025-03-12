import random
import string
import qrcode
import io
import csv
import datetime
import math

from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import CheckinLocation, AttendanceRecord, Course
from trackingapp.models import CheckinLocation, AttendanceRecord
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.utils import timezone
from django.db.models import Count, Q, Prefetch
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.http import FileResponse

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .forms import (
    UserRegisterForm, 
    CustomAuthForm, 
    CourseForm, 
    AnnouncementForm, 
    GradeForm, 
    SystemSettingForm,
    ImportGradesForm
)
from .models import User, Course, Announcement, AttendanceRecord, Grade, LoginLog, AnnouncementReadStatus, SystemSetting, CheckinLocation


###############################
# 辅助函数
###############################
def generate_6_digit_code():
    return ''.join(random.choices(string.digits, k=6))

def send_mfa_code_via_email(user, code):
    subject = "Login Verification Code"
    message = f"Hello {user.username},\nYour verification code is: {code}\n"
    from_email = "2082393264@qq.com"  
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

def calculate_user_avg_attendance(user: User) -> float:
    """
    计算某个学生的平均出勤率（0~100%）。
    """
    total_records = AttendanceRecord.objects.filter(student=user).count()
    if total_records == 0:
        return 0.0
    present_records = AttendanceRecord.objects.filter(student=user, status='P').count()
    return round(present_records / total_records * 100, 1)

def calculate_teacher_avg_attendance(user: User) -> float:
    """
    计算某位老师教授的所有课程的平均出勤率。
    """
    courses = Course.objects.filter(teacher=user)
    qs = AttendanceRecord.objects.filter(course__in=courses)
    total_records = qs.count()
    if total_records == 0:
        return 0.0
    present_records = qs.filter(status='P').count()
    return round(present_records / total_records * 100, 1)

def count_unread_announcements(user: User) -> int:
    """
    统计某用户的未读公告数。
    逻辑：公告未过期 + AnnouncementReadStatus 中 has_read=False
    """
    now = timezone.now()
    valid_anns = Announcement.objects.filter(Q(valid_until__gt=now) | Q(valid_until__isnull=True))
    unread_count = valid_anns.exclude(
        read_status__user=user,
        read_status__has_read=True
    ).count()
    return unread_count

def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'

def is_teacher(user):
    return user.is_authenticated and user.role == 'TEACHER'


###############################
# MFA登录 / 注册 / 首页
###############################
def custom_login_view(request):
    if request.method == 'POST':
        form = CustomAuthForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                code = generate_6_digit_code()
                request.session['mfa_user_id'] = user.id
                request.session['mfa_code'] = code
                send_mfa_code_via_email(user, code)
                return redirect('verify_mfa')
    else:
        form = CustomAuthForm()
    return render(request, 'trackingapp/login.html', {'form': form})


def verify_mfa_view(request):
    if request.method == 'POST':
        input_code = request.POST.get('mfa_code')
        session_code = request.session.get('mfa_code', '')
        user_id = request.session.get('mfa_user_id')
        if input_code == session_code and user_id:
            user = User.objects.get(id=user_id)
            login(request, user)
            request.session.pop('mfa_code', None)
            request.session.pop('mfa_user_id', None)
            messages.success(request, "MFA verification successful, logged in.")
            return redirect('/')
        else:
            messages.error(request, "Incorrect verification code, please try again.")
    return render(request, 'trackingapp/verify_mfa.html')


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, "Registration successful, please log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'trackingapp/home.html', {'form': form, 'register': True})


def home_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('dashboard_admin')
        elif request.user.role == 'TEACHER':
            return redirect('dashboard_teacher')
        else:
            return redirect('dashboard_student')
    form = UserRegisterForm()
    return render(request, 'trackingapp/home.html', {'form': form, 'register': True})


###############################
# 不同角色Dashboard
###############################
@login_required
def dashboard_admin_view(request):
    if request.user.role != 'ADMIN':
        return redirect('/')

    # 全校平均出勤率
    total_attendance = AttendanceRecord.objects.count()
    if total_attendance == 0:
        avg_attendance = 0.0
    else:
        present_count = AttendanceRecord.objects.filter(status='P').count()
        avg_attendance = round(present_count / total_attendance * 100, 1)

    # 未读公告数
    unread_ann_count = count_unread_announcements(request.user)

    # 统计示例
    total_students = User.objects.filter(role='STUDENT').count()
    total_teachers = User.objects.filter(role='TEACHER').count()
    total_courses = Course.objects.count()

    context = {
        'avg_attendance': avg_attendance,
        'unread_ann_count': unread_ann_count,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
    }
    return render(request, 'trackingapp/dashboard_admin.html', context)


@login_required
def dashboard_teacher_view(request):
    if request.user.role != 'TEACHER':
        return redirect('/')
    courses = Course.objects.filter(teacher=request.user)

    avg_attendance = calculate_teacher_avg_attendance(request.user)
    unread_ann_count = count_unread_announcements(request.user)

    # 统计“在读学生”
    distinct_students_count = User.objects.filter(
        role='STUDENT',
        courses__in=courses
    ).distinct().count()

    context = {
        'courses': courses,
        'avg_attendance': avg_attendance,
        'unread_ann_count': unread_ann_count,
        'distinct_students_count': distinct_students_count,
    }
    return render(request, 'trackingapp/dashboard_teacher.html', context)


@login_required
def dashboard_student_view(request):
    if request.user.role != 'STUDENT':
        return redirect('/')
    courses = request.user.courses.all()

    avg_attendance = calculate_user_avg_attendance(request.user)
    unread_ann_count = count_unread_announcements(request.user)

    context = {
        'courses': courses,
        'avg_attendance': avg_attendance,
        'unread_ann_count': unread_ann_count,
    }
    return render(request, 'trackingapp/dashboard_student.html', context)


@login_required
def role_dashboard_redirect_view(request):
    if request.user.role == 'ADMIN':
        return redirect('dashboard_admin')
    elif request.user.role == 'TEACHER':
        return redirect('dashboard_teacher')
    else:
        return redirect('dashboard_student')


###############################
# 课程管理：允许学生选课
###############################
@login_required
def manage_courses_view(request):
    user = request.user
    if user.role == 'ADMIN':
        courses = Course.objects.all()
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Course created successfully")
                return redirect('manage_courses')
        else:
            form = CourseForm()
        return render(request, 'trackingapp/manage_courses.html', {
            'courses': courses,
            'form': form
        })

    elif user.role == 'TEACHER':
        courses = Course.objects.filter(teacher=user)
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Course created successfully")
                return redirect('manage_courses')
        else:
            form = CourseForm()
        return render(request, 'trackingapp/manage_courses.html', {
            'courses': courses,
            'form': form
        })

    elif user.role == 'STUDENT':
        # 学生可查看全部课程，并可选/退课
        courses = Course.objects.all()
        if request.method == 'POST':
            action_type = request.POST.get('action_type')
            c_id = request.POST.get('course_id')
            try:
                c = Course.objects.get(id=c_id)
                if action_type == 'enroll':
                    c.students.add(user)
                    messages.success(request, f"You have successfully enrolled in: {c.name}")
                elif action_type == 'drop':
                    c.students.remove(user)
                    messages.success(request, f"You have successfully dropped course: {c.name}")
            except Course.DoesNotExist:
                messages.error(request, "Course does not exist")
        return render(request, 'trackingapp/manage_courses.html', {
            'courses': courses
        })
    else:
        messages.error(request, "No permission to access this page")
        return redirect('/')


@login_required
def manage_course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    if user.role == 'ADMIN' or (user.role == 'TEACHER' and course.teacher == user):
        if request.method == 'POST':
            student_id = request.POST.get('student_id')
            action_type = request.POST.get('action_type')
            if student_id and action_type:
                try:
                    student = User.objects.get(id=student_id, role='STUDENT')
                    if action_type == 'add':
                        course.students.add(student)
                        messages.success(request, f"Student added: {student.username}")
                    elif action_type == 'remove':
                        course.students.remove(student)
                        messages.success(request, f"Student removed: {student.username}")
                except User.DoesNotExist:
                    messages.error(request, "Student does not exist")
        students_in_course = course.students.all()
        all_students = User.objects.filter(role='STUDENT')
        return render(request, 'trackingapp/manage_course_detail.html', {
            'course': course,
            'students_in_course': students_in_course,
            'all_students': all_students
        })
    else:
        messages.error(request, "No permission to access this page")
        return redirect('/')


###############################
# 公告管理
###############################
@login_required
def announcement_list_view(request):
    now = timezone.now()
    announcements = Announcement.objects.filter(
        Q(valid_until__gt=now) | Q(valid_until__isnull=True)
    ).order_by('-created_at')
    return render(request, 'trackingapp/announcement_list.html', {
        'announcements': announcements
    })


@login_required
def announcement_detail_view(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    # 标记已读
    read_obj, _ = AnnouncementReadStatus.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    if not read_obj.has_read:
        read_obj.has_read = True
        read_obj.read_time = timezone.now()
        read_obj.save()

    return render(request, 'trackingapp/announcement_detail.html', {
        'announcement': announcement
    })


@login_required
def create_announcement_view(request):
    if request.user.role not in ['ADMIN', 'TEACHER']:
        messages.error(request, "No permission to access this page")
        return redirect('/')
    create_mode = True
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.creator = request.user
            if request.user.role == 'TEACHER':
                ann.is_global = False
            ann.save()
            messages.success(request, "Announcement created successfully")
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'trackingapp/announcement_list.html', {
        'form': form,
        'create_mode': create_mode,
        'announcements': announcements
    })


@login_required
def edit_announcement_view(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.user.role == 'ADMIN' or (request.user.role == 'TEACHER' and announcement.creator == request.user):
        edit_mode = True
        if request.method == 'POST':
            form = AnnouncementForm(request.POST, instance=announcement)
            if form.is_valid():
                ann = form.save(commit=False)
                if request.user.role == 'TEACHER':
                    ann.is_global = False
                ann.save()
                messages.success(request, "Announcement edited successfully")
                return redirect('announcement_detail', pk=pk)
        else:
            form = AnnouncementForm(instance=announcement)
        announcements = Announcement.objects.all().order_by('-created_at')
        return render(request, 'trackingapp/announcement_list.html', {
            'form': form,
            'edit_mode': edit_mode,
            'announcements': announcements,
            'announcement': announcement,
        })
    else:
        messages.error(request, "No permission to edit this announcement")
        return redirect('/')


@login_required
def delete_announcement_view(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.user.role == 'ADMIN' or (request.user.role == 'TEACHER' and announcement.creator == request.user):
        announcement.delete()
        messages.success(request, "Announcement deleted")
    else:
        messages.error(request, "No permission to delete this announcement")
    return redirect('announcement_list')


###############################
# 考勤管理
###############################
@login_required
def attendance_list_view(request):
    user = request.user
    if user.role == 'STUDENT':
        attendance_records = AttendanceRecord.objects.filter(student=user)
        courses = None
    elif user.role == 'TEACHER':
        courses = Course.objects.filter(teacher=user).prefetch_related('students')
        attendance_records = AttendanceRecord.objects.filter(course__in=courses)
    elif user.role == 'ADMIN':
        courses = Course.objects.all().prefetch_related('students')
        attendance_records = AttendanceRecord.objects.all()
    else:
        courses = None
        attendance_records = AttendanceRecord.objects.none()

    return render(request, 'trackingapp/attendance_list.html', {
        'attendance_records': attendance_records,
        'courses': courses,
    })


@login_required
def mark_attendance_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        user = request.user
        if user.role == 'STUDENT':
            # 学生只可标记自己的考勤，并且必须已选该课程
            if user in course.students.all():
                status = request.POST.get('status', 'P')
                AttendanceRecord.objects.create(student=user, course=course, status=status)
                messages.success(request, "Attendance marked successfully")
            else:
                messages.error(request, "You have not enrolled in this course, unable to mark attendance")
        elif user.role in ['TEACHER', 'ADMIN']:
            student_id = request.POST.get('student_id')
            status = request.POST.get('status', 'P')
            try:
                student = User.objects.get(id=student_id, role='STUDENT')
                AttendanceRecord.objects.create(student=student, course=course, status=status)
                messages.success(request, f"Attendance marked for {student.username}")
            except User.DoesNotExist:
                messages.error(request, "Student does not exist or incorrect role")
        else:
            messages.error(request, "No permission")
    return redirect('attendance_list')


@login_required
def generate_qr_code_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.role not in ['TEACHER', 'ADMIN']:
        messages.error(request, "No permission")
        return redirect('/')

    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    code = f"{course_id}-{random_str}"
    checkin_url = request.build_absolute_uri(f"/attendance/qr/scan/{code}/")

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(checkin_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    image_bytes = buf.getvalue()

    qr_map = request.session.get('qr_code_map', {})
    qr_map[code] = course_id
    request.session['qr_code_map'] = qr_map

    return HttpResponse(image_bytes, content_type="image/png")


@login_required
def scan_qr_code_view(request, code):
    qr_map = request.session.get('qr_code_map', {})
    if code not in qr_map:
        messages.error(request, "QR code invalid or expired")
        return redirect('/')
    if request.user.role != 'STUDENT':
        messages.error(request, "You must log in with a student account to check in")
        return redirect('/')
    course_id = qr_map[code]
    course = get_object_or_404(Course, id=course_id)
    AttendanceRecord.objects.create(student=request.user, course=course, status='P')
    messages.success(request, f"You have successfully checked in for {course.name}")
    return redirect('attendance_list')

@login_required
def checkin_view(request):
    """
    GPS 地图签到
    """
    if request.method == 'POST':
        user = request.user
        allowed_distance = 100  # 允许的签到范围（米）

        # 获取前端传来的数据
        course_id = request.POST.get('course_id')
        if not course_id:
            return JsonResponse({"message": "Course is required for check-in!"}, status=400)

        try:
            latitude = float(request.POST.get('latitude', 0))
            longitude = float(request.POST.get('longitude', 0))
        except ValueError:
            return JsonResponse({"message": "Invalid location data!"}, status=400)

         # 获取课程对象
        course = get_object_or_404(Course, id=course_id)

        # 检查签到地点是否有效
        locations = CheckinLocation.objects.all()
        if not locations.exists():
            return JsonResponse({"message": "No check-in locations configured!"}, status=400)

            # 检查是否在允许范围内
        for loc in locations:
            distance = get_distance(latitude, longitude, float(loc.latitude), float(loc.longitude))
            if distance <= allowed_distance:  # 允许 100 米范围内签到
                AttendanceRecord.objects.create( course=course,  student=user, location=loc,date=timezone.now().date(), status='P')
                return JsonResponse({"message": "Check-in successful!"})

        return JsonResponse({"message": "Location not recognized!"}, status=400)

    # 获取该学生的课程并传递到前端
    courses = Course.objects.filter(students=request.user)
    return render(request, 'trackingapp/checkin.html', {'courses': courses})

def get_distance(lat1, lon1, lat2, lon2):
    """
    计算两个经纬度坐标之间的距离（单位：米）
    """
    R = 6371000  # 地球半径（米）
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

###############################
# 成绩报告
###############################
@login_required
def grade_report_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    if user.role == 'STUDENT':
        grade, _ = Grade.objects.get_or_create(student=user, course=course)
        return render(request, 'trackingapp/grade_report.html', {
            'course': course,
            'grade': grade,
            'is_teacher': False
        })
    elif user.role == 'TEACHER' and course.teacher == user:
        if request.method == 'POST':
            student_id = request.POST.get('student_id')
            try:
                g = Grade.objects.get(student_id=student_id, course=course)
            except Grade.DoesNotExist:
                g = Grade.objects.create(student_id=student_id, course=course)
            f = GradeForm(request.POST, instance=g)
            if f.is_valid():
                f.save()
        grades = Grade.objects.filter(course=course)
        return render(request, 'trackingapp/grade_report.html', {
            'course': course,
            'grades': grades,
            'is_teacher': True,
            'GradeForm': GradeForm
        })
    else:
        messages.error(request, "No permission to view this page")
        return redirect('/')


###############################
# 系统报告 / 个人资料
###############################
@login_required
def system_report_view(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "No permission to access this page")
        return redirect('/')

    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_announcements = Announcement.objects.count()
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    active_users = LoginLog.objects.filter(login_time__gte=one_week_ago).values('user').distinct().count()

    total_attendance = AttendanceRecord.objects.count()
    present_count = AttendanceRecord.objects.filter(status='P').count()
    absent_count = AttendanceRecord.objects.filter(status='A').count()
    late_count = AttendanceRecord.objects.filter(status='L').count()

    course_registrations = Course.objects.annotate(num_students=Count('students'))

    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_announcements': total_announcements,
        'active_users': active_users,
        'total_attendance': total_attendance,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'course_registrations': course_registrations,
    }
    return render(request, 'trackingapp/system_report.html', context)


@login_required
def profile_view(request):
    return render(request, 'trackingapp/profile.html')


###############################
# ========== 新增功能 ==========
###############################
@login_required
def system_settings_view(request):
    if request.user.role != 'ADMIN':
        raise PermissionDenied("No permission to access system settings")

    setting, created = SystemSetting.objects.get_or_create(id=1)
    if request.method == 'POST':
        form = SystemSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, "System settings saved")
            return redirect('dashboard_admin')
    else:
        form = SystemSettingForm(instance=setting)

    return render(request, 'trackingapp/system_settings.html', {
        'form': form
    })


@login_required
def export_report_view(request):
    """
    PDF 导出，用于管理员或教师导出考勤记录。
    """
    if request.user.role not in ['ADMIN', 'TEACHER']:
        raise PermissionDenied("No permission to export report")

    # 设置 HTTP 响应头
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

    # 创建PDF文档
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # 标题
    elements.append(Paragraph("Attendance Report", styles['Title']))

    # 表格数据
    data = [["Student", "Course", "Date", "Status"]]

    if request.user.role == 'TEACHER':
        courses = Course.objects.filter(teacher=request.user)
        records = AttendanceRecord.objects.filter(course__in=courses)
    else:  # ADMIN
        records = AttendanceRecord.objects.all()

    for rec in records:
        data.append([rec.student.username, rec.course.code, str(rec.date), rec.get_status_display()])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4B8DF8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
    ]))
    elements.append(table)

    doc.build(elements)
    return response


@login_required
def import_grades_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.role not in ['ADMIN', 'TEACHER']:
        raise PermissionDenied("No permission to import grades")
    if request.user.role == 'TEACHER' and course.teacher != request.user:
        raise PermissionDenied("You are not the teacher of this course, unable to import")

    if request.method == 'POST':
        form = ImportGradesForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file)
            count_success = 0
            for row in reader:
                sid = row.get('student_id')
                try:
                    student = User.objects.get(id=sid, role='STUDENT')
                except User.DoesNotExist:
                    continue
                try:
                    g = Grade.objects.get(student=student, course=course)
                except Grade.DoesNotExist:
                    g = Grade(student=student, course=course)
                g.homework_score = float(row.get('homework_score', 0))
                g.exam_score = float(row.get('exam_score', 0))
                g.practice_score = float(row.get('practice_score', 0))
                g.save()
                count_success += 1

            messages.success(request, f"Successfully imported {count_success} grade records")
            return redirect('grade_report', course_id=course_id)
    else:
        form = ImportGradesForm()

    return render(request, 'trackingapp/import_grades.html', {
        'course': course,
        'form': form
    })


@login_required
def teacher_analysis_view(request):
    if request.user.role != 'TEACHER':
        raise PermissionDenied("No permission to access this feature")

    courses = Course.objects.filter(teacher=request.user)
    total_students = User.objects.filter(role='STUDENT', courses__in=courses).distinct().count()
    avg_att = calculate_teacher_avg_attendance(request.user)

    return render(request, 'trackingapp/teacher_analysis.html', {
        'courses': courses,
        'total_students': total_students,
        'avg_att': avg_att,
    })
