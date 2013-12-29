from django.contrib import admin

from .models import TavernGroup, Event, Attendee, Member

admin.site.register(TavernGroup)
admin.site.register(Event)
admin.site.register(Attendee)
admin.site.register(Member)
