from django.contrib import admin

from .models import TavernGroup, Event, Attendee, Membership


class GroupAdmin(admin.ModelAdmin):
    exclude = ('slug',)


class EventAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ['name', 'group', 'starts_at', 'ends_at', 'show']
    list_editable = ['show', ]
    list_filter = ['show', ]
    date_hierarchy = 'starts_at'

admin.site.register(TavernGroup, GroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Attendee)
admin.site.register(Membership)
