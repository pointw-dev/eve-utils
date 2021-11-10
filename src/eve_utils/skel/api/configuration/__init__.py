import os
import socket

from configuration.log_setup import get_configured_logger

VERSION = '0.1.0'


def set_optional_setting(var):
    if os.environ.get(var):
        SETTINGS[var] = os.environ.get(var)


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
    'ES_LOG_TO_FOLDER': os.environ.get('ES_LOG_TO_FOLDER', 'Disabled'),
    'ES_SEND_ERROR_EMAILS': os.environ.get('ES_SEND_ERROR_EMAILS', 'Disabled'),
}

# optional settings...
set_optional_setting('ES_MONGO_USERNAME')
set_optional_setting('ES_MONGO_PASSWORD')
set_optional_setting('ES_MONGO_AUTH_SOURCE')
set_optional_setting('ES_MEDIA_BASE_URL')
set_optional_setting('ES_PUBLIC_RESOURCES')

set_optional_setting('ES_SMTP_HOST')
set_optional_setting('ES_SMTP_PORT')
set_optional_setting('ES_ERROR_EMAIL_RECIPIENTS')
set_optional_setting('ES_ERROR_EMAIL_FROM')

# cancellable settings...
# if SETTINGS.get('ES_CANCELLABLE') == '':
#     del SETTINGS['ES_CANCELLABLE']

LOG = get_configured_logger(SETTINGS, VERSION)
for setting in sorted(SETTINGS):
    key = setting.upper()
    if ('PASSWORD' not in key) and ('SECRET' not in key):
        LOG.info(f'{setting}: {SETTINGS[setting]}')
