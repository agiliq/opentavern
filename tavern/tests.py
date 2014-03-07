from django.test import TestCase, Client
from django.contrib.auth.models import User

from .models import TavernGroup, Member

class TestModels(TestCase):

    def test_tavern_group_save(self):
        """When a TavernGroup is saved, we want to make sure
        an instance of Member which associates the creator
        with group is created"""
        creator = create_and_get_user()
        tavern_group = create_and_get_tavern_group(creator=creator)
        self.assertEqual(TavernGroup.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 1)
        #Change an attribute of tavern_group
        tavern_group.description = 'Changed description'
        tavern_group.save()
        self.assertEqual(TavernGroup.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 1)


class TestIndex(TestCase):

    def test_http_200(self):
        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)


def create_and_get_user():
    return User.objects.create_user(username='test', email='test@agiliq.com', password='test')

def create_and_get_tavern_group(creator, organizers=None):
        group = TavernGroup(name='TestGroup', description='A group for testing', creator=creator)
        group.save()
        if organizers:
            group.organizers.add(organizers)
        return group
