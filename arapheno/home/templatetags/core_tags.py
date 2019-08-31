from django import template
from dateutil import parser
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.filter
def parse_dt(value):
    return parser.parse(value)