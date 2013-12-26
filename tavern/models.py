from django.db import models

from django.contrib.auth.models import User


class Group(models.Model):
    "Similar interests group, create events for these"
    name = models.CharField(max_length=40)
    group_type = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    members_name = models.CharField(max_length=40)
    country = models.CharField(max_length=20)
    city = models.CharField(max_length=20)

    creator = models.ForeignKey(User, related_name="created_groups")

    # members = models.ManyToManyField(User, related_name="groups_users")
    organizers = models.ManyToManyField(User)

    def __unicode__(self):
        return self.name


class Event(models.Model):
    "Event you can attend"
    group = models.ForeignKey(Group)

    name = models.CharField(max_length=200)
    description = models.TextField()
    starts_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)

    creator = models.ForeignKey(User)


class Attendee(models.Model):
    "People who have RSVPed to events"
    user = models.ForeignKey(User)
    user = models.ForeignKey(Event)
    rsvped_on = models.DateTimeField()
