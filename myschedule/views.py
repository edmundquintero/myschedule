# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings

from cpsite import ods
# from cpsite.decorators import groups_required

from myschedule import models, forms

def index(request):
    search = forms.search_form()
    return direct_to_template(request, 'myschedule/index.html', {'search':search})

def compose_booklink(campus=None, term=None, year=None, course_prefix=None,
                     course_number=None, section=None):
    """
        Composes a link to the textbook publisher's web service.
    """
    store_campus_mapping = settings.BOOKLOOK_STORE_CAMPUS_MAPPING
    store_id = ''
    if campus != '' and campus != None:
        store_id = settings.BOOKLOOK_DEFAULT_STORE
        if campus in store_campus_mapping:
            store_id = store_campus_mapping[campus]
    if term.lower() in settings.BOOKLOOK_TERMS:
        term = settings.BOOKLOOK_TERMS[term.lower()]
    else:
        term = ''
    booklink=''
    if (store_id != '' and term != '' and year != '' and year != None
                and course_prefix != '' and course_prefix != None
                and course_number != '' and course_number != None):
        booklink = (''+settings.BOOKLOOK_URL +
                    '?sect-1=' + section +
                    '&bookstore_id-1=' + store_id +
                    '&dept-1=' + course_prefix +
                    '&course-1=' + course_number +
                    '&term_id-1=' + term + ' ' + year)
    return booklink

def show_courses(request):
    """
        Displays course search results template.
    """
    # TODO: For now we'll just grab all mat courses via cpapi so we'll have
    # some courses to display.
    ods_spec_dict = {"key": settings.CPAPI_KEY,
                     "data": "course",
                     "prefix": 'MAT'}
    course_data = ods.get_data(ods_spec_dict)
    search = forms.search_form()
    return direct_to_template(request,
            'myschedule/course_results.html',
            {'courses':course_data,
             'search':search}
    )

def show_sections(request, prefix, number):
    """
        Display section results template for specified course.
    """
    # TODO: Get the section data
    search = forms.search_form()
    return direct_to_template(request,
            'myschedule/section_results.html',
            {'prefix':prefix, 'number':number, 'search':search}
    )

def query(request, querystring):
    print querystring
    print querystring.split("/")
    search = forms.search_form()
    return direct_to_template(request, 'myschedule/index.html', {'search':search})

