from django import template

from tavern.models import get_groups

register = template.Library()


@register.assignment_tag
def get_user_tavern_groups(user):
    user_groups = get_groups(user)
    return user_groups
