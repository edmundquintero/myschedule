# Load into ipython.

def update_courses_test():
    # For testing update_courses view.
    import urllib
    import httplib
    headers = {'Content-type':'application/json'}
    req = urllib.urlopen('http://te409-05.cpcc.edu/schedule_data3.json')
    course_data = req.read()
    data = '[{"auth_key":"test_key","course_data":'+course_data+'}]'
    conn = httplib.HTTPConnection('te409-05.cpcc.edu:5075')
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
    headers = {'Content-type':'application/json'}
    availability_data='[{"section_code":"REC-8800-01-su-2011","available_seats":"99", "status":"Active"},{"section_code":"REC-8112-01-su-2011","available_seats":1,"status":"Canceled"}]'
    data = '[{"auth_key":"test_key","availability_data":'+availability_data+'}]'
    conn = httplib.HTTPConnection('te409-05.cpcc.edu:5075')
    req2 = conn.request('POST','/myschedule/update_seats/',data,headers)
    resp = conn.getresponse()
    temp = resp.read()
    print temp
    conn.close()
    f = open('temp.txt','w')
    f.write(temp)
    f.close()

