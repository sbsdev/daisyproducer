# http://djangosnippets.org/snippets/847/
from django.utils.encoding import force_unicode
from django import template

register = template.Library()

@register.filter
def in_group(user, groups):
    """Returns a boolean if the user is in the given group, or comma-separated
    list of groups.
    
    Usage::

        {% if user|in_group:"Friends" %}
        ...
        {% endif %}

    or::

        {% if user|in_group:"Friends,Enemies" %}
        ...
        {% endif %}

    """
    if user.is_authenticated():
        group_list = force_unicode(groups).split(',')
        return bool(user.groups.filter(name__in=group_list).values('name'))
    else:
        return False
