import os, sys
#sys.path.append(os.getcwd() + '/..')
sys.path.append('/Users/seb/dev/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'albums.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/egg_cache'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
