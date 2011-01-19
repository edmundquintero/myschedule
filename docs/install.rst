Initial Install
===============

Dependencies:
django_haystack 1.0.1 final
apache solr 1.4.1
pysolr 2.0.13
django_piston 0.2.2

Setup for Solr:
Download version 1.4.1 here - http://ftp.wayne.edu/apache//lucene/solr/1.4.1/
Alternately find a mirror here - http://www.apache.org/dyn/closer.cgi/lucene/solr/ and snag 1.4.1
Unpack to somewhere convenient, and make sure Sun Java is installed and java is in your PATH
Snag pysolr (easy_install or similar is suggested, as pysolr has plenty of dependencies itself)
CD into your solr folder, then ./example/solr/conf/ and drop schema.xml and solrconfig.xml here
CD back to ./example and run "java -jar start.jar"
Update HAYSTACK_SOLR_URL in development.py to point to your machine. Port 8983 is the default, so you should not have to change that.
You should be able to update/rebuild your search indexes at that point in myschedule root with "python appmanage.py update_index" or "python appmanage.py rebuild_index"

Note on installation of Solr:
Presently, django-haystack supports solr versions 1.3+, and thus far there have been no issues in using 1.4.1. If we change to a 1.3.x release, you will need to run "python appmanage build_solr_schema" and replace the existing schema.xml. It will likely produce the same xml as before, but it is best to cover bases here.