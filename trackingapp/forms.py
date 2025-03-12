#################################################################
# 文件: trackingapp/forms.py
#################################################################
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Course, Announcement, Grade, SystemSetting


class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label='Role')

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']


class CustomAuthForm(AuthenticationForm):

    pass


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'teacher']


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'important_level', 'course', 'is_global', 'valid_until']


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['homework_score', 'exam_score', 'practice_score']


class SystemSettingForm(forms.ModelForm):
    class Meta:
        model = SystemSetting
        fields = ['site_name', 'maintenance_mode']


class ImportGradesForm(forms.Form):

    file = forms.FileField(label="Choose CSV File")
