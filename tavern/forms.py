""" Opentavern Forms """

from django.forms import ModelForm
from .models import TavernGroup


class CreateGroupForm(ModelForm):
    """ CreateGroupForm """
    class Meta:
        model = TavernGroup
