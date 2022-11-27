import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
# from oauthlib.oauth2 import LegacyApplicationClient as Client
from oauthlib.oauth2 import BackendApplicationClient as Client
from oauthlib.oauth2.rfc6749.errors import AccessDeniedError
from requests_oauthlib import OAuth2


def authorize(creds=None):
    client_id = creds.get('client_id')
    oauth = OAuth2Session(client=Client(client_id)) #, update_token=_update_token)
    try:
        token = oauth.fetch_token(
            token_url='https://cri-stellantis-dev.us.auth0.com/oauth/token',
            **creds
        )
    except AccessDeniedError as ex:
        print(ex)
        return None

    return OAuth2(client_id, Client(client_id), token)
    
    
    
REQUEST_TOKEN_URL = "https://cri-stellantis-dev.us.auth0.com/oauth/token"
def request_access_token(creds):
    auth = HTTPBasicAuth(creds['username'], creds['password'])
    print(f'{auth}')

    # # auth = HTTPBasicAuth(client_id, client_secret)
    # oauth = OAuth2Session(client=Client(client_id=creds['client_id']))
    # try:
    #     token = oauth.fetch_token(token_url=REQUEST_TOKEN_URL, audience='uri://cri.com/ishowroom-catalog-api', auth=auth)
    #     return token["access_token"]
    # except Exception as err:
    #     print(f"{err}")
    #     raise ValueError(err)



def main():
    creds = {
        'username': 'michael.ottoson@cri.com',
        'password': 'apple1Sauce!',
        'client_id': 'eKYFw6OKNq0XJesDNL0Xqt9cxKXIluqk',
        'client_secret': 'MCnHjbINgrD6VDllpmOmwGsgDhCUEcs9gj5xdAkrbZ50UHaadY8CXrODzgOTQZ3G',
        'audience': 'uri://cri.com/ishowroom-catalog-api'
    }
    # auth = authorize(creds)
    auth = request_access_token(creds)
    print(auth)



if __name__ == '__main__':
    main()
