""" Opentavern Forms """

from django.forms import ModelForm
from .models import Group


class CreateGroupForm(ModelForm):
    """ CreateGroupForm """
    class Meta:
        model = Group
