from django import template
from django.utils.text import capfirst

register = template.Library()

@register.filter
def verbose_name(obj, arg):
    return capfirst(obj._meta.get_field(arg).verbose_name)

    
    
