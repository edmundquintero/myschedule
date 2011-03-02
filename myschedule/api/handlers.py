from piston.handler import BaseHandler
from piston.utils import rc, validate

from django.conf import settings

from myschedule.models import Section

import base64

class MyScheduleHandler(BaseHandler):
    """
        Handler for reading and updating section seat counts and status.

        To test
        -------
        In the interactive shell (python appmanage.py shell) issue the
        following commands:
        from django.test import Client
        c=Client()
        temp1=c.get('/myschedule/api/seats/ART-288G-01-su-2011/')
        temp2=c.put('/myschedule/api/seats/ART-288G-01-su-2011/2/Active/')

        See test.py in views to see how to send put request with httplib.
        The read can just be tested from the browser since it's a get request.

        Might need to eventually add piston to installed_apps in settings and
        run syncdb to create it's tables.  For now it's not needed (I think it
        may be needed if add in authorization support).
    """

    allowed_methods = ('GET', 'PUT',)
    fields = ('id', 'section_code', 'available_seats', 'status')
    model = Section

    def read(self, request, section_code):
        """
            Returns data for specified section.
        """
        section = self.model.objects.get(section_code=section_code)
        return section

    def update(self, request, section_code, available_seats, status):
        """
            Updates seat count and status for specified section.
        """
        if request.META.has_key('HTTP_AUTHORIZATION'):
            # Calling function needs to make sure to remove extraneous line
            # feed attached to encoded authorization string. Django does not
            # like it - post data will be messed up.
            authorization = request.META['HTTP_AUTHORIZATION']
            authorization = authorization.replace('Basic ','')
            credentials = base64.decodestring(authorization)
            credentials = credentials.split(':')
            # Compare the credentials passed in through the header to
            # those in the settings to verify calling application is
            # authorized
            if (credentials[0] != settings.DATA_CREDENTIALS[0] or
                    credentials[1] != settings.DATA_CREDENTIALS[1]):
                raise ValueError("Invalid credentials")
        else:
            raise ValueError("Missing credentials")
        section = self.model.objects.get(section_code=section_code)
        section.available_seats = available_seats
        section.status = status
        section.save()
        return section


