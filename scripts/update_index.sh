cd /opt/wsgi-apps/
sudo chmod go+r myschedule_settings.py
export PYTHONPATH=/opt/wsgi-apps
django-admin.py update_index
sudo chmod go-r myschedule_settings.py
cd -
