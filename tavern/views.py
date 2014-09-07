""" Opentavern Views"""
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, get_list_or_404
from django.views.generic import DetailView
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin

from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import TavernGroup, Membership, Event, Attendee
from .forms import CreateGroupForm, CreateEventForm, UpdateEventForm, AddOrganizerForm, RemoveOrganizerForm
from .multiform import MultiFormsView


def today_date():
    today_object = timezone.now()
    today = today_object.isoformat()
    return today


def index(request, template='tavern/home.html'):
    """ index page """
    all_groups = TavernGroup.objects.all()
    if request.user.is_authenticated():
        joined_groups = request.user.tavern_groups.all()
        unjoined_groups = list(set(all_groups) - set(joined_groups))
        upcoming_events = Event.visible_events.upcoming()
        events = Attendee.objects.filter(user=request.user)
        events_rsvped = [event.event for event in events]

        context = {'joined_groups': joined_groups,
                   'unjoined_groups': unjoined_groups,
                   'upcoming_events': upcoming_events,
                   'events_rsvped': events_rsvped}
    else:
        context = {'groups': all_groups}
    return render(request, template, context)


@login_required
def rsvp(request, event_id, rsvp_status):
    """ View to set RSVP status for an event """
    event = get_object_or_404(Event, id=int(event_id))
    user = get_object_or_404(User, id=request.user.id)
    try:
        attendee = Attendee.objects.get(user=user,
                                        event=event)
        attendee.rsvp_status = rsvp_status
        attendee.rsvped_on = timezone.now()
        attendee.save()
    except Attendee.DoesNotExist:
        attendee = Attendee.objects.create(user=user,
                                           event=event,
                                           rsvp_status=rsvp_status,
                                           rsvped_on=timezone.now())

    if rsvp_status == 'yes':
        message = "You are attending this event."
    elif rsvp_status == 'no':
        message = "You are not attending this event."
    elif rsvp_status == 'maybe':
        message = "You may attend this event."

    return HttpResponse(message)


@login_required
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


class UpcomingEventsMixin(object):
    """ Add upcoming events to the view """
    def get_context_data(self, **kwargs):
        context = super(UpcomingEventsMixin, self).get_context_data(**kwargs)
        context['upcoming_events'] = Event.visible_events.upcoming()
        return context


class GroupDetail(UpcomingEventsMixin, DetailView):
    """ Group details Page """
    template_name = "group_details.html"
    context_object_name = "group"
    model = TavernGroup

    def get_context_data(self, **kwargs):
        context = super(GroupDetail, self).get_context_data(**kwargs)
        context['past_events'] = Event.visible_events.past()

        tavern_group = context['group']
        try:
            Membership.objects.get(tavern_group=tavern_group,
                                   user=self.request.user.id)
            user_is_member = True
        except Membership.DoesNotExist:
            user_is_member = False
        context['user_is_member'] = user_is_member

        recent_group_members = get_list_or_404(Membership, tavern_group=tavern_group)[:5]
        context["recent_group_members"] = recent_group_members

        return context


class EventDetail(UpcomingEventsMixin, DetailView):
    """ Give details about an event and its attendees"""
    template_name = "event_details.html"
    context_object_name = "event"
    model = Event

    def get_queryset(self, **kwargs):
        return self.model.visible_events.all()

    def get_context_data(self, **kwargs):
        context = super(EventDetail, self).get_context_data(**kwargs)
        event = context['event']
        try:
            attendee = Attendee.objects.get(user=self.request.user,
                                            event=event)
            if attendee.rsvp_status == 'yes':
                message = "You are attending this event."
            elif attendee.rsvp_status == 'no':
                message = "You are not attending this event."
            elif attendee.rsvp_status == 'maybe':
                message = "You may attend this event."
            context['attendee'] = attendee
        except Attendee.DoesNotExist:
            message = "You have not rsvped yet"
        context['attendee_rsvp'] = message

        context['event_attendees'] = Attendee.objects.filter(event=event,
                                                             rsvp_status="yes")
        context['editable'] = event.starts_at > timezone.now()
        return context


class GroupCreate(LoginRequiredMixin, CreateView):
    """ Create new group """
    form_class = CreateGroupForm
    model = TavernGroup
    template_name = "group_form.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(GroupCreate, self).form_valid(form)


class GroupUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """ Updates a group """
    model = TavernGroup
    form_class = CreateGroupForm
    template_name = 'group_form.html'
    permission_required = 'tavern.change_taverngroup'
    render_403 = True
    return_403 = True


class GroupDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TavernGroup
    permission_required = 'tavern.delete_taverngroup'
    render_403 = True
    return_403 = True

    def get_success_url(self, **kwargs):
        return reverse("index")


class EditOrganizers(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, MultiFormsView):
    template_name = "edit_organizers.html"
    form_classes = {'add': AddOrganizerForm,
                    'remove': RemoveOrganizerForm
                    }
    model = TavernGroup
    permission_required = 'tavern.delete_taverngroup'
    render_403 = True
    return_403 = True

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(EditOrganizers, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(EditOrganizers, self).post(request, *args, **kwargs)

    def get_remove_initial(self):
        return {'group': self.object.pk}

    def add_form_valid(self, form):
        for user in form.cleaned_data['users']:
            self.object.organizers.add(user)
        return HttpResponseRedirect(self.get_success_url())

    def remove_form_valid(self, form):
        for user in form.cleaned_data['users']:
            self.object.organizers.remove(user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, **kwargs):
        return reverse('tavern_group_details', kwargs={'slug': self.object.slug})


class EventCreate(LoginRequiredMixin, CreateView):
    """ Creates new Event """
    form_class = CreateEventForm
    model = Event
    template_name = "event_form.html"

    def get_form_kwargs(self):
        kwargs = super(EventCreate, self).get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(EventCreate, self).form_valid(form)


class EventUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """ Update an Event """
    model = Event
    form_class = UpdateEventForm
    template_name = 'event_form.html'
    permission_required = 'tavern.change_event'
    render_403 = True
    return_403 = True


class EventDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Event
    permission_required = 'tavern.delete_event'
    render_403 = True
    return_403 = True

    def get_success_url(self, **kwargs):
        return reverse("tavern_group_details", kwargs={"slug": self.object.group.slug})


class RsvpDelete(LoginRequiredMixin, DeleteView):
    """ Remove a RSVP"""
    model = Attendee

    def get_success_url(self, **kwargs):
        return reverse("tavern_event_details", kwargs={"slug": self.object.event.slug})


tavern_group_update = GroupUpdate.as_view()
tavern_event_update = EventUpdate.as_view()
create_group = GroupCreate.as_view()
create_event = EventCreate.as_view()
event_details = EventDetail.as_view()
group_details = GroupDetail.as_view()
group_delete = GroupDelete.as_view()
event_delete = EventDelete.as_view()
delete_rsvp = RsvpDelete.as_view()
edit_organizers = EditOrganizers.as_view()
