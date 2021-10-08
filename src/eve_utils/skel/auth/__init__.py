"""Home of the auth modules that govern access via Eve."""
import os
import logging
import jwt

LOG = logging.getLogger('auth')

SETTINGS = {
    'ES_AUTH_ADD_BASIC': os.environ.get('ES_AUTH_ADD_BASIC', 'No'),  # [0] in 'yYtT', i.e. yes, Yes, true, True
    'ES_AUTH_ROOT_PASSWORD': os.environ.get('ES_AUTH_ROOT_PASSWORD', 'password'),
    'ES_AUTH_REALM': os.environ.get('ES_AUTH_REALM', '{$project_name}.pointw.com'),

    'ES_AUTH_JWT_DOMAIN': os.environ.get('ES_AUTH_JWT_DOMAIN', '{$project_name}.us.auth0.com'),
    'ES_AUTH_JWT_ISSUER': os.environ.get('ES_AUTH_JWT_ISSUER', 'https://{$project_name}.us.auth0.com/'),
    'ES_AUTH_JWT_AUDIENCE': os.environ.get('ES_AUTH_JWT_AUDIENCE', 'https://pointw.com/{$project_name}'),

    'AUTH0_API_AUDIENCE': os.environ.get('AUTH0_API_AUDIENCE', 'https://{$project_name}.us.auth0.com/api/v2/'),
    'AUTH0_API_BASE_URL': os.environ.get('AUTH0_API_BASE_URL', 'https://{$project_name}.us.auth0.com/api/v2'),
    'AUTH0_CLAIMS_NAMESPACE': os.environ.get('AUTH0_CLAIMS_NAMESPACE', 'https://pointw.com/{$project_name}'),
    'AUTH0_TOKEN_ENDPOINT': os.environ.get('AUTH0_TOKEN_ENDPOINT', 'https://{$project_name}.us.auth0.com/oauth/token'),
    'AUTH0_CLIENT_ID': os.environ.get('AUTH0_CLIENT_ID', '--your-client-id--'),
    'AUTH0_CLIENT_SECRET': os.environ.get('AUTH0_CLIENT_SECRET',
                                          '--your-client-secret--')
}

JWK_CLIENT = jwt.PyJWKClient(f'https://{SETTINGS["ES_AUTH_JWT_DOMAIN"]}/.well-known/jwks.json')
_jwks = JWK_CLIENT.get_signing_keys()
SIGNING_KEYS = {jwk.key_id: jwk.key for jwk in _jwks}


# cancellable
if SETTINGS['ES_AUTH_JWT_AUDIENCE'] == '':
    del SETTINGS['ES_AUTH_JWT_AUDIENCE']

for setting in SETTINGS:
    key = setting.upper()
    if ('PASSWORD' not in key) and ('SECRET' not in key):
        LOG.info('%s: %s', setting, SETTINGS[setting])
