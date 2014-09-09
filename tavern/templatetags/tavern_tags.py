from django import template

register = template.Library()

class UserGroupsNode(template.Node):
    def __init__(self, user_string, context_name):
        self.user_to_be_used = template.Variable(user_string)
        self.context_name = context_name
        pass

    def render(self, context):
        self.user = self.user_to_be_used.resolve(context)
        context[self.context_name] = self.user.tavern_groups.all()
        return ''

def do_get_user_groups(parser, token):
    """
    {% get_user_groups for request.user as user_groups %}
    """
    try:
        tag_name, for_keyword, user_string, as_keyword, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Erong")
    return UserGroupsNode(user_string, context_name)

register.tag('get_user_groups', do_get_user_groups)

@register.simple_tag
def user_groups(user):
    return user.username
