from django import forms
from haystack.forms import SearchForm
from myschedule.models import Section

class FilterSearchForm(SearchForm):
    """
       Form used by search to further filter query results.
    """
    distinct_campuses = Section.objects.distinct('campus').values('campus').order_by('campus')
    distinct_delivery_types = Section.objects.distinct('delivery_type').values('delivery_type')
    campuses = [('all','All campuses')]
    for campus in distinct_campuses:
        if campus['campus'] != '':
            campuses.append((campus['campus'],campus['campus']))
    delivery_types = [('all','All delivery methods')]
    for delivery_type in distinct_delivery_types:
        if delivery_type['delivery_type'] != '':
            delivery_types.append((delivery_type['delivery_type'],delivery_type['delivery_type']))
    date_formats =['%m/%d/%Y', # 10/25/2006'
                   '%m-%d-%Y' # '10-25-2006'
    ]
 
    campus = forms.ChoiceField(choices=campuses, required=False)
    delivery_method = forms.ChoiceField(choices=delivery_types, required=False)
    start_date = forms.DateField(input_formats=date_formats, required=False)
    end_date = forms.DateField(input_formats=date_formats, required=False)

    def search(self):
        # TODO: Try refactoring some of this code!
        from datetime import datetime
        sqs = super(FilterSearchForm, self).search()
        # An important fact to keep in mind is that campuses, delivery types (or methods),
        # start dates and end dates are multi-value fields in the search index (because
        # this data comes from the sections and not the course).  That accounts for the
        # additional filtering steps below.  In hindsight, the index probably should have
        # been at the section level (or potentially the meeting level). Maybe in version 3...
        if self.cleaned_data['campus']:
            if self.cleaned_data['campus'] != 'all':
                sqs = sqs.filter(campuses__exact=self.cleaned_data['campus'])
        if self.cleaned_data['delivery_method']:
            if self.cleaned_data['delivery_method'] != 'all':
                # Initial filtering of delivery method.
                sqs = sqs.filter(delivery_types__exact=self.cleaned_data['delivery_method'])
                # Despite specifying exact, if the delivery method is 'Online', it retains
                # all delivery methods that contain the word 'Online', so will need to
                # explicitly verify the courses really have sections with delivery method
                # equal to 'Online'.
                if self.cleaned_data['delivery_method'] == 'Online':
                    for item in sqs:
                        remove_item = True
                        for delivery_type in item.delivery_types:
                            if delivery_type == 'Online':
                                remove_item = False
                                break
                        if remove_item == True:
                            sqs = sqs.exclude(primary_key=item.pk)
                # If the user wants to filter by both campus and delivery method, we have to
                # go back through and make sure the delivery method that was retained applied
                # to the campus that was requested.
                if self.cleaned_data['campus'] != 'all':
                    for item in sqs:
                        i = 0
                        remove_item = True
                        if item.campuses:
                            for campus in item.campuses:
                                if campus == self.cleaned_data['campus'] and item.delivery_types[i] == self.cleaned_data['delivery_method']:
                                    remove_item = False
                                    break
                                i = i + 1
                        if remove_item == True:
                            sqs = sqs.exclude(primary_key=item.pk)
        # Unfortunately trying to filter dates through haystack and solr seems to be
        # not functioning as expected (may be due to our versions of those apps - not
        # sure at this point), so we'll just do it the manual way.
        if self.cleaned_data['start_date'] or self.cleaned_data['end_date']:
            for item in sqs:
                if self.cleaned_data['start_date'] != None:
                    remove_item = True
                    if item.start_dates:
                        i = 0
                        for start_date in item.start_dates:
                            temp_date = datetime.strptime(start_date.strip('T00:00:00Z'), '%Y-%m-%d').date()
                            if temp_date >= self.cleaned_data['start_date']:
                                if self.cleaned_data['end_date'] != None:
                                    if item.end_dates:
                                        temp_date = datetime.strptime(item.end_dates[i].strip('T00:00:00Z'), '%Y-%m-%d').date()
                                        if temp_date <= self.cleaned_data['end_date']:
                                            # If campus and/or delivery method filters were also specified,
                                            # make sure this end date is for the specified campus and/or delivery method.
                                            if (self.cleaned_data['campus'] == 'all' or 
                                                   (self.cleaned_data['campus'] != 'all' and 
                                                    item.campuses and
                                                    item.campuses[i] == self.cleaned_data['campus'])):
                                                if (self.cleaned_data['delivery_method'] == 'all' or 
                                                       (self.cleaned_data['delivery_method'] != 'all' and 
                                                        item.delivery_types and
                                                        item.delivery_types[i] == self.cleaned_data['delivery_method'])):
                                                    remove_item = False
                                                    break    
                                else:
                                    if (self.cleaned_data['campus'] == 'all' or 
                                           (self.cleaned_data['campus'] != 'all' and 
                                            item.campuses and
                                            item.campuses[i] == self.cleaned_data['campus'])):
                                        if (self.cleaned_data['delivery_method'] == 'all' or 
                                               (self.cleaned_data['delivery_method'] != 'all' and 
                                                item.delivery_types and
                                                item.delivery_types[i] == self.cleaned_data['delivery_method'])):
                                            remove_item = False
                                            break
                            i = i + 1
                else:
                    if self.cleaned_data['end_date'] != None:
                        remove_item = True
                        if item.end_dates:
                            i=0
                            for end_date in item.end_dates:
                                temp_date = datetime.strptime(end_date.strip('T00:00:00Z'), '%Y-%m-%d').date()
                                if temp_date <= self.cleaned_data['end_date']:
                                    if (self.cleaned_data['campus'] == 'all' or 
                                           (self.cleaned_data['campus'] != 'all' and 
                                            item.campuses and
                                            item.campuses[i] == self.cleaned_data['campus'])):
                                        if (self.cleaned_data['delivery_method'] == 'all' or 
                                               (self.cleaned_data['delivery_method'] != 'all' and 
                                                item.delivery_types and
                                                item.delivery_types[i] == self.cleaned_data['delivery_method'])):
                                            remove_item = False
                                            break
                                i = i + 1
                if remove_item == True:
                    sqs = sqs.exclude(primary_key=item.pk)
        return sqs
