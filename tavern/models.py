# pylint: disable=method-hidden
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse

from .slugify import unique_slugify


class NonEmptyGroupManager(models.Manager):

    def get_queryset(self):
        """
        Filters out tavern groups which contain no members
        """
        return super(NonEmptyGroupManager, self).get_queryset().exclude(members=None)


class TavernGroup(models.Model):
    "Similar interests group, create events for these"
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=200)
    members_name = models.CharField(verbose_name="Member's Name",
                                    help_text='What do you want to \
                                              call the group members?',
                                    max_length=40,
                                    blank=True)
    creator = models.ForeignKey(User,
                                related_name="created_groups")
    organizers = models.ManyToManyField(User,
                                        related_name="organizes_groups")
    members = models.ManyToManyField(User,
                                     through="Membership",
                                     related_name="tavern_groups")
    slug = models.SlugField(max_length=50)

    default = models.Manager()
    objects = NonEmptyGroupManager()

    def get_absolute_url(self):
        return reverse("tavern_group_details", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(TavernGroup, self).save(*args, **kwargs)
        Membership.objects.get_or_create(
            user=self.creator,
            tavern_group=self,
            defaults={'join_date': timezone.now().isoformat()})

    def __unicode__(self):
        return "%s" % self.name


class Membership(models.Model):
    "People who are in a TavernGroup"
    user = models.ForeignKey(User,
                             related_name='tgroup_memberships')
    tavern_group = models.ForeignKey(TavernGroup,
                                     related_name='memberships')
    join_date = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s" % (self.user.username, self.tavern_group.name)


class EventShowManager(models.Manager):

    def get_queryset(self):
        return super(EventShowManager, self).get_queryset().filter(show=True)


class Event(models.Model):
    "Event you can attend"
    group = models.ForeignKey(TavernGroup)

    name = models.CharField(max_length=200)
    description = models.TextField()
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=250)

    creator = models.ForeignKey(User)
    show = models.BooleanField(default=True)

    default = models.Manager()
    objects = EventShowManager()

    class Meta:
        unique_together = ('group', 'name')
        ordering = ['starts_at']

    def get_absolute_url(self):
        return reverse("tavern_event_details", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(Event, self).save(*args, **kwargs)
        Attendee.objects.get_or_create(
            user=self.creator,
            event=self,
            defaults={'rsvped_on': timezone.now(),
                      'rsvp_status': 'yes'})

    def __unicode__(self):
        return "%s" % self.name


RSVP_CHOICES = (('yes', 'Yes'), ('no', 'No'), ('maybe', 'May Be'))


class Attendee(models.Model):
    "People who have RSVPed to events"
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    rsvped_on = models.DateTimeField()
    rsvp_status = models.CharField(verbose_name="RSVP Status",
                                   choices=RSVP_CHOICES,
                                   max_length=5,
                                   blank=True,
                                   null=True)

    def __unicode__(self):
        return "%s - %s" % (self.user.first_name, self.event.name)


#Helper methods
def get_groups(user):
    user_groups = TavernGroup.objects.filter(members=user)
    return user_groups
