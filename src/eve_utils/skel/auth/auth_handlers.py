import os
import jwt
from base64 import b64decode
from auth import SETTINGS


def basic(token, **kwargs):
    try:
        username, password = b64decode(token).decode().split(':', 1)
        is_root = False
        if username.lower() == 'root':
            if password == SETTINGS.get('ES_AUTH_ROOT_PASSWORD'):
                is_root = True
            else:
                return {}

        role = 'admin' if is_root else ''
        rtn = {
            'user': username,
            'role': role
        }
    except:
        rtn = {}

    return rtn


# TODO: detect opaque token, then handle accordingly (how?)
def bearer(token, **kwargs):
    client_id = SETTINGS.get('ES_AUTH_JWT_CLIENT_ID')
    domain = SETTINGS.get('ES_AUTH_JWT_DOMAIN')
    audience = SETTINGS.get('ES_AUTH_JWT_AUDIENCE')
    issuer = SETTINGS.get('ES_AUTH_JWT_ISSUER')

    options = {}

    if audience:
        options['audience'] = audience
    if issuer:
        options['issuer'] = issuer

    options['algorithm'] = 'RS256'  # TODO: how to detect the actual algo?

    try:
        headers = jwt.get_unverified_header(token)

        parsed = jwt.decode(token, SETTINGS['AUTH0_PUBLIC_KEY'], **options)
        rtn = {
            'user': parsed.get('sub')
        }

        claims_namespace = SETTINGS['AUTH0_CLAIMS_NAMESPACE']

        for claim in ['roles', 'acl', 'email', 'name', 'nickname']:
            value = parsed.get(f'{claims_namespace}/{claim}')
            if value:
                rtn[claim] = value
        if 'roles' in rtn:
            rtn['roles'] = [role.lower() for role in rtn['roles']]
            if 'admin' in rtn['roles']:
                rtn['role'] = 'admin'

    except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.InvalidAudienceError, jwt.InvalidAlgorithmError) as ex:  # TODO: other jwt ex's?
        # TODO: how to return detail to user - abort 401 here with message?
        rtn = None
    except ValueError as ex:
        rtn = None
    except Exception as ex:  # TODO: handle differently?  end result is the same though...
        rtn = None

    return rtn


def bearer_challenge(**kwargs):
    request = kwargs.get('request')
    rtn = {}
    if request:
        if 'Bearer' in request.headers.get('Authorization', '') or request.args.get('access_token'):
            rtn['error'] = "invalid_token"

    return rtn
