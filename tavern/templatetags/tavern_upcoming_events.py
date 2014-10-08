from django import template

from tavern.models import get_upcoming_events

register = template.Library()


class TavernUpcomingEvents(template.Node):
    def __init__(self, user, local_variable):
        """Instantiating the name of the variable to
        resolve and calling varible.resolve(context)"""
        self.user = template.Variable(user)
        self.var = local_variable

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except:
            raise template.TemplateSyntaxError("Should be user instance")
        upcoming_events_for_user_joined_groups = get_upcoming_events(user)
        context[self.var] = upcoming_events_for_user_joined_groups
        return ''


@register.tag
def get_tavern_upcoming_events(parser, token):
    """gets the upcoming events for which the user joined group"""
    try:
        tag_name, for_keyword, user, as_keyword, var = token.split_contents()
    except:
        raise template.TemplateSyntaxError("Invalid argument type")
    return TavernUpcomingEvents(user, var)
