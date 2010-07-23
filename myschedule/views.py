# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

# from cpsite import ods
# from cpsite.decorators import groups_required

from myschedule import models, forms

def index(request):
    return direct_to_template(request, 'myschedule/index.html', dict())
