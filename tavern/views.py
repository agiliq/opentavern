from django.shortcuts import render
from .forms import CreateGroupForm


def index(request, template='home.html'):
    """ index page """
    form = CreateGroupForm()
    context = {'form': form}
    return render(request, template, context)
