from django import template

from tavern.models import get_unjoined_groups

register = template.Library()


class UserUnjoinedTavernGroup(template.Node):
    """Instantiating the name of the variable to be resolved
    and calling variable.resolve(context)"""
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
    """gets all unjoined groups for a user"""
    try:
        tag_name, for_keyword, user, as_keyword, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag is invalid. use 'get_user_tavern_unjoined_groups for request.user/user in user_tavern_unjoined_groups'" % token.contents.split()[0])
    user = token.split_contents()[2]
    return UserUnjoinedTavernGroup(user, var_name)
