from django import template
from tavern.models import get_rsvped_no_events

register = template.Library()


class UserTavernRsvpNoEvents(template.Node):
    def __init__(self, user, local_var):
        self.user = template.Variable(user)
        self.var = local_var

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except:
            raise template.TemplateSyntaxError("Should be user instance")
        rsvp_no_events = get_rsvped_no_events(user)
        context[self.var] = rsvp_no_events
        return ''

@register.tag
def get_user_tavern_rsvped_no_events(parser, token):
    """gets the events for which the rsvped NO"""
    try:
        tag_name, for_keyword, user, as_keyword, var = token.split_contents()
    except:
        raise template.TemplateSyntaxError("Invalid argument type")
    return UserTavernRsvpNoEvents(user, var)
