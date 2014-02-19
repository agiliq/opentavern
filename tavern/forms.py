from django.forms import ModelForm

from .models import TavernGroup, Event


class CreateGroupForm(ModelForm):
    """ CreateGroupForm """
    class Meta:
        model = TavernGroup
        exclude = ['creator', 'organizers', 'slug']


class CreateEventForm(ModelForm):
    """ CreateEventForm """
    class Meta:
        model = Event
        exclude = ['creator', 'slug']
