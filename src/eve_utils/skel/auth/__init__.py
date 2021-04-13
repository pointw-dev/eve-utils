"""Home of the auth modules that govern access via Eve."""
import os
import logging

LOG = logging.getLogger('auth')

SETTINGS = {
    'ES_AUTH_ADD_BASIC': os.environ.get('ES_AUTH_ADD_BASIC', 'No'),  # [0] in 'yYtT', i.e. yes, Yes, true, True
    'ES_AUTH_ROOT_PASSWORD': os.environ.get('ES_AUTH_ROOT_PASSWORD', 'password'),
    'ES_AUTH_REALM': os.environ.get('ES_AUTH_REALM', '{$project_name}.cri.com'),

    'ES_AUTH_JWT_DOMAIN': os.environ.get('ES_AUTH_JWT_DOMAIN', '{$project_name}.us.auth0.com'),
    'ES_AUTH_JWT_CLIENT_ID': os.environ.get('ES_AUTH_JWT_CLIENT_ID', '--your-client_id--'),
    'ES_AUTH_JWT_ISSUER': os.environ.get('ES_AUTH_JWT_ISSUER', 'https://{$project_name}.us.auth0.com/'),
    'ES_AUTH_JWT_AUDIENCE': os.environ.get('ES_AUTH_JWT_AUDIENCE', 'https://cri.com/{$project_name}'),

    'AUTH0_API_AUDIENCE': os.environ.get('AUTH0_API_AUDIENCE', 'https://{$project_name}.us.auth0.com/api/v2/'),
    'AUTH0_API_BASE_URL': os.environ.get('AUTH0_API_BASE_URL', 'https://{$project_name}.us.auth0.com/api/v2'),
    'AUTH0_CLAIMS_NAMESPACE': os.environ.get('AUTH0_CLAIMS_NAMESPACE', 'https://cri.com/{$project_name}'),
    'AUTH0_TOKEN_ENDPOINT': os.environ.get('AUTH0_TOKEN_ENDPOINT', 'https://{$project_name}.us.auth0.com/oauth/token'),
    'AUTH0_CLIENT_ID': os.environ.get('AUTH0_CLIENT_ID', '--your-client-id--'),
    'AUTH0_CLIENT_SECRET': os.environ.get('AUTH0_CLIENT_SECRET',
                                          '--your-client-secret--'),
                                          
    # NOTE: AUTH0_PUBLIC_KEY cannot be set by envar
    'AUTH0_PUBLIC_KEY': b'''
-----BEGIN PUBLIC KEY-----
    --your-public-key--
-----END PUBLIC KEY-----
'''
}

# cancellable
if SETTINGS['ES_AUTH_JWT_AUDIENCE'] == '':
    del SETTINGS['ES_AUTH_JWT_AUDIENCE']

for setting in SETTINGS:
    key = setting.upper()
    if ('PASSWORD' not in key) and ('SECRET' not in key):
        LOG.info('%s: %s', setting, SETTINGS[setting])
