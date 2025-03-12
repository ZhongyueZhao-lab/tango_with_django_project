#################################################################
# 文件: trackingapp/tests.py (单元测试)
#################################################################
from django.test import TestCase, Client
from django.urls import reverse
from .models import User

class SimpleTests(TestCase):
    def setUp(self):
        self.client = Client()
        # 创建一个测试用户
        self.test_user = User.objects.create_user(username='testuser', password='12345', role='STUDENT')

    def test_homepage_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        login_success = self.client.login(username='testuser', password='12345')
        # MFA不在此做深度测试，只验证用户名密码对即可
        self.assertTrue(login_success)
