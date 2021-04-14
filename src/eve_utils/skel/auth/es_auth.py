"""
The auth module used for ES.
"""
from bson.objectid import ObjectId
from eve_negotiable_auth import NegotiableAuth, AUTH_PARSER

from utils import get_db
from . import SETTINGS
from .auth_handlers import basic, bearer, bearer_challenge

AUTH_PARSER.add_handler('Bearer', bearer, bearer_challenge, realm=f'{SETTINGS["ES_AUTH_REALM"]}')
if SETTINGS['ES_AUTH_ADD_BASIC'][0] in 'tyTY':
    AUTH_PARSER.add_handler('Basic', basic, realm=f'{SETTINGS["ES_AUTH_REALM"]}')


class EveServiceAuth(NegotiableAuth):
    def __init__(self):
        super(EveServiceAuth, self).__init__()

    def process_claims(self, claims, allowed_roles, resource, method):
        authorized = 'user' in claims
        if not authorized:
            return False

        is_admin = claims.get('role') == 'admin'

        if not is_admin:
            auth_value = 'all-denied'
            accounts = get_db()['accounts']
            account = accounts.find_one({'user_id': claims['user']})
            if account:
                auth_value = ObjectId(account['_customer_ref'])
                claims['role'] = auth_value

            self.set_request_auth_value(auth_value)

        if resource in ['accounts', 'roles'] and not is_admin:
            authorized = False

        return authorized
