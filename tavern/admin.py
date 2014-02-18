from django.contrib import admin

from .models import TavernGroup, Event, Attendee, Member


class GroupAdmin(admin.ModelAdmin):
    exclude = ('slug',)


class EventAdmin(admin.ModelAdmin):
    exclude = ('slug',)

admin.site.register(TavernGroup, GroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Attendee)
admin.site.register(Member)
