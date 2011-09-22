Production and staging instances of Solr are currently on mysq1-central, running under tomcat.

==========================
Solr Configuration Updates
==========================

Solr config files are located in the myschedule/solr folder. Configuration updates typically will consist of changes to schema.xml, solrconfig.xml, and/or synonyms.txt.

Note that for solronfig.xml, you must use the appropriate version of the file for the environment you are deploying to. (The difference is the data-dir path.):

 * solrconfig.xml is for production 
 * solrconfig.xml.staging is for staging 
 * solrconfig.xml.dev is for development 

1. Copy the files to the appropriate solr conf dir

First backup the files you will be copying over!!!

For staging, copy the new versions of the files into /vol1/solr-staging/conf:
sudo cp solrconfig.xml.staging /vol1/solr-staging/conf/solrconfig.xml
sudo cp schema.xml /vol1/solr-staging/conf/
sudo cp synonyms.txt /vol1/solr-staging/conf/

For production, copy them into /vol1/solr/conf:
sudo cp solrconfig.xml /vol1/solr/conf/
sudo cp schema.xml /vol1/solr/conf/
sudo cp synonyms.txt /vol1/solr/conf/

2. After copying the appropriate version of the files into the appropriate solr conf directory, restart tomcat:

sudo service tomcat6 restart

3. After restarting tomcat, the index may need to be rebuilt. If so, on one of the myschedule front-ends, (pas3 or pas4), run (WITH SUDO) the myschedule_rebuild_index.py script located in the myschedule/scripts folder:

sudo python2.5 myschedule_rebuild_index.py


===========================================================
Initial Install of Solr, and production and staging indexes
===========================================================

(For a server with tomcat6)

# On the server hosting the solr api, install solr
# Some References:
# http://wiki.apache.org/solr/SolrInstall
# http://wiki.apache.org/solr/SolrTomcat
# http://yoodey.com/install-solr-141-ubuntu-1010-maven-maverick-multicore-using-tomcat-6-complete-guide

# Get solr
# list of mirrors: http://pas-staging.cpcc.edu/myschedule/
wget http://apache.mirrors.tds.net//lucene/solr/1.4.1/apache-solr-1.4.1.tgz
tar -zxvf apache-solr-1.4.1.tgz
cd apache-solr-1.4.1

# install the war file
sudo cp dist/apache-solr-1.4.1.war /var/lib/tomcat6/webapps/solr.war


# create the solr.xml file for tomcat
sudo vi /etc/tomcat6/Catalina/localhost/solr.xml

  <Context docBase="/var/lib/tomcat6/webapps/solr.war" debug="0" privileged="true" allowLinking="true" crossContext="true">
    <Environment name="solr/home" type="java.lang.String" value="/vol1/solr" override="true" />
  </Context>

# Create directory for solr home and data 
sudo cp -R example/solr /vol1     
sudo mkdir /vol1/solr/data 

# Backup distributed schema.xml and solrconfig.xml
cd /vol1/solr/config
sudo cp schema.xml schema.xml.dist
sudo cp solrconfig.xml solrconfig.xml.dist
cd -

# Get the custom config files onto the server
scp schema.xml solrconfig.xml mysq1-central.cpcc.edu:./myschedule

# Copy the custom config files into solr/conf
cp schema.xml solrconfig.xml .../solr/conf

# Make sure dataDir is set to dir on server
sudo vi /vol1/solr/conf/solrconfig.xml
  <dataDir>/vol1/solr/data</dataDir>

# give tomcat access to data dir
sudo chown -R tomcat6:tomcat6 /vol1/solr/data

# restart tomcat
sudo service tomcat6 restart

# URL of solr service is:
http://mysq1-central.cpcc.edu:8080/solr


# To create a second instance of solr named solr-staging:

# make a copy of the solr war, renaming to solr-staging
sudo cp /var/lib/tomcat6/webapps/solr.war /var/lib/tomcat6/webapps/solr-staging.war

# copy and update the solr.xml file for tomcat
sudo cp /etc/tomcat6/Catalina/localhost/solr.xml /etc/tomcat6/Catalina/localhost/solr-staging.xml

# rename the war file and the value of solr/home
# do not rename "solr/home" itself!
sudo vi /etc/tomcat6/Catalina/localhost/solr-staging.xml

  <Context docBase="/var/lib/tomcat6/webapps/solr-staging.war" debug="0" privileged="true" allowLinking="true" crossContext="true">
    <Environment name="solr/home" type="java.lang.String" value="/vol1/solr-staging" override="true" />
  </Context>


# Make a copy of the current solr instance directory
sudo cp -R solr solr-staging

# Update the dataDir in the new instance dir

  <dataDir>/vol1/solr-staging/data</dataDir>

# give tomcat access to data dir
sudo chown -R tomcat6:tomcat6 /vol1/solr-staging/data

# restart tomcat
sudo service tomcat6 restart

# URL of solr-staging service is:
http://mysq1-central.cpcc.edu:8080/solr-staging

