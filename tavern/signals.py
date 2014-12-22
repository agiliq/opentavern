from django.db.models.signals import pre_save

from .models import TavernGroup


def group_pre_save(sender, instance, **kwargs):
    if instance.pk:
        instance._old_m2m = set(list(instance.organizers.values_list('pk', flat=True)))
    else:
        instance._old_m2m = set(list())

pre_save.connect(group_pre_save, sender=TavernGroup)
