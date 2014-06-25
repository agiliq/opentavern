from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from django.contrib.auth.models import User

from guardian.shortcuts import assign_perm, remove_perm

from .models import TavernGroup, Event


def create_event_permission(sender, instance, created, **kwargs):
    remove_perm('change_event', instance.creator, instance)
    remove_perm('delete_event', instance.creator, instance)
    remove_perm('change_event', instance.group.creator, instance)
    remove_perm('delete_event', instance.group.creator, instance)
    assign_perm('change_event', instance.creator, instance)
    assign_perm('delete_event', instance.creator, instance)
    assign_perm('change_event', instance.group.creator, instance)
    assign_perm('delete_event', instance.group.creator, instance)


def group_pre_save(sender, instance, **kwargs):
    if instance.pk:
        instance._old_m2m = set(list(instance.organizers.values_list('pk', flat=True)))
    else:
        instance._old_m2m = set(list())


def create_group_permission_for_organizers(sender, instance, action, reverse, pk_set, *args, **kwargs):
    # Assign permissions to all organizers of group
    if action == 'post_clear':
        for pk in instance._old_m2m:
            user = User.objects.get(pk=pk)
            remove_perm('change_taverngroup', user, instance)
            remove_perm('delete_taverngroup', user, instance)
    if action == 'post_add' and not reverse:
        for pk in pk_set:
            user = User.objects.get(pk=pk)
            assign_perm('change_taverngroup', user, instance)
            assign_perm('delete_taverngroup', user, instance)


def delete_group_permissions(sender, instance, **kwargs):
    remove_perm('change_taverngroup', instance.creator, instance)
    remove_perm('delete_taverngroup', instance.creator, instance)
    for user in instance.organizers.all():
        remove_perm('change_taverngroup', user, instance)
        remove_perm('delete_taverngroup', user, instance)


def delete_event_permissions(sender, instance, **kwargs):
    remove_perm('change_event', instance.creator, instance)
    remove_perm('delete_event', instance.creator, instance)
    remove_perm('change_event', instance.group.creator, instance)
    remove_perm('delete_event', instance.group.creator, instance)


post_save.connect(create_event_permission, sender=Event)
pre_save.connect(group_pre_save, sender=TavernGroup)
m2m_changed.connect(create_group_permission_for_organizers, sender=TavernGroup.organizers.through)
pre_delete.connect(delete_group_permissions, sender=TavernGroup)
pre_delete.connect(delete_event_permissions, sender=Event)
