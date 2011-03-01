# This can be used for testing pushing data to the course_update view.
# Load into ipython.

import urllib
import httplib
import base64
creds = base64.encodestring('%s:%s' % ('testuser','testpass'))
authstring = "Basic %s" % creds
authstring = authstring.replace("\n","")
headers = {'Content-type':'application/json','AUTHORIZATION':authstring}
#headers = {'Content-type':'application/json'}
req = urllib.urlopen('http://te409-05.cpcc.edu/schedule_data3.json')
data = req.read()

conn = httplib.HTTPConnection('te409-05.cpcc.edu:5000')
req2 = conn.request('POST','/myschedule/update_courses/',data,headers)
resp = conn.getresponse()
temp = resp.read()
print temp
conn.close()
