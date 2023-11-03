from django import template
from ..views import get_notifications

register = template.Library()

@register.inclusion_tag('chest_requests.html', takes_context=True)
def display_notifications(context):
    request = context['request']  # Get the request from the context
    notifications_list = get_notifications(request)
    return {'requests_list': notifications_list}