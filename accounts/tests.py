from django.test import TestCase, Client
from django.contrib.auth.models import User


class TestViews(TestCase):

    def setUp(self):
        self.user = create_and_get_user()
        self.client = Client()
        self.client.login(username="test", password="test")


    def test_change_password(self):
        response = self.client.post(
            '/user/change_password/',
            {'old_password': 'test',
             'new_password1': 'test2',
             'new_password2': 'test2'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user/change_password/')
        self.assertEqual(response.status_code, 200)


    def test_signup(self):
        response = self.client.post(
            '/user/signup',
            {'username': 'test1',
            'password1': 'test_password',
            'password2': 'test_password',
            'email': 'test@test.com'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/user/signup/')
        self.assertEqual(response.status_code, 200)


    def test_signin(self):
        response = self.client.post(
            '/user/signin',
            {'username': 'test',
             'password': 'test'})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            '/user/signin',
            {'username': 'dummy',
             'password': 'dummy'})
        self.assertEqual(response.status_code, 302)

        inactive_user = User.objects.create_user(username='inactive',
                                                 password='inactive')
        inactive_user.is_active = False
        inactive_user.save()

        response = self.client.post(
            '/user/signin',
            {'username': 'inactive',
             'password': 'inactive'})
        self.assertEqual(response.status_code, 302)


def create_and_get_user():
    return User.objects.create_user(username='test',
                                    email='test@agiliq.com',
                                    password='test')
