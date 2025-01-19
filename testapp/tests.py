
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

from .models import Test, StudentTest, Question

class FullFeaturesTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_login_logout(self):
        resp = self.client.post(reverse('register'), {
            'username':'tester',
            'email':'test@test.com',
            'password1':'Abc12345!',
            'password2':'Abc12345!'
        }, follow=True)
        print('DEBUG register =>', resp.content.decode('utf-8','ignore'))
        self.assertContains(resp, 'Регистрация ok!', html=False)

        # logout
        resp = self.client.get(reverse('logout'), follow=True)
        print('DEBUG logout =>', resp.content.decode('utf-8','ignore'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

        # login
        resp = self.client.post(reverse('login'), {
            'username':'tester',
            'password':'Abc12345!'
        }, follow=True)
        print('DEBUG login =>', resp.content.decode('utf-8','ignore'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_become_admin(self):
        user = User.objects.create_user('testuser','t@u.com','pass123')
        self.client.login(username='testuser', password='pass123')
        resp = self.client.get(reverse('become_admin'), follow=True)
        print('DEBUG become_admin =>', resp.content.decode('utf-8','ignore'))
        self.assertContains(resp, 'Теперь вы админ', html=False)
        user.refresh_from_db()
        self.assertTrue(user.is_staff)

    def test_create_test_and_delete(self):
        # admin
        admin = User.objects.create_user('admin','admin@test.com','adminpass')
        admin.is_staff=True
        admin.save()
        self.client.login(username='admin', password='adminpass')

        now = timezone.now()
        start_str = (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_str   = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

        resp = self.client.post(reverse('create_test'), {
            'title':'TestX',
            'description':'descX',
            'start_time': start_str,
            'end_time': end_str,
            'duration_minutes':'30',
            'pass_score':'50',
            'access_key':'KEYX'
        }, follow=True)
        print('DEBUG create_test =>', resp.content.decode('utf-8','ignore'))
        self.assertContains(resp, 'Тест создан.', html=False)
        t = Test.objects.get(access_key='KEYX')

        # delete
        resp = self.client.get(reverse('delete_test', args=[t.id]), follow=True)
        print('DEBUG delete_test =>', resp.content.decode('utf-8','ignore'))
        self.assertContains(resp, 'Тест удалён.', html=False)
        self.assertFalse(Test.objects.filter(id=t.id).exists())

    def test_create_question_and_pass(self):
        # admin
        admin = User.objects.create_user('admin2','adm2@test.com','pass222')
        admin.is_staff=True
        admin.save()
        self.client.login(username='admin2', password='pass222')

        now = timezone.now()
        start_str = (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        end_str   = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

        resp = self.client.post(reverse('create_test'), {
            'title':'TestQ',
            'description':'descQ',
            'start_time': start_str,
            'end_time': end_str,
            'duration_minutes':'5',
            'pass_score':'10',
            'access_key':'QKEY'
        }, follow=True)
        print('DEBUG create_test QKEY =>', resp.content.decode('utf-8','ignore'))
        self.assertContains(resp, 'Тест создан.', html=False)
        t = Test.objects.get(access_key='QKEY')

        # create question
        resp = self.client.post(reverse('create_question', args=[t.id]), {
            'text':'1+1=?',
            'question_type':'text',
            'correct_text':'2',
            'score':'10'
        }, follow=True)
        print('DEBUG create_question =>', resp.content.decode('utf-8','ignore'))
        self.assertContains(resp, 'Вопрос добавлен.', html=False)
        q = Question.objects.get(test=t, text='1+1=?')

        # user pass
        self.client.logout()
        user2 = User.objects.create_user('u2','u2@x.com','xxpass')
        self.client.login(username='u2', password='xxpass')

        resp = self.client.post(reverse('test_access'), {
            'access_key':'QKEY'
        }, follow=True)
        print('DEBUG test_access =>', resp.content.decode('utf-8','ignore'))
        # проверяем 'Доступ к тесту получен!'
        self.assertContains(resp, 'Доступ к тесту получен!', html=False)

        pass_url = reverse('test_detail', args=[t.id])
        resp = self.client.post(pass_url, {
            f"q_{q.id}": "2"
        }, follow=True)
        print('DEBUG passing test =>', resp.content.decode('utf-8','ignore'))
        st = StudentTest.objects.get(test=t, student__user__username='u2')
        self.assertEqual(st.score, 10)
        self.assertTrue(st.passed)
        self.assertContains(resp, 'Тест пройден', html=False)
