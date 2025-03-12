#################################################################
# 文件: trackingapp/models.py
#################################################################
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class AnnouncementReadStatus(models.Model):
    """
    用于记录用户是否已读某条公告。
    """
    announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE, related_name='read_status')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='announcement_reads')
    has_read = models.BooleanField(default=False)
    read_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.announcement.title} (Read: {self.has_read})"


class User(AbstractUser):
    # 角色：ADMIN、TEACHER、STUDENT
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'TEACHER'})

    students = models.ManyToManyField(User, related_name='courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    important_level = models.IntegerField(default=1, help_text="1=Normal, 2=Important, 3=Urgent")
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    is_global = models.BooleanField(default=False)  # 是否全局公告(仅管理员可创建)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - By {self.creator.username}"

class CheckinLocation(models.Model):
    """
    用于存储可签到的地理位置
    """
    location_name = models.CharField(max_length=255, default="Unknown Location")  # 位置名称
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # 维度
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # 经度
    radius = models.FloatField(default=100.0)  # 允许签到的半径（单位：米）
    created_at = models.DateTimeField(auto_now_add=True)  # 记录创建时间

    def __str__(self):
        return f"{self.location_name} ({self.latitude}, {self.longitude})"

class AttendanceRecord(models.Model):
    ATTENDANCE_STATUS = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=1, choices=ATTENDANCE_STATUS, default='P')
    location = models.ForeignKey(CheckinLocation, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.code} - {self.date} - {self.get_status_display()}"


class Grade(models.Model):
    """
    用于记录多种类型成绩
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    homework_score = models.FloatField(default=0)  # 平时
    exam_score = models.FloatField(default=0)      # 考试
    practice_score = models.FloatField(default=0)  # 作业

    @property
    def total_score(self):

        return (self.homework_score * 0.3
              + self.exam_score * 0.5
              + self.practice_score * 0.2)

    def __str__(self):
        return f"{self.student.username}-{self.course.code} => {self.total_score}"


class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} at {self.login_time}"


class SystemSetting(models.Model):
    """
    用于存储系统级别配置，如站点名称等
    """
    site_name = models.CharField(max_length=100, default="EduTracking System")
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return self.site_name


