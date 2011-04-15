import commands
from django.conf import settings

class WebAdvisorCreator(object):
    """
        Issues the command to submit the user's schedule to mycollege
        (webadvisor).  More or less copied this over from
        rios/snap/packages/snap/models/snap2webadvisor.py.
    """
    command = "ssh -i %s -o UserKnownHostsFile=%s %s 'schedule2webadvisor %s %s'"
    key_location = settings.S2W_KEY_LOCATION
    user_at_server = settings.S2W_USER_AT_SERVER
    knownhosts = settings.KNOWNHOSTS
    def __call__(self, student_id, sections):
        s2w_command = self.command % (self.key_location,
                                      self.knownhosts,
                                      self.user_at_server,
                                      student_id,
                                      sections)
        code, output = commands.getstatusoutput(s2w_command)
        return output
