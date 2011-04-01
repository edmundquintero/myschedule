cd /opt/wsgi-apps/
sudo chmod go+r myschedule_settings.py
export PYTHONPATH=/opt/wsgi-apps
django-admin.py rebuild_index
sudo chmod go-r myschedule_settings.py
cd -
