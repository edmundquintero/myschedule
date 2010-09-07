#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# from django.shortcuts import get_object_or_404, redirect
import string

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
    courses = ods.get_data(ods_spec_dict)
    active_courses = []
    for course in courses:
        if course.has_key('status') and string.upper(course['status'])=='AB':
            # TODO: Update this with actual seat availability.
            course['information']='Sections with seats remaining'
            active_courses.append(course)
    active_courses.sort(key=lambda c: (c['prefix'], c['number']))
    search = forms.search_form()
    return direct_to_template(request,
            'myschedule/course_results.html',
            {'courses':active_courses,
             'search':search}
    )

def show_sections(request, prefix, number, course_id):
    """
        Display section results template for specified course.
    """
    from myschedule.cart import save_cartitems, add_cartitem
    if request.method == 'POST':
        sections = ''
        for key in request.POST:
            temp_key = key
            if 'section_' in temp_key:
                section = temp_key.replace('section_','')
                cart_item = add_cartitem(request, section)
                #sections = sections + section +'/'
        #if sections != '':
            #return HttpResponseRedirect(reverse(save_cartitems, args=[sections]))

    # TODO: Can't retrieve a course or section records using course_id via
    # cpapi, so until this whole data thing gets figured out will have to
    # filter the lists to get the items for a particular course_id. Actually
    # can only filter the course - sections doesn't include the course ID.
    ods_spec_dict = {"key": settings.CPAPI_KEY,
                     "data": "course",
                     "prefix": prefix,
                     "number": number}
    courses = ods.get_data(ods_spec_dict)
    active_course = {}
    for course in courses:
        if course.has_key('id') and course['id'] == course_id:
            active_course = course
    # TODO: Get the section data
    ods_spec_dict = {"key": settings.CPAPI_KEY,
                     "data": "sections",
                     "prefix": prefix,
                     "number": number}

    sections = ods.get_data(ods_spec_dict)
    active_sections = []
    for section in sections:
        if string.upper(section['term'])=='FA' and section['year']=='2010':
            active_sections.append(section)
            # Get the link to the book information TODO: replace hard-coded campus code with proper field when cpapi is updated to return location
            section["booklink"] = compose_booklink('1013', section['term'],
                              section['year'], section['prefix'],
                              section['number'], section['section'])
    search = forms.search_form()

    print request.user.is_anonymous()

    return direct_to_template(request,
            'myschedule/section_results.html',
            {'course':active_course,
             'sections':active_sections,
             'search':search,
             'anonymous': request.user.is_anonymous}
    )


