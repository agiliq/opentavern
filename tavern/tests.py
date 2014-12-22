from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

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
        self.assertEqual(attendee.__unicode__(), u' - Tavern Event - yes')

    def test_event_manager(self):
        """Test the new objects manager that it returns only
        events that have show=True"""

        event1 = create_and_get_event()
        event2 = Event.objects.create(
            group=event1.group,
            name="Tavern Event 2",
            description="Test cases",
            starts_at=datetime.now(),
            ends_at=datetime.now(),
            location="Hyderabad",
            creator=event1.creator)
        event2.show = False
        event2.save()
        self.assertEqual(event1 in Event.visible_events.all(), True)
        self.assertEqual(event2 in Event.visible_events.all(), False)


class TestViews(TestCase):

    def setUp(self):
        self.user = create_and_get_user()
        self.client = Client()
        self.client.login(username="test", password="test")

    def test_index(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context['joined_groups']), 0)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context['groups']), 0)
        self.assertEqual(response.status_code, 200)

    def test_create_event(self):
        creator = self.user
        group = create_and_get_tavern_group(creator)
        response = self.client.post(
            reverse("tavern_create_event"),
            {'starts_at': u'2014-06-25 12:00',
             'ends_at': u'2014-06-25 14:00',
             'group': group.id,
             'name': 'Test',
             'description': 'Test Event',
             'location': 'Hyderabad'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("tavern_create_event"))
        self.assertEqual(response.status_code, 200)

    def test_create_group(self):
        response = self.client.post(
            reverse("tavern_create_group"),
            {'name': 'OpenTavern',
             'description': 'A Test Group',
             'members_name': 'Djangoers'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("tavern_create_group"))
        self.assertEqual(response.status_code, 200)

    def test_group_details(self):
        creator = self.user
        group = create_and_get_tavern_group(creator)
        response = self.client.get('/groups/%s/' % group.slug)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/groups/%s/' % 'Incorrect_Slug')
        self.assertEqual(response.status_code, 404)

    def test_event_details(self):
        """ Test that events with valid slugs and show=True are shown,
        otherwise return 404"""

        event = create_and_get_event(self.user)
        response = self.client.get(reverse("tavern_event_details",
                                           kwargs={'slug': event.slug,
                                                   'group': event.group.slug}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("tavern_event_details",
                                           kwargs={'slug': 'incorrect_slug',
                                                   'group': event.group.slug}))
        self.assertEqual(response.status_code, 404)
        event.show = False
        event.save()
        response = self.client.get(reverse("tavern_event_details",
                                           kwargs={'slug': 'incorrect_slug',
                                                   'group': event.group.slug}))
        self.assertEqual(response.status_code, 404)

    def test_tavern_toggle_member(self):
        group = create_and_get_tavern_group(self.user)
        response = self.client.post(
            reverse('tavern_toggle_member'),
            {'user_id': self.user.id,
             'slug': group.slug})
        self.assertEqual(response.status_code, 200)

        user = User.objects.create_user(username='test2',
                                        email='test2@agiliq.com',
                                        password='test2')
        group = create_and_get_tavern_group(user, name='group2')
        response = self.client.post(
            reverse('tavern_toggle_member'),
            {'user_id': self.user.id,
             'slug': group.slug})
        self.assertEqual(response.status_code, 200)

    def test_group_update(self):
        group = create_and_get_tavern_group(self.user)
        response = self.client.get(reverse("tavern_group_update",
                                           kwargs={'slug': group.slug}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("tavern_group_update", kwargs={'slug': group.slug}),
            {'name': 'OpenTavern',
             'description': 'A Test Group',
             'members_name': 'Djangoers'})

        self.assertRedirects(response,
                             reverse("tavern_group_details", kwargs={'slug': 'opentavern'}),
                             status_code=302)

    def test_group_delete(self):
        group = create_and_get_tavern_group(self.user)
        response = self.client.post(reverse("delete_group",
                                            kwargs={'slug': group.slug}), follow=True)
        self.assertRedirects(response, reverse("index"), status_code=302)
        self.assertEqual(group in TavernGroup.objects.all(), False)

    def test_event_update(self):
        event = create_and_get_event(user=self.user)
        response = self.client.get(reverse("tavern_event_update",
                                           kwargs={'slug': event.slug}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("tavern_event_update", kwargs={'slug': event.slug}),
            {'name': 'New name',
             'description': 'A Test Event',
             'starts_at': '2014-07-04 09:25',
             'ends_at': '2014-07-04 20:25',
             'location': 'Delhi'})
        self.assertRedirects(response,
                             reverse("tavern_event_details", kwargs={'slug': 'new-name',
                                                                     'group': event.group.slug}),
                             status_code=302)

    def test_event_delete(self):
        event = create_and_get_event(user=self.user)
        response = self.client.post(reverse("delete_event",
                                            kwargs={'slug': event.slug}), follow=True)
        self.assertRedirects(response,
                             reverse("tavern_group_details", kwargs={'slug': event.group.slug}),
                             status_code=302)
        self.assertEqual(event in Event.objects.all(), False)

    def test_change_rsvp(self):
        event = create_and_get_event(user=self.user)
        response = self.client.get(reverse("change_rsvp",
                                           kwargs={'event_id': event.pk, 'rsvp_status': 'no'}))
        self.assertContains(response, 'You are not attending this event')

        response = self.client.get(reverse("change_rsvp",
                                           kwargs={'event_id': event.pk, 'rsvp_status': 'maybe'}))
        self.assertContains(response, 'You may attend this event')

    def test_delete_rsvp(self):
        event = create_and_get_event(user=self.user)
        attendee = Attendee.objects.get(event=event, user=self.user)
        response = self.client.post(reverse("delete_rsvp",
                                            kwargs={'pk': attendee.pk}), follow=True)
        self.assertRedirects(response,
                             reverse("tavern_event_details", kwargs={'slug': event.slug,
                                                                     'group': event.group.slug}),
                             status_code=302)

    def test_edit_organizers(self):
        group = create_and_get_tavern_group(self.user)
        org = User.objects.create_user(username='org',
                                       email='org@agiliq.com',
                                       password='org')
        response = self.client.post(
            reverse('edit_organizers', kwargs={'slug': group.slug}),
            {'usernames': org.username,
             'action': 'add'})
        self.assertRedirects(response,
                             reverse("tavern_group_details", kwargs={'slug': group.slug}),
                             status_code=302)
        self.assertEqual(org in group.organizers.all(), True)

        response = self.client.post(
            reverse('edit_organizers', kwargs={'slug': group.slug}),
            {'usernames': org.username,
             'action': 'remove',
             'group': group.pk})
        self.assertRedirects(response,
                             reverse("tavern_group_details", kwargs={'slug': group.slug}),
                             status_code=302)
        self.assertEqual(org in group.organizers.all(), False)


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


def create_and_get_event(user=None, tgroup=None):
    ends_at = datetime.now() + timedelta(days=1)

    if user:
        creator = user
    else:
        creator = create_and_get_user()

    if tgroup:
        group = tgroup
    else:
        group = create_and_get_tavern_group(creator)
    event = Event.objects.create(group=group,
                                 name="Tavern Event",
                                 description="Test cases",
                                 starts_at=datetime.now(),
                                 ends_at=ends_at,
                                 location="Hyderabad",
                                 creator=creator)
    return event
