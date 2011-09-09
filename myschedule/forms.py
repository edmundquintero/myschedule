from django import forms
from haystack.forms import SearchForm
from myschedule.models import Section

class FilterSearchForm(SearchForm):
    distinct_campuses = Section.objects.distinct('campus').values('campus').order_by('campus')
    distinct_delivery_types = Section.objects.distinct('delivery_type').values('delivery_type')
    campuses = [('all','All campuses')]
    for campus in distinct_campuses:
        campuses.append((campus['campus'],campus['campus']))
    delivery_types = [('all','All delivery methods')]
    for delivery_type in distinct_delivery_types:
        delivery_types.append((delivery_type['delivery_type'],delivery_type['delivery_type']))
    campus = forms.ChoiceField(choices=campuses, required=False)
    delivery_method = forms.ChoiceField(choices=delivery_types, required=False)
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def search(self):
        sqs = super(FilterSearchForm, self).search()
        if self.cleaned_data['campus']:
            if self.cleaned_data['campus'] != 'all':
                sqs = sqs.filter(campuses__exact=self.cleaned_data['campus'])
        if self.cleaned_data['delivery_method']:
            if self.cleaned_data['delivery_method'] != 'all':
                sqs = sqs.filter(delivery_types__exact=self.cleaned_data['delivery_method'])
        #if self.cleaned_data['start_date']:
        #    if self.cleaned_data['start_date'] != '':
        #        sqs = sqs.filter(delivery_types__icontains=self.cleaned_data['delivery_method'])
        return sqs
