from auth0.v3.authentication import GetToken

env = 'dev'


if env == 'dev':
    domain = 'cri-stellantis-dev.us.auth0.com'
    client_id = 'eKYFw6OKNq0XJesDNL0Xqt9cxKXIluqk'
    client_secret = 'MCnHjbINgrD6VDllpmOmwGsgDhCUEcs9gj5xdAkrbZ50UHaadY8CXrODzgOTQZ3G'
    user = 'support_scripts@cri.com'
    password = 'ij9eF.QMvw4sC(NU,mkh'
    audience = 'uri://cri.com/ishowroom-catalog-api'
elif env == 'uat':
    domain = 'cri-stellantis-dev.us.auth0.com'
    client_id = 'eKYFw6OKNq0XJesDNL0Xqt9cxKXIluqk'
    client_secret = 'MCnHjbINgrD6VDllpmOmwGsgDhCUEcs9gj5xdAkrbZ50UHaadY8CXrODzgOTQZ3G'
    user = 'support_scripts@cri.com'
    password = 'ij9eF.QMvw4sC(NU,mkh'
    audience = 'uri://cri.com/ishowroom-catalog-api'


sdk = GetToken(domain)
response = sdk.login(client_id,
   client_secret,
   user,
   password,
   'openid offline_access',
   'Username-Password-Authentication', # also change this
   audience=audience,
   # grant_type='password'
   grant_type='http://auth0.com/oauth/grant-type/password-realm',
)
token = response['access_token']


print(token)
