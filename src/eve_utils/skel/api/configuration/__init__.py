import os
import socket

from utils import is_enabled, log_settings
from configuration.log_setup import get_configured_logger

VERSION = '0.1.0'


def set_optional_setting(var):
    if os.environ.get(var):
        SETTINGS[var] = os.environ.get(var)


def set_optional_int_setting(var):
    if os.environ.get(var):
        SETTINGS[var] = environment_variable_to_int(var)


def environment_variable_to_int(variable, default=0):
    try:
        rtn = int(os.environ.get(variable, default))
    except ValueError:
        rtn = default

    return rtn


# set environment variables from _env.conf (which is in .gitignore)
if os.path.exists('_env.conf'):
    with open('_env.conf') as setting:
        for line in setting:
            if not line.startswith('#'):
                line = line.rstrip()
                nvp = line.split('=')
                if len(nvp) == 2:
                    os.environ[nvp[0].strip()] = nvp[1].strip()

SETTINGS = {
    'ES_API_NAME': '{$project_name}',

    'ES_MONGO_ATLAS': os.environ.get('ES_MONGO_ATLAS', 'Disabled'),
    'ES_MONGO_HOST': os.environ.get('ES_MONGO_HOST', 'localhost'),
    'ES_MONGO_PORT': environment_variable_to_int('ES_MONGO_PORT', 27017),
    'ES_MONGO_DBNAME': os.environ.get('ES_MONGO_DBNAME', '{$project_name}'),
    'ES_API_PORT': environment_variable_to_int('ES_API_PORT', 2112),
    'ES_INSTANCE_NAME': os.environ.get('ES_INSTANCE_NAME', socket.gethostname()),
    'ES_TRACE_LOGGING': os.environ.get('ES_TRACE_LOGGING', 'Enabled'),
    'ES_PAGINATION_LIMIT': environment_variable_to_int('ES_PAGINATION_LIMIT', 3000),
    'ES_PAGINATION_DEFAULT': environment_variable_to_int('ES_PAGINATION_DEFAULT', 1000),
    'ES_ADD_ECHO': os.environ.get('ES_ADD_ECHO', 'Disabled'),
    'ES_LOG_TO_FOLDER': os.environ.get('ES_LOG_TO_FOLDER', 'Disabled'),
    'ES_SEND_ERROR_EMAILS': os.environ.get('ES_SEND_ERROR_EMAILS', 'Disabled'),
}

# optional settings...
set_optional_setting("ES_URL_PREFIX")
set_optional_setting("ES_CACHE_CONTROL")
set_optional_int_setting("ES_CACHE_EXPIRES")
set_optional_setting('ES_MONGO_USERNAME')
set_optional_setting('ES_MONGO_PASSWORD')
set_optional_setting('ES_MONGO_AUTH_SOURCE')
set_optional_setting('ES_MEDIA_BASE_URL')
set_optional_setting('ES_PUBLIC_RESOURCES')

if is_enabled('ES_SEND_ERROR_EMAILS'):
    SETTINGS['ES_SMTP_PORT'] = environment_variable_to_int('ES_SMTP_PORT', 25)
    set_optional_setting('ES_SMTP_HOST')
    set_optional_setting('ES_ERROR_EMAIL_RECIPIENTS')
    set_optional_setting('ES_ERROR_EMAIL_FROM')

# cancellable settings...
# if SETTINGS.get('ES_CANCELLABLE') == '':
#     del SETTINGS['ES_CANCELLABLE']

LOG = get_configured_logger(SETTINGS, VERSION)
log_settings(LOG, SETTINGS)
