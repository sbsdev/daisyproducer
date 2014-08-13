from django import template
from django.utils.safestring import mark_safe
from docutils.core import publish_parts

register = template.Library()     
@register.filter
def restructuredtext(value,smode=None):
    return mark_safe(publish_parts(value, writer_name='html')['html_body'])
