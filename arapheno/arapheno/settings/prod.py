"""
Production settings
"""
# Load defaults in order to then add/override with dev-only settings
from defaults import *
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://9a156862319542a88f13172b04a338cb@sentry.io/1798770",
    integrations=[DjangoIntegration()]
)

DATACITE_REST_URL='https://mds.datacite.org/'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ.get("EMAIL_PORT",25)
EMAIL_HOST_USER = os.environ["EMAIL_USER"]
