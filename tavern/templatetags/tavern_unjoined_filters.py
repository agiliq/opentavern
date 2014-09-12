import re

from django import template

from tavern.models import get_unjoined_groups

register = template.Library()


class UserUnjoinedTavernGroup(template.Node):
    def __init__(self, user, var_name):
        self.user = template.Variable(user)
        self.var_name = var_name

    def render(self, context):
        user = self.user.resolve(context)
        user_unjoined_groups = get_unjoined_groups(user)
        context[self.var_name] = user_unjoined_groups
        return ''


@register.tag
def get_user_tavern_unjoined_groups(parser, token):
    tag_name, arg = token.contents.split(None, 1)
    m = re.search(r'for (\w+.\w+) as (\w+)', arg)
    user, var_name = m.groups()
    return UserUnjoinedTavernGroup(user, var_name)
