from django.test import TestCase, Client
from django.contrib.auth.models import User

from .models import TavernGroup, Membership, Event, Attendee

from datetime import datetime, timedelta


class TestModels(TestCase):

    def test_tavern_group_save(self):
        """When a TavernGroup is saved, we want to make sure
        an instance of Membership which associates the creator
        with group is created"""
        creator = create_and_get_user()
        tavern_group = create_and_get_tavern_group(creator=creator)
        self.assertEqual(TavernGroup.objects.count(), 1)
        self.assertEqual(Membership.objects.count(), 1)
        # Change an attribute of tavern_group
        tavern_group.description = 'Changed description'
        tavern_group.save()
        self.assertEqual(TavernGroup.objects.count(), 1)
        self.assertEqual(Membership.objects.count(), 1)

        member = Membership.objects.all()[0]
        self.assertEqual(member.__unicode__(), u'test - TestGroup')

    def test_tavern_attendees(self):
        """Test to assert that two attendee objects are
           created.One object is created after an Event
           and one object after Attendee"""

        event = create_and_get_event()
        self.assertEqual(event.__unicode__(), 'Tavern Event')

        self.assertEqual(Attendee.objects.count(), 1)
        attendee = Attendee.objects.create(user=event.creator,
                                           event=event,
                                           rsvped_on=datetime.now(),
                                           rsvp_status="yes")
        self.assertEqual(Attendee.objects.count(), 2)
        self.assertEqual(attendee.__unicode__(), u' - Tavern Event')


class TestViews(TestCase):

    def setUp(self):
        self.user = create_and_get_user()
        self.client = Client()
        self.client.login(username="test", password="test")

    # def test_today_date(self):
        # self.assertEqual(today_date(), timezone.now().isoformat())

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(len(response.context['joined_groups']), 0)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        response = self.client.get("/")
        self.assertEqual(len(response.context['groups']), 0)
        self.assertEqual(response.status_code, 200)

    def test_create_event(self):
        creator = self.user
        group = create_and_get_tavern_group(creator)
        response = self.client.post(
            "/create_event/",
            {'starts_at': u'2014-06-25 12:00',
             'ends_at': u'2014-06-25 14:00',
             'group': group.id,
             'name': 'Test',
             'description': 'Test Event',
             'location': 'Hyderabad'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/create_event/')
        self.assertEqual(response.status_code, 200)

    def test_create_group(self):
        creator = self.user
        response = self.client.post(
            "/create_group/",
            {'name': 'OpenTavern',
             'group_type': 'Technical',
             'description': 'A Test Group',
             'members_name': 'Djangoers',
             'country': 'India',
             'city': 'Hyderabad'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/create_group/')
        self.assertEqual(response.status_code, 200)

    def test_group_details(self):
        creator = self.user
        group = create_and_get_tavern_group(creator)
        response = self.client.get('/groups/%s/' % group.slug)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/groups/%s/' % 'Incorrect_Slug')
        self.assertEqual(response.status_code, 404)

    def test_event_details(self):
        event = create_and_get_event(self.user)
        response = self.client.get('/events/%s/' % event.slug)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/events/%s/' % 'incorrect_slug')
        self.assertEqual(response.status_code, 404)

    def test_tavern_toggle_member(self):
        group = create_and_get_tavern_group(self.user)
        response = self.client.post(
            '/tavern_toggle_member/',
            {'user_id': self.user.id,
             'slug': group.slug})
        self.assertEqual(response.status_code, 200)

        user = User.objects.create_user(username='test2',
                                        email='test2@agiliq.com',
                                        password='test2')
        group = create_and_get_tavern_group(user, name='group2')
        response = self.client.post(
            '/tavern_toggle_member/',
            {'user_id': self.user.id,
             'slug': group.slug})
        self.assertEqual(response.status_code, 200)


def create_and_get_user():
    return User.objects.create_user(username='test',
                                    email='test@agiliq.com',
                                    password='test')


def create_and_get_tavern_group(creator, name=None, organizers=None):
    if not name:
        name = 'TestGroup'
    group = TavernGroup(name=name,
                        description='A group for testing',
                        creator=creator)
    group.save()
    if organizers:
        group.organizers.add(organizers)
    return group


def create_and_get_event(user=None):
    ends_at = datetime.now() + timedelta(days=1)

    if user:
        creator = user
    else:
        creator = create_and_get_user()

    group = create_and_get_tavern_group(creator)
    event = Event.objects.create(group=group,
                                 name="Tavern Event",
                                 description="Test cases",
                                 starts_at=datetime.now(),
                                 ends_at=ends_at,
                                 location="Hyderabad",
                                 creator=creator)
    return event
