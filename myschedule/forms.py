from django import forms
from haystack.forms import SearchForm
from myschedule.models import Course, Section
from django.conf import settings

class FilterSearchForm(SearchForm):
    """
       Form used by search to further filter query results.
    """
    distinct_campuses = Section.objects.exclude(campus='').order_by('campus').values('campus').distinct()
    distinct_delivery_types = Section.objects.exclude(delivery_type='').order_by('delivery_type').values('delivery_type').distinct()
    distinct_academic_levels = Course.objects.exclude(academic_level='').order_by('academic_level').values('academic_level').distinct()
    campuses = [('all','All campuses')]
    for campus in distinct_campuses:
        campuses.append((campus['campus'],campus['campus']))
    delivery_types = [('all','All delivery methods')]
    for delivery_type in distinct_delivery_types:
        delivery_types.append((delivery_type['delivery_type'],delivery_type['delivery_type']))
    academic_levels = [('all','All academic levels')]
    for academic_level in distinct_academic_levels:
        academic_levels.append((academic_level['academic_level'],academic_level['academic_level']))
    date_formats =['%m/%d/%Y', # 10/25/2006
                   '%m-%d-%Y' # 10-25-2006
    ]
    terms = [('all','All terms')]
    for term in settings.AVAILABLE_TERMS:
        terms.append((term['display_term'], term['display_term']))
    campus = forms.ChoiceField(choices=campuses, required=False)
    delivery_method = forms.ChoiceField(choices=delivery_types, required=False)
    academic_level = forms.ChoiceField(choices=academic_levels, required=False)
    term = forms.ChoiceField(choices=terms, required=False)
    start_date = forms.DateField(input_formats=date_formats, required=False)
    end_date = forms.DateField(input_formats=date_formats, required=False)
    all_courses = forms.BooleanField(required=False)

    def search(self):
        from datetime import datetime

        sqs = super(FilterSearchForm, self).search()

        campus = ''
        delivery_method = ''
        start_date = None
        end_date = None
        filter_count = 0
        if self.cleaned_data['academic_level']:
            if self.cleaned_data['academic_level'] != 'all':
                academic_level = self.cleaned_data['academic_level']
                # Don't increment filter_count here because academic level
                # is at the course level, not the section level.
                sqs = sqs.filter(academic_level__exact=academic_level)
        if self.cleaned_data['campus']:
            if self.cleaned_data['campus'] != 'all':
                campus = self.cleaned_data['campus']
                filter_count = filter_count + 1
                sqs = sqs.filter(campuses__exact=campus)
        if self.cleaned_data['delivery_method']:
            if self.cleaned_data['delivery_method'] != 'all':
                delivery_method = self.cleaned_data['delivery_method']
                filter_count = filter_count + 1
                sqs = sqs.filter(delivery_types__exact=delivery_method)
        if self.cleaned_data['start_date']:
            if self.cleaned_data['start_date'] != None:
                start_date = self.cleaned_data['start_date']
                filter_count = filter_count + 1
                sqs = sqs.filter(start_dates__gte=start_date)
        if self.cleaned_data['end_date']:
            if self.cleaned_data['end_date'] != None:
                end_date = self.cleaned_data['end_date']
                filter_count = filter_count + 1
                sqs = sqs.filter(end_dates__lte=end_date)

        # An important fact to keep in mind is that campuses, delivery types (or methods),
        # start dates and end dates are multi-value fields in the search index (because
        # this data comes from the sections and not the course).  That accounts for the
        # additional filtering steps below.  (If more than one filter was specified, we
        # must make sure to include the course only if it had section data that met all
        # of the filtering criteria). In hindsight, the index probably should have
        # been at the section level (or potentially the meeting level). Maybe in version 3...
        if filter_count >= 2:
            for item in sqs:
                i = 0
                max_length = 0
                remove_item = True
                if item.campuses and campus != '':
                    max_length = len(item.campuses)
                if max_length == 0 and item.delivery_types and delivery_method != '':
                    max_length = len(item.delivery_types)
                if max_length == 0 and item.start_dates and start_date != None:
                    max_length = len(item.start_dates)
                if max_length == 0 and item.end_dates and end_date != None:
                    max_length = len(item.end_dates)
                while i <= max_length - 1:
                    if ((campus == '' or (item.campuses and item.campuses[i] == campus)) and
                        (delivery_method == '' or (item.delivery_types and item.delivery_types[i] == delivery_method)) and
                        (start_date == None or (item.start_dates and 
                                                datetime.strptime(item.start_dates[i].replace('T00:00:00Z',''), '%Y-%m-%d').date() >= start_date)) and
                        (end_date == None or (item.end_dates and datetime.strptime(item.end_dates[i].replace('T00:00:00Z',''), '%Y-%m-%d').date() <= end_date))):
                        remove_item = False
                        break
                    i = i + 1
                if remove_item == True:
                    sqs = sqs.exclude(primary_key=item.pk)

        return sqs
