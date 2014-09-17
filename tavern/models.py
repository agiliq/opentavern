# pylint: disable=method-hidden
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

from .slugify import unique_slugify


class TavernGroupManager(models.Manager):

    def non_empty_groups(self):
        """
        Excludes groups which does not contain any member
        """
        return super(TavernGroupManager, self).all().exclude(members=None)


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

    objects = TavernGroupManager()

    def get_absolute_url(self):
        return reverse("tavern_group_details", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(TavernGroup, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % self.name


class Membership(models.Model):
    "People who are in a TavernGroup"
    user = models.ForeignKey(User,
                             related_name='tgroup_memberships')
    tavern_group = models.ForeignKey(TavernGroup,
                                     related_name='memberships')
    join_date = models.DateTimeField()

    class Meta:
        unique_together = ['user', 'tavern_group']

    def __unicode__(self):
        return "%s - %s" % (self.user.username, self.tavern_group.name)


class EventShowManager(models.Manager):

    def get_queryset(self):
        return super(EventShowManager, self).get_queryset().filter(show=True)

    def upcoming(self):
        return self.get_queryset().filter(starts_at__gte=timezone.now())

    def past(self):
        return self.get_queryset().filter(starts_at__lte=timezone.now())


class Event(models.Model):
    "Event you can attend"
    group = models.ForeignKey(TavernGroup)

    name = models.CharField(max_length=200)
    description = models.TextField()
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)

    attendees = models.ManyToManyField(User, through="Attendee",
                                       related_name="events_attending")
    slug = models.SlugField(max_length=250)

    creator = models.ForeignKey(User)
    show = models.BooleanField(default=True)

    objects = models.Manager()
    visible_events = EventShowManager()

    class Meta:
        ordering = ['starts_at']

    def get_absolute_url(self):
        return reverse("tavern_event_details", kwargs={"slug": self.slug,
                                                       "group": self.group.slug})

    def save(self, *args, **kwargs):
        # This event's slug should not match a slug of any
        # existing event in the same group.
        slug_queryset = self.group.event_set.all()
        unique_slugify(self, self.name, queryset=slug_queryset)
        super(Event, self).save(*args, **kwargs)
        Attendee.objects.get_or_create(
            user=self.creator,
            event=self,
            defaults={'rsvped_on': timezone.now(),
                      'rsvp_status': 'yes'})

    def __unicode__(self):
        return "%s" % self.name


class Attendee(models.Model):
    "People who have RSVPed to events"
    RSVP_CHOICES = (('yes', 'Yes'), ('no', 'No'), ('maybe', 'May Be'))
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    rsvped_on = models.DateTimeField()
    rsvp_status = models.CharField(verbose_name="RSVP Status",
                                   choices=RSVP_CHOICES,
                                   max_length=5,
                                   default="yes")

    def __unicode__(self):
        return "%s - %s" % (self.user.first_name, self.event.name)


def get_unjoined_groups(user):
    user_unjoined_groups = TavernGroup.objects.exclude(members=user)
    return user_unjoined_groups


def get_groups(user):
    user_groups = TavernGroup.objects.filter(members=user)
    return user_groups


@receiver(post_save, sender=TavernGroup)
def group_create(sender, **kwargs):
    model_instance = kwargs["instance"]
    if kwargs["created"]:
        user_instance = User.objects.filter(created_groups__name=model_instance)[0]
        membership = Membership.objects.get_or_create(tavern_group=model_instance, join_date=timezone.now(), user=user_instance)
        return reverse('tavern_group_details', kwargs={"slug": model_instance})

post_save.connect(group_create, sender=TavernGroup)
