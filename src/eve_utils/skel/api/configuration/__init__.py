import os
import logging.config
import platform
import socket
import yaml
from eve import __version__ as eve_version
from cerberus import __version__ as cerberus_version
from werkzeug.utils import secure_filename

VERSION = '0.1.0'

# TODO: organize into functions!


def is_enabled(setting_key):
    setting_value = SETTINGS.get(setting_key)
    if not setting_value:
        return False
    return setting_value[0].lower() in 'yte'
    # i.e. the following means setting is enabled:
    # - 'Yes' or 'yes' or 'Y' or 'y'
    # - 'True' or 'true' or 'T' or 't'
    # - 'Enabled' or 'enabled' or 'E' or 'e'
    # TODO: refactor so lower level configurations can use (e.g. auth)


def set_optional_setting(var):
    if os.environ.get(var):
        SETTINGS[var] = os.environ.get(var)


def envar_to_int(envar, default=0):
    rtn = default
    try:
        rtn = int(os.environ.get(envar, default)
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


# TODO: sanitize smtp/email_recipients
SETTINGS = {
    'ES_API_NAME': '{$project_name}',

    'ES_MONGO_ATLAS': os.environ.get('ES_MONGO_ATLAS', 'Disabled'),
    'ES_MONGO_HOST': os.environ.get('ES_MONGO_HOST', 'localhost'),
    'ES_MONGO_PORT': envar_to_int('ES_MONGO_PORT', 27017),
    'ES_MONGO_DBNAME': os.environ.get('ES_MONGO_DBNAME', '{$project_name}'),
    'ES_API_PORT': envar_to_int('ES_API_PORT', 2112),
    'ES_INSTANCE_NAME': os.environ.get('ES_INSTANCE_NAME', socket.gethostname()),
    'ES_TRACE_LOGGING': os.environ.get('ES_TRACE_LOGGING', 'Enabled'),
    'ES_PAGINATION_LIMIT': envar_to_int('ES_PAGINATION_LIMIT', 3000),
    'ES_PAGINATION_DEFAULT': envar_to_int('ES_PAGINATION_DEFAULT', 1000),
    'ES_LOG_TO_FOLDER': os.environ.get('ES_LOG_TO_FOLDER', 'Enabled'),
    'ES_SEND_ERROR_EMAILS': os.environ.get('ES_SEND_ERROR_EMAILS', 'Enabled'),
    'ES_SMTP_HOST': os.environ.get('ES_SMTP_HOST', 'internalmail.cri.com'),
    'ES_SMTP_PORT': envar_to_int('ES_SMTP_PORT', 25),
    'ES_ERROR_EMAIL_RECIPIENTS': os.environ.get('ES_ERROR_EMAIL_RECIPIENTS', 'michael@pointw.com')
}

# optional settings...
set_optional_setting('ES_MONGO_USERNAME')
set_optional_setting('ES_MONGO_PASSWORD')
set_optional_setting('ES_MONGO_AUTH_SOURCE')
set_optional_setting('ES_MEDIA_BASE_URL')
set_optional_setting('ES_PUBLIC_RESOURCES')

# cancellable settings...
# if SETTINGS.get('ES_CANCELLABLE') == '':
#     del SETTINGS['ES_CANCELLABLE']


# Set up logging
API_NAME = SETTINGS.get('ES_API_NAME')

with open('logging.yml', 'r') as f:
    logging_config = yaml.load(f, Loader=yaml.FullLoader)

if is_enabled('ES_LOG_TO_FOLDER'):
    LOG_FOLDER = f'/var/log/{secure_filename(API_NAME)}'
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    logging_config['handlers']['all']['filename'] = os.path.join(LOG_FOLDER, 'all.log')
    logging_config['handlers']['warn']['filename'] = os.path.join(LOG_FOLDER, 'warn.log')
    logging_config['handlers']['error']['filename'] = os.path.join(LOG_FOLDER, 'error.log')

if is_enabled('ES_SEND_ERROR_EMAILS'):
    logging_config['handlers']['smtp']['mailhost'] = [SETTINGS.get('ES_SMTP_HOST'), SETTINGS.get('ES_SMTP_PORT')]
    logging_config['handlers']['smtp']['toaddrs'] = [e.strip() for e in SETTINGS.get('ES_ERROR_EMAIL_RECIPIENTS').split(',')]
    logging_config['handlers']['smtp']['subject'] = f'Problem encountered with {API_NAME}'


logging.config.dictConfig(logging_config)

werkzeug_log = logging.getLogger('werkzeug')
werkzeug_log.setLevel(logging.ERROR)

LOG = logging.getLogger('configuration')
LOG.info('%s version:  %s', API_NAME, VERSION)
LOG.info('Eve version:      %s', eve_version)
LOG.info('Cerberus version: %s', cerberus_version)
LOG.info('Python version:   %s', platform.sys.version)



if is_enabled('ES_SEND_ERROR_EMAILS'):
    instance_name = SETTINGS.get('ES_INSTANCE_NAME')
    EMAIL_FORMAT = f'''%(levelname)s sent from {API_NAME} instance "{instance_name}" (hostname: {socket.gethostname()})

    %(asctime)s - %(levelname)s - File: %(filename)s - %(funcName)s() - Line: %(lineno)d -  %(message)s
    '''

    EMAIL_FORMAT += f'''
    {API_NAME} version:  {VERSION}
    Eve version:      {eve_version}
    Cerberus version: {cerberus_version}
    Python version:   {platform.sys.version}

    '''

    for setting in sorted(SETTINGS):
        key = setting.upper()
        if ('PASSWORD' not in key) and ('SECRET' not in key):
            LOG.info(f'{setting}: {SETTINGS[setting]}')
            EMAIL_FORMAT += f'{setting}: {SETTINGS[setting]}\n'
    EMAIL_FORMAT += '\n\n'

    LOGGER = logging.getLogger()
    HANDLERS = LOGGER.handlers

    SMTP_HANDLER = [x for x in HANDLERS if x.name == 'smtp'][0]
    SMTP_HANDLER.setFormatter(logging.Formatter(EMAIL_FORMAT))
