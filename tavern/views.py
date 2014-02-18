""" Opentavern Views"""

import json
from datetime import date, timedelta

from .models import TavernGroup, Member, Event, Attendee
from .forms import CreateGroupForm, CreateEventForm

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


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


def group_details(request, slug):
    """ Group Details Page"""
    template = "group_details.html"
    upcoming_events = Event.objects.filter(starts_at__gt=today)
    past_events = Event.objects.filter(starts_at__lt=today)
    recent_group_members = Member.objects.all().order_by('-join_date')[:5]

    context = {"upcoming_events": upcoming_events,
               "past_events": past_events,
               "recent_group_members": recent_group_members}

    try:
        group = TavernGroup.objects.get(slug=slug)
        context.update({'group': group})
    except ObjectDoesNotExist:
        return render(request, '404.html', context)

    return render(request, template, context)


def event_details(request, slug):
    """ Event Details View """
    template = "event_details.html"
    upcoming_events = Event.objects.filter(starts_at__gt=today)
    event_attendees = Attendee.objects.filter(event__slug=slug,
                                              rsvp_status="yes")
    context = {"upcoming_events": upcoming_events,
               "event_attendees": event_attendees}
    try:
        event = Event.objects.get(slug=slug)
        context.update({'event': event})
    except ObjectDoesNotExist:
        return render(request, '404.html', context)

    return render(request, template, context)


def rsvp(request, event_id, rsvp_status):
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


@login_required
def create_group(request, template='create_group.html'):
    # pylint: disable=E1103
    """ index page """
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            Member.objects.create(user=request.user,
                                  tavern_group=group,
                                  join_date=today_object)
            return redirect("index")

    context = {'form': form}
    return render(request, template, context)


class GroupUpdate(UpdateView):
    model = TavernGroup
    form_class = CreateGroupForm
    template_name = 'tavern_group_update.html'

tavern_group_update = GroupUpdate.as_view()


@login_required
def create_event(request, template='create_event.html'):
    # pylint: disable=E1103
    form = CreateEventForm()
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            return redirect(reverse("event_details",
                                    kwargs={'slug': event.slug}))

    context = {'form': form}
    return render(request, template, context)


class EventUpdate(UpdateView):
    model = Event
    form_class = CreateEventForm
    template_name = 'tavern_event_update.html'

tavern_event_update = EventUpdate.as_view()


@login_required
def change_password(request, template='change_password.html'):
    form = PasswordChangeForm(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            context = {'form': form, 'success': True}
            return render(request, template, context)

    context = {'form': form}
    return render(request, template, context)


def signup(request, template='signup.html'):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            context = {'form': form, 'success': True}
            return render(request, template, context)

    context = {'form': form}
    return render(request, template, context)
