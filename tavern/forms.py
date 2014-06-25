from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import HiddenInput

from .models import TavernGroup, Event, Membership
from bootstrap3_datetime.widgets import DateTimePicker


class CreateGroupForm(forms.ModelForm):
    """ CreateGroupForm """
    class Meta:
        model = TavernGroup
        exclude = ['creator', 'organizers', 'members', 'slug']


class CreateEventForm(forms.ModelForm):
    """ CreateEventForm """

    class Meta:
        model = Event
        exclude = ['creator', 'slug', 'show']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('current_user', None)
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = self.user.tavern_groups.all()
        self.fields['starts_at'].widget = DateTimePicker(options={"format": "YYYY-MM-DD HH:mm", })
        self.fields['ends_at'].widget = DateTimePicker(options={"format": "YYYY-MM-DD HH:mm", })

    def clean(self):
        cleaned_data = super(CreateEventForm, self).clean()
        group = cleaned_data.get('group')
        try:
            Membership.objects.get(user=self.user, tavern_group=group)
        except Membership.DoesNotExist:
            raise forms.ValidationError("You are not a member of this group")
        return cleaned_data


class UpdateEventForm(forms.ModelForm):
    """ Change Event Details """

    class Meta:
        model = Event
        exclude = ['creator', 'slug', 'show', 'group']

    def __init__(self, *args, **kwargs):
        super(UpdateEventForm, self).__init__(*args, **kwargs)
        self.fields['starts_at'].widget = DateTimePicker(options={"format": "YYYY-MM-DD HH:mm", })
        self.fields['ends_at'].widget = DateTimePicker(options={"format": "YYYY-MM-DD HH:mm", })


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


class AddOrganizerForm(forms.Form):
    usernames = forms.CharField()

    def clean(self):
        cleaned_data = super(AddOrganizerForm, self).clean()
        usernames = cleaned_data.get('usernames')
        cleaned_data['users'] = []
        for username in usernames.split(','):
            try:
                user = User.objects.get(username=username.strip())
                cleaned_data['users'].append(user)
            except User.DoesNotExist:
                raise forms.ValidationError("%s is not a user" % username.strip())
        return cleaned_data


class RemoveOrganizerForm(AddOrganizerForm):
    group = forms.CharField(max_length=5)

    def __init__(self, *args, **kwargs):
        super(RemoveOrganizerForm, self).__init__(*args, **kwargs)
        self.fields['group'].widget = HiddenInput()

    def clean(self):
        cleaned_data = super(RemoveOrganizerForm, self).clean()
        users = cleaned_data.get('users')
        group = TavernGroup.objects.get(pk=cleaned_data['group'])
        for user in users:
            try:
                group.organizers.get(username=user.username)
            except User.DoesNotExist:
                raise forms.ValidationError("%s is not an organizer of %s group" % (user.username, group.name))
        return cleaned_data
