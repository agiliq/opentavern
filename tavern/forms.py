from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime

from .models import TavernGroup, Event


class CreateGroupForm(forms.ModelForm):
    """ CreateGroupForm """
    class Meta:
        model = TavernGroup
        exclude = ['creator', 'organizers', 'members', 'slug']


class CreateEventForm(forms.ModelForm):
    """ CreateEventForm """
    event_time = forms.CharField(max_length=50, required=True)

    class Meta:
        model = Event
        exclude = ['creator', 'slug', 'starts_at', 'ends_at']

    def __init__(self, *args, **kwargs):
            self.user = kwargs.pop('user', None)
            super(CreateEventForm, self).__init__(*args, **kwargs)
            self.fields['group'].queryset = self.user.tavern_groups.all()

    def save(self, commit=True):
        event = super(CreateEventForm, self).save(commit=False)
        event_time = self.cleaned_data['event_time'].split(" - ")
        start_time = datetime.strptime(event_time[0], '%d/%m/%Y %I:%M %p')
        end_time = datetime.strptime(event_time[1], '%d/%m/%Y %I:%M %p')
        event.starts_at = start_time
        event.ends_at = end_time
        if commit:
            event.save()
        return event


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
