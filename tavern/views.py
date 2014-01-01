""" Opentavern Views"""

import json
from datetime import date, timedelta

from .models import TavernGroup, Member, Event, Attendee
from .forms import CreateGroupForm


from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render


today_object = timezone.now()
today = today_object.isoformat()
seven_days_before_today = date.today() - timedelta(7)

last_week = [seven_days_before_today, today]


def index(request, template='home.html'):
    """ index page """
    if request.user.is_authenticated():
        # import ipdb; ipdb.set_trace()
        groups = request.user.taverngroup_set.all()
        upcoming_events = Event.objects.filter(starts_at__gt=today)
        # import ipdb; ipdb.set_trace()
        events_rsvped = Attendee.objects.filter(user_id=request.user.id)

        context = {'groups': groups,
                   'upcoming_events': upcoming_events,
                   'events_rsvped': events_rsvped}
    else:
        groups = TavernGroup.objects.all()
        context = {'groups': groups}
    return render(request, template, context)


def group_details(request, group_id):
    """ Group Details Page"""
    template = "group_details.html"
    upcoming_events = Event.objects.filter(starts_at__gt=today)
    past_events = Event.objects.filter(starts_at__lt=today)
    recent_group_members = Member.objects.all().order_by('-join_date')[:5]

    context = {"upcoming_events": upcoming_events,
               "past_events": past_events,
               "recent_group_members": recent_group_members}

    try:
        group = TavernGroup.objects.get(id=group_id)
        context.update({'group': group})
    except ObjectDoesNotExist:
        return render(request, '404.html', context)

    return render(request, template, context)


def event_details(request, event_id):
    """ Event Details View """
    template = "event_details.html"
    upcoming_events = Event.objects.filter(starts_at__gt=today)
    event_attendees = Attendee.objects.filter(event__id=event_id,
                                              rsvp_status="yes")
    context = {"upcoming_events": upcoming_events,
               "event_attendees": event_attendees}
    try:
        event = Event.objects.get(id=event_id)
        context.update({'event': event})
    except ObjectDoesNotExist:
        return render(request, '404.html', context)

    return render(request, template, context)


def rsvp(request,  event_id, rsvp_status):
    """ View to set RSVP status for an event """
    attendee = Attendee.objects.get_or_create(user__id=request.user.id,
                                              event__id=event_id)
    attendee.rsvp_status = rsvp_status
    attendee.rsvped_on = timezone.now()
    attendee.save()

    message = 'Successfully Chaged your RSVP status. '
    if rsvp_status == 'yes':
        message += "You are attending this event."
    elif rsvp_status == 'no':
        message += "You are not attending this event."
    elif rsvp_status == 'maybe':
        message += "You may attend this event."

    response = {'message': message}
    return json.dumps(response)


def create_group(request, template='create_group.html'):
    """ index page """
    form = CreateGroupForm()
    context = {'form': form}
    return render(request, template, context)
