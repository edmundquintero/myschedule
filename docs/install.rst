Initial Install
===============
1. Install the application.
2. Update DATA_CREDENTIALS setting with appropriate username and password.
3. Populate course data (run cron jobs for course data and seat count data)
4. Install/run haystack, solr, and pysolr (see dependencies and notes below)
5. Update HAYSTACK_SOLR_URL setting to access solr.
6. Run "python appmanage.py rebuild_index" or script rebuild_index.sh

Dependencies:
django_haystack 1.0.1 final
apache solr 1.4.1
pysolr 2.0.13
cpsite 1.5.1+
cpapi 1.4.4+

Setup for Solr:
Download version 1.4.1 here - http://ftp.wayne.edu/apache//lucene/solr/1.4.1/
Alternately find a mirror here - http://www.apache.org/dyn/closer.cgi/lucene/solr/ and snag 1.4.1
Unpack to somewhere convenient, and make sure Sun Java is installed and java is in your PATH
Snag pysolr (easy_install or similar is suggested, as pysolr has plenty of dependencies itself)
CD into your solr folder, then ./example/solr/conf/ and drop schema.xml and solrconfig.xml here
CD back to ./example and run "java -jar start.jar"
Update HAYSTACK_SOLR_URL in development.py to point to your machine. Port 8983 is
the default, so you should not have to change that.
You should be able to update/rebuild your search indexes at that point in myschedule
root with "python appmanage.py update_index" or "python appmanage.py rebuild_index"

Note on installation of Solr:
Presently, django-haystack supports solr versions 1.3+, and thus far there have
been no issues in using 1.4.1. If we change to a 1.3.x release, you will need to
run "python appmanage build_solr_schema" and replace the existing schema.xml. It
will likely produce the same xml as before, but it is best to cover bases here.

Schedule CRON jobs (production environment):
1. course data bulk load
2. seat count update
3. scripts/popularity.py
4. scripts/update_index.sh

SSH
===

In addition to the standard initial deploy process, you will also need to set up the ssh files
used to submit schedule data to webadvisor (mycollege).

Getting the files in place
--------------------------

Get the ssh files in one of your directories on the server, for example:
scp ~/hg/myschedule/.ssh/* pas-staging.cpcc.edu:./deploy/myschedule/.ssh

Create the ssh directory on the server:
sudo mkdir -p /usr/local/etc/myschedule/.ssh/   # or whatever the settings.SSH_ROOT will be set to

Copy the files into the ssh directory:
sudo cp ~/deploy/myschedule/.ssh/*  /usr/local/etc/myschedule/.ssh/

Replace the privkey file with actual (and current) private key files (myschedule will use
the same one used by snap).

If there aren't already files you can copy from a server get the privkey from CIS (Ben Diel)

Make sure the appropriate knownhosts file is updated if the remote server also changed, (ie, webadvisor) -
myschedule should be using the same one used by snap.

Setting the permissions and ownership
-------------------------------------

The files need to be u+rw only, and owned by the user that runs the app.
 sudo chown -R myschedule:myschedule /usr/local/etc/myschedule/
 sudo chmod -R ugo-rwx /usr/local/etc/myschedule/.ssh/        # clear out all r/w/x permissions
 sudo chmod -R u+rw /usr/local/etc/myschedule/.ssh/           # give r/w back only to user for this directory and its contents
 sudo chmod  u+x /usr/local/etc/myschedule/.ssh/              # give x back only to user for directory only

If these permissions are not set correctly, the schedule2webadvisor calls will not work
and may prompt you for additional credentials or keys.
