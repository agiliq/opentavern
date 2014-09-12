import re

from django import template

from tavern.models import TavernGroup
from tavern.models import get_groups

register = template.Library()


class UserTavernGroups(template.Node):
    def __init__(self, user, var_name):
        self.user = template.Variable(user)
        self.var_name = var_name

    def render(self, context):
        user = self.user.resolve(context)
        user_groups = get_groups(user)
        context[self.var_name] = user_groups
        return ''


@register.tag
def get_user_tavern_groups(parser, token):
    tag_name, arg = token.contents.split(None, 1)
    m = re.search(r'for (\w+.\w+) as (\w+)', arg)
    user, var_name = m.groups()
    return UserTavernGroups(user, var_name)
