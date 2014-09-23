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
        if not user.__class__.__name__ == "User":
            raise template.TemplateSyntaxError("Invalid arguments passed."
                        "Argument should be an instance of User")
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
        if not user.__class__.__name__ == 'User':
            raise template.TemplateSyntaxError("Invalid argument type passed."
                " Argument should be an instance of user")
        events = get_rsvp_yes_events(user)
        context[self.var_name] = events
        return ''


@register.tag
def get_user_tavern_groups(parser, token):
    """ returns all the groups in which is a member
    {% get_user_tavern_groups for request.user as user_tavern_groups %}"""
    try:
        tag_name, for_contxt, user, as_contxt, var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(("%r tag is not correct Ex: "
            "get_user_tavern_groups for user as tavern_groups") % token.split_contents()[0])
    return UserTavernGroups(user, var)


@register.tag
def get_all_tavern_groups(parser, token):
    """returns all the tavern groups
    {% get_all_tavern_groups as tavern_groups %}"""
    try:
        tag_name, as_contxt, variable = token.split_contents()
    except:
        raise template.TemplateSyntaxError(("Invalid template tag %r."
            " Ex: get_all_tavern_groups as tavern_groups") % token.split_contents()[0])
    return AllTavernGroups(variable)


@register.tag
def get_user_tavern_rsvp_yes_events(parser, token):
    """returns all the events in which user has assigned rsvp as yes
    {% get_user_tavern_rsvp_yes_events for request.user as attending_events %}
    """
    try:
        tag_name, for_contxt, user, as_contxt, var = token.split_contents()
    except:
        raise template.TemplateSyntaxError(("Invalid template tag %r"
                    "Ex: get_user_tavern_rsvp_yes_events for user as"
                    "attending_events"), token.split_contents()[0])
    return UserTavernRsvpEvents(user, var)
