from django.db import models

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class TavernGroup(models.Model):
    "Similar interests group, create events for these"
    name = models.CharField(max_length=40)
    group_type = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    members_name = models.CharField(verbose_name="Member's Name",
                                    help_text='What do you want to \
                                              call the group members?',
                                    max_length=40,
                                    null=True,
                                    blank=True)
    country = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    creator = models.ForeignKey(User, related_name="created_groups")
    organizers = models.ManyToManyField(User)
    slug = models.SlugField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return u'/groups/%s' % self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(TavernGroup, self).save(*args, **kwargs)


class Member(models.Model):
    "People who are in a TavernGroup"
    user = models.ForeignKey(User, related_name='tavern_groups')
    tavern_group = models.ForeignKey(TavernGroup, related_name='members')
    join_date = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s" % (self.user.username, self.tavern_group.name)


class Event(models.Model):
    "Event you can attend"
    group = models.ForeignKey(TavernGroup)

    name = models.CharField(max_length=200)
    description = models.TextField()
    starts_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=250)    

    creator = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return u'/events/%s' % self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)


RSVP_CHOICES = (('yes', 'Yes'), ('no', 'No'), ('maybe', 'May Be'))


class Attendee(models.Model):
    "People who have RSVPed to events"
    user = models.ForeignKey(User)
    member = models.ForeignKey(Member)
    event = models.ForeignKey(Event)
    rsvped_on = models.DateTimeField()
    rsvp_status = models.CharField(verbose_name="RSVP Status",
                                   choices=RSVP_CHOICES,
                                   max_length=5,
                                   blank=True,
                                   null=True)

    def __unicode__(self):
        return "%s - %s" % (self.user.first_name, self.event.name)
