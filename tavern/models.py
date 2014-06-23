# pylint: disable=method-hidden
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.urlresolvers import reverse

from django.db.models.signals import post_save, pre_delete
from guardian.shortcuts import assign_perm
from guardian.models import UserObjectPermission

from .slugify import unique_slugify


class TavernGroup(models.Model):
    "Similar interests group, create events for these"
    name = models.CharField(max_length=40, unique=True)
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
    organizers = models.ManyToManyField(User, related_name="organizes_groups")
    members = models.ManyToManyField(User, through="Membership", related_name="tavern_groups")
    slug = models.SlugField(max_length=50)

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
    user = models.ForeignKey(User, related_name='tgroup_memberships')
    tavern_group = models.ForeignKey(TavernGroup, related_name='memberships')
    join_date = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s" % (self.user.username, self.tavern_group.name)


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

    class Meta:
        unique_together = ('group', 'name')

    def get_absolute_url(self):
        return reverse("tavern_event_details", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(Event, self).save(*args, **kwargs)
        # Old check: if event creator is member of that group
        # but it should display only those groups which the user is member of and then
        # check in form validation and return error
        Attendee.objects.get_or_create(
            user=self.creator,
            event=self,
            defaults={'rsvped_on': timezone.now().isoformat(),
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


def create_event_permission(sender, instance, created, **kwargs):
    if created:
        assign_perm('change_event', instance.creator, instance)
        assign_perm('delete_event', instance.creator, instance)
    # Assign permissions to creator of the group
        assign_perm('change_event', instance.group.creator, instance)
        assign_perm('delete_event', instance.group.creator, instance)
    # Assign permissions to all organizers of group
    for user in instance.group.organizers.all():
        assign_perm('change_event', user, instance)
        assign_perm('delete_event', user, instance)


def create_group_permission(sender, instance, created, **kwargs):
    if created:
        assign_perm('change_taverngroup', instance.creator, instance)
        assign_perm('delete_taverngroup', instance.creator, instance)
    # Assign permissions to all organizers of group
    for user in instance.organizers.all():
        assign_perm('change_event', user, instance)
        assign_perm('delete_event', user, instance)


def delete_orphaned_permissions(sender, instance, **kwargs):
    UserObjectPermission.objects.filter(
            user=instance.creator,
            content_type=ContentType.objects.get_for_model(instance),
            object_pk=instance.pk).delete()

post_save.connect(create_event_permission, sender=Event)
post_save.connect(create_group_permission, sender=TavernGroup)
pre_delete.connect(delete_orphaned_permissions, sender=Event)
pre_delete.connect(delete_orphaned_permissions, sender=TavernGroup)
