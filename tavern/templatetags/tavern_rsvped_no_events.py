from django import template
from tavern.models import get_rsvped_no_events

register = template.Library()


class TavernEventNoRsvped(template.Node):
    def __init__(self, user, var_name):
        """ Instantiating with the name of the variable
        to be resolved and calling variable.resolve(context)"""
        self.user = template.Variable(user)
        self.var_name = var_name

    def render(self, context):
        user = self.user.resolve(context)
        Events_for_rsvped_no = get_rsvped_no_events(user)
        context[self.var_name] = Events_for_rsvped_no
        return ''


@register.tag
def get_user_tavern_rsvped_no_events(parser, token):
    """gets the events for which the rsvped NO"""
    args = token.split_contents()
    var_name = args[-1]
    arg_variable = args.index('request.user')
    user = args[arg_variable]
    return TavernEventNoRsvped(user, var_name)
