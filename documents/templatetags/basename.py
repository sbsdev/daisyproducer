from django import template
from django.template.defaultfilters import stringfilter
import os

register = template.Library()

@register.filter
@stringfilter
def basename(value):
    return os.path.basename(value)
