from django import template


register = template.Library()

@register.filter
def format_term(value):
    return value.upper().replace('FA', 'Fall').replace('SP', 'Spring').replace('SU', 'Summer')

@register.filter(name='days_of_week')
def days_of_week(value):
    return value.upper().replace('R','Th').replace('S','Sa').replace('U','Su')
