"""
Production settings
"""
# Load defaults in order to then add/override with dev-only settings
from defaults import *


DATACITE_REST_URL='https://mds.datacite.org/'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}