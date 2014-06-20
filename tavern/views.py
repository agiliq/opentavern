""" Opentavern Views"""
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, CreateView, UpdateView

from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import TavernGroup, Membership, Event, Attendee
from .forms import CreateGroupForm, CreateEventForm


def today_date():
    today_object = timezone.now()
    today = today_object.isoformat()
    return today


def index(request, template='home.html'):
    """ index page """
    all_groups = TavernGroup.objects.all()
    if request.user.is_authenticated():
        joined_groups = request.user.tavern_groups.all()
        unjoined_groups = list(set(all_groups) - set(joined_groups))
        upcoming_events = Event.objects.filter(starts_at__gt=today_date())
        events = Attendee.objects.filter(user_id=request.user.id)
        events_rsvped = [event.event for event in events]

        context = {'joined_groups': joined_groups,
                   'unjoined_groups': unjoined_groups,
                   'upcoming_events': upcoming_events,
                   'events_rsvped': events_rsvped}
    else:
        context = {'groups': all_groups}
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
            Membership.objects.get(tavern_group=tavern_group,
                               user=self.request.user.id)
            user_is_member = True
        except Membership.DoesNotExist:
            user_is_member = False
        context['user_is_member'] = user_is_member

        # Raise 404 when there are no members in that group. TODO: is 404 it needed?
        try:
            recent_group_members = Membership.objects.filter(
                tavern_group=tavern_group).order_by('-join_date')[:5]
        except Membership.DoesNotExist:
            raise Http404
        context["recent_group_members"] = recent_group_members

        return context


group_details = GroupDetail.as_view()


def tavern_toggle_member(request):
    """
    Adds a member to the group if he's not in the group, or
    deletes a member if he's already a member
    """

    user = get_object_or_404(User, id=request.POST.get('user_id'))
    group = get_object_or_404(TavernGroup, slug=request.POST.get('slug'))
    try:
        member = Membership.objects.get(user=user, tavern_group=group)
        response = "Join Group"
        member.delete()
    except Membership.DoesNotExist:
        member = Membership.objects.create(
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
        event = context['event']

        context['event_attendees'] = Attendee.objects.filter(event=event, rsvp_status="yes")
        context['editable'] = event.starts_at > timezone.now()
        return context

event_details = EventDetail.as_view()

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


class GroupCreate(LoginRequiredMixin, CreateView):
    form_class = CreateGroupForm
    model = TavernGroup
    template_name = "create_group.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(GroupCreate, self).form_valid(form)


create_group = GroupCreate.as_view()


class GroupUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TavernGroup
    form_class = CreateGroupForm
    template_name = 'tavern_group_update.html'
    permission_required = 'tavern.change_taverngroup'
    render_403 = True
    return_403 = True

tavern_group_update = GroupUpdate.as_view()


class EventCreate(LoginRequiredMixin, CreateView):
    form_class = CreateEventForm
    model = Event
    template_name = "create_event.html"

    def get_form_kwargs(self):
        kwargs = super(EventCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(EventCreate, self).form_valid(form)


create_event = EventCreate.as_view()


class EventUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Event
    form_class = CreateEventForm
    template_name = 'tavern_event_update.html'
    permission_required = 'tavern.change_event'
    render_403 = True
    return_403 = True

tavern_event_update = EventUpdate.as_view()
