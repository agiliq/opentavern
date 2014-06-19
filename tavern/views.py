""" Opentavern Views"""
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from .models import TavernGroup, Member, Event, Attendee
from .forms import CreateGroupForm, CreateEventForm


def today_date():
    today_object = timezone.now()
    today = today_object.isoformat()
    return today


def index(request, template='home.html'):
    """ index page """
    if request.user.is_authenticated():
        groups = request.user.tavern_groups.all()
        joined_groups = [group.tavern_group for group in groups]
        all_groups = TavernGroup.objects.all()
        unjoined_groups = list(set(all_groups) - set(joined_groups))
        upcoming_events = Event.objects.filter(starts_at__gt=today_date())
        events = Attendee.objects.filter(user_id=request.user.id)
        events_rsvped = [event.event for event in events]

        context = {'joined_groups': joined_groups,
                   'unjoined_groups': unjoined_groups,
                   'upcoming_events': upcoming_events,
                   'events_rsvped': events_rsvped}
    else:
        joined_groups = TavernGroup.objects.all()
        context = {'joined_groups': joined_groups}
    return render(request, template, context)


class UpcomingEventsMixin(object):
    """ Add upcoming events to the view """
    def get_context_data(self, **kwargs):
        context = super(UpcomingEventsMixin, self).get_context_data(**kwargs)
        context['upcoming_events'] = Event.objects.filter(starts_at__gt=today_date())
        return context



class GroupDetail(UpcomingEventsMixin, DetailView):
    """ Group details Page """
    template_name = "group_details.html"
    context_object_name = "group"
    model = TavernGroup

    def get_context_data(self, **kwargs):
        context = super(GroupDetail, self).get_context_data(**kwargs)
        context['past_events'] = Event.objects.filter(starts_at__lt=today_date())

        tavern_group = context['group']
        try:
            Member.objects.get(tavern_group=tavern_group,
                               user=self.request.user)
            user_is_member = True
        except Member.DoesNotExist:
            user_is_member = False
        context['user_is_member'] = user_is_member

        # Raise 404 when there are no members in that group. TODO: is 404 it needed?
        try:
            recent_group_members = Member.objects.filter(
                tavern_group=tavern_group).order_by('-join_date')[:5]
        except Member.DoesNotExist:
            raise Http404
        context["recent_group_members"] = recent_group_members

        return context


def tavern_toggle_member(request):
    """
    Adds a member to the group if he's not in the group, or
    deletes a member if he's already a member
    """

    user = get_object_or_404(User, id=request.POST.get('user_id'))
    group = get_object_or_404(TavernGroup, slug=request.POST.get('slug'))
    try:
        member = Member.objects.get(user=user, tavern_group=group)
        response = "Join Group"
        member.delete()
    except Member.DoesNotExist:
        member = Member.objects.create(
            user=user,
            tavern_group=group,
            join_date=today_date())
        response = "Unjoin Group"
    return HttpResponse(response)


class EventDetail(UpcomingEventsMixin, DetailView):
    template_name = "event_details.html"
    context_object_name = "event"
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventDetail, self).get_context_data(**kwargs)
        context['event_attendees'] = Attendee.objects.filter(event__slug=self.kwargs['slug'],
                                              rsvp_status="yes")
        try:
            event = Event.objects.get(slug=self.kwargs['slug'], creator=self.request.user)
            # condition to test if the event has already started.
            editable = event.starts_at > timezone.now()
        except Event.DoesNotExist:
            editable = False
        context['editable'] = editable
        return context


# def rsvp(request, event_id, rsvp_status):
#     """ View to set RSVP status for an event """
#     attendee = Attendee.objects.get_or_create(user__id=request.user.id,
#                                               event__id=event_id)
#     attendee.rsvp_status = rsvp_status
#     attendee.rsvped_on = timezone.now()
#     attendee.save()

#     message = 'Successfully Chaged your RSVP status. '
#     if rsvp_status == 'yes':
#         message += "You are attending this event."
#     elif rsvp_status == 'no':
#         message += "You are not attending this event."
#     elif rsvp_status == 'maybe':
#         message += "You may attend this event."

#     response = {'message': message}
#     return json.dumps(response)


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
            return redirect("tavern_group_details", slug=group.slug)

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
            return redirect(reverse("tavern_event_details",
                                    kwargs={'slug': event.slug}))

    context = {'form': form}
    return render(request, template, context)


class EventUpdate(UpdateView):
    model = Event
    form_class = CreateEventForm
    template_name = 'tavern_event_update.html'

tavern_event_update = EventUpdate.as_view()
