from django import template

from tavern.models import get_users_attending_event
from tavern.models import get_users_not_attending_event

register = template.Library()


class EventTemplateTagMixin(template.Node):
    def __init__(self, event, local_variable):
        """Instantiating the name of the variable to
        be resolve and calling variable.resolve(context)"""
        self.event = template.Variable(event)
        self.var = local_variable


class TavernAttendeeUsers(EventTemplateTagMixin, template.Node):
    def __init__(self, event, local_variable):
        super(TavernAttendeeUsers, self).__init__(event, local_variable)

    def render(self, context):
        try:
            event = self.event.resolve(context)
        except:
            raise template.TemplateSyntaxError("Should be event instance")
        users_attending_event = get_users_attending_event(event)
        context[self.var] = users_attending_event
        return ''


class TavernNotAttendeeUsers(EventTemplateTagMixin, template.Node):
    def __init__(self, event, local_variable):
        super(TavernNotAttendeeUsers, self).__init__(event, local_variable)

    def render(self, context):
        try:
            event = self.event.resolve(context)
        except:
            raise template.TemplateSyntaxError("Should be event instance")
        users_not_attending_event = get_users_not_attending_event(event)
        context[self.var] = users_not_attending_event
        return ''


@register.tag
def get_tavern_attendees(parser, token):
    """gets all the users who are attending the event"""
    try:
        tag_name, for_keyword, event, as_keyword, var = token.split_contents()
    except:
        raise template.TemplateSyntaxError("Invalid argument type")
    return TavernAttendeeUsers(event, var)


@register.tag
def get_tavern_not_attendees(parser, token):
    """gets all the users who are not attending the event"""
    try:
        tag_name, for_keyword, event, as_keyword, var = token.split_contents()
    except:
        raise template.TemplateSyntaxError("Invalid argument type")
    return TavernNotAttendeeUsers(event, var)
