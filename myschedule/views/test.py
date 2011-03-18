# Load into ipython.

def update_courses_test():
    # For testing update_courses view.
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
    f = open('temp.txt','w')
    f.write(temp)
    f.close()

def update_seats_test():
    # For testing update_seats view.
    import httplib
    import base64
    creds = base64.encodestring('%s:%s' % ('testuser','testpass'))
    authstring = "Basic %s" % creds
    authstring = authstring.replace("\n","")
    headers = {'Content-type':'application/json','AUTHORIZATION':authstring}
    data='[{"section_code":"REC-8800-01-su-2012","available_seats":"99", "status":"Active"},{"section_code":"REC-8112-01-sp-2011","available_seats":1,"status":"Canceled"}]'
    conn = httplib.HTTPConnection('te409-05.cpcc.edu:5000')
    req2 = conn.request('POST','/myschedule/update_seats/',data,headers)
    resp = conn.getresponse()
    temp = resp.read()
    print temp
    conn.close()
    f = open('temp.txt','w')
    f.write(temp)
    f.close()

