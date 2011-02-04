from django import template


register = template.Library()

@register.filter
def format_section(value):
    return value.replace('-', ' ').replace('fa', 'Fall').replace('sp', 'Spring')

@register.filter(name='days_of_week')
def days_of_week(value):
    return value.upper().replace('R','Th').replace('S','Sa').replace('U','Su')
