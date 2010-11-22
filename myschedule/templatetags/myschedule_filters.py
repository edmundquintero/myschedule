from django import template


register = template.Library()

@register.filter
def format_section(value):
    return value.replace('-', ' ').replace('fa', 'Fall').replace('sp', 'Spring')
