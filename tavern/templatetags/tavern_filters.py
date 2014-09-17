import re
import pdb
from django import template

from tavern.models import TavernGroup
from tavern.models import get_groups
from tavern.models import get_rsvp_yes_events

register = template.Library()


class UserTemplateTagMixin(template.Node):
    def __init__(self, user, var_name):
        self.user = template.Variable(user)
        self.var_name = var_name


class UserTavernGroups(UserTemplateTagMixin, template.Node):
    def __init__(self, user, var_name):
        super(UserTavernGroups, self).__init__(user, var_name)

    def render(self, context):
        user = self.user.resolve(context)
        user_groups = get_groups(user)
        context[self.var_name] = user_groups
        return ''


class AllTavernGroups(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        all_groups = TavernGroup.objects.all()
        context[self.var_name] = all_groups
        return ''


class UserTavernRsvpEvents(UserTemplateTagMixin, template.Node):

    def __init__(self, user, var_name):
        super(UserTavernRsvpEvents, self).__init__(user, var_name)

    def render(self, context):
        user = self.user.resolve(context)
        events = get_rsvp_yes_events(user)
        context[self.var_name] = events
        return ''


@register.tag
def get_user_tavern_groups(parser, token):
    tag_elements = token.split_contents()
    var_name = tag_elements[-1]
    arg_index = tag_elements.index('request.user')
    user = tag_elements[arg_index]
    return UserTavernGroups(user, var_name)


@register.tag
def get_all_tavern_groups(parser, token):
    tag_name, arg = token.contents.split(None, 1)
    m = re.search(r'as (\w+)', arg)
    var_name = m.groups()[0]
    return AllTavernGroups(var_name)


@register.tag
def get_user_tavern_rsvp_yes_events(parser, token):
    tag_name, arg = token.contents.split(None, 1)
    m = re.search(r'for (\w+.\w+) as (\w+)', arg)
    user, var_name = m.groups()
    return UserTavernRsvpEvents(user, var_name)
