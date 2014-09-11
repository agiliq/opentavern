from django import template

from tavern.models import get_unjoined_groups

register = template.Library()


@register.assignment_tag
def get_user_tavern_unjoined_groups(user):
    user_unjoined_groups = get_unjoined_groups(user)
    return user_unjoined_groups
