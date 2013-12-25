from django.test import TestCase, Client


class TestIndex(TestCase):

    def test_http_200(self):
        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
