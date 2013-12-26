""" Opentavern Views"""

import datetime

from django.shortcuts import render
from .models import Group, Event


today = datetime.datetime.now()


def index(request, template='home.html'):
    """ index page """
    if request.user.is_authenticated():
        # groups = request.user.groups_users.all()
        groups = []
    else:
        groups = Group.objects.all()

    # upcoming_events = Event.objects.filter("starts_at" > today)
    upcoming_events = Event.objects.all()
    context = {'groups': groups, 'upcoming_events': upcoming_events}
    return render(request, template, context)


def group_details(request, group_id):
    template = "group_details.html"
    # upcoming_events = Event.objects.filter("starts_at" > today)
    upcoming_events = Event.objects.all()

    context = {"upcoming_events": upcoming_events}

    try:
        group = Group.objects.get(id=group_id)
        context.update({'group': group})
    except:
        return render(request, '404.html', context)

    return render(request, template, context)


def event_details(request, event_id):
    template = "event_details.html"
    upcoming_events = Event.objects.all()
    context = {"upcoming_events": upcoming_events}
    try:
        event = Event.objects.get(id=event_id)
        context.update({'event': event})
    except:
        return render(request, '404.html', context)

    return render(request, template, context)
