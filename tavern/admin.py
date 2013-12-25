from django.contrib import admin

from .models import Group, Event, Attendee

admin.site.register(Group)
admin.site.register(Event)
admin.site.register(Attendee)
