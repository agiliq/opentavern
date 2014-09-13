import re

from django import template

from tavern.models import Attendee

register = template.Library()


class TavernEventNoRsvped(template.Node):
    def __init__(self, event, var_name):
        self.event = template.Variable(event)
        self.var_name = var_name

    def render(self, context):
        event = self.event.resolve(context)
        Events_for_rsvped_no = event.attendee_set.filter(rsvp_status="no")
        context[self.var_name] = Events_for_rsvped_no
        return ''


@register.tag
def get_user_tavern_rsvped_no_events(parser, token):
    tag_name, arg = token.contents.split(None, 1)
    m = re.search(r'for (\w+.\w+) as (\w+)', arg)
    event, var_name = m.groups()
    return TavernEventNoRsvped(event, var_name)
