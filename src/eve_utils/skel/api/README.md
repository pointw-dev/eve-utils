# {$project_name}

An Eve-based API, created with **[eve-utils](https://pointw.com/rapid-api-creation-with-eve-utils/)**.

## Getting Started

If you have created this api with docker support (`mkapi {$project_name} --with_docker`) then to launch your API with docker-compose:

`docker-compose up -d`

If you have created this api with serverless support (`mkapi {$project_name} --with_serverless`) then to launch your API:

`sls wsgi serve -p 2112`

If you did not add docker or serverless support, do the following (I recommend you first create a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/)):

```bash
cd {$project_name}
pip install -r requirements.txt
python run.py
```

Either way, the API is now running and its base endpoint is

http://localhost:2112 (for docker or for `python run.py`)


After making changes to the API, you must stop/start the API service.

## Configuration

The API is configured via environment variables.  These can be set in in several ways:

* Your OS

  * `set var=value` in Windows
  *  `export var=value` in Linux

* In `docker-compose.yml`

  ```yml
  environment:
   - var1=value1
   - var2=value2
  ```

* In serverless-XXX.yml

  ```yml
  environment:
    var1: value1
    var2: value2
  ```

* In `_env.conf` (this is useful to set values for use in your IDE, this file is listed in `.gitignore` and `.dockerignore` - lines that begin with `#` are treated as comments)  Takes precedence over OS envars.

  ```bash
  var1=value1
  var2=value2
  ```

The base variables are prefixed with ES_ for Eve Service.  The environment variables you can set are:

| Variable                  | Description                                                  | Default                                                     |
| ------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------- |
| ES_API_NAME               | The name of your API.  Appears in logs and emails.           | The name you used with `mkapi` (i.e. {$project_name})                              |
| ES_MONGO_ATLAS            | Set to Enabled (or True, or Yes) to use the following Mongo values to construct the MONGO_URI.  If disabled, will use a non-Atlas connection. | Disabled                                                    |
| ES_MONGO_HOST             |                                                              | localhost                                                   |
| ES_MONGO_PORT             | (ignored if ES_MONGO_ATLAS is enabled)                       | 27017                                                       |
| ES_MONGO_DBNAME           |                                                              | The name you used with `mkapi` (i.e. {$project_name})                             |
| ES_API_PORT               |                                                              | 2112                                                        |
| ES_INSTANCE_NAME          | This name appears in logs and in error emails                | The hostname the API is running on (`socket.gethostname()`) |
| ES_TRACE_LOGGING          | When enabled, causes logs to include enter/exit/exception details for each method - not something to have enabled in production. | Enabled                                                     |
| ES_PAGINATION_LIMIT       | Eve pass-through                                             | 3000                                                        |
| ES_PAGINATION_DEFAULT     | Eve pass-through                                             | 1000                                                        |
| ES_LOG_TO_FOLDER          | (disable if deploying as serverless as there is no folder to log to) | Enabled                                                     |
| ES_SEND_ERROR_EMAILS      | (only works if the following values are set)                 | Enabled                                                     |
| ES_SMTP_HOST              |                                                              | internal.cri.com                                            |
| ES_SMTP_PORT              |                                                              | 25                                                          |
| ES_ERROR_EMAIL_RECIPIENTS |                                                              | michael@pointw.com                                          |

Optional environment variables

| Variable             | Description                             |
| -------------------- | --------------------------------------- |
| ES_MONGO_USERNAME    | (required if ES_MONGO_ATLAS is enabled) |
| ES_MONGO_PASSWORD    | (required if ES_MONGO_ATLAS is enabled) |
| ES_MONGO_AUTH_SOURCE | Eve pass-through                        |
| ES_MEDIA_BASE_URL    | Eve pass-through                        |
| ES_PUBLIC_RESOURCES  | not yet implemented                     |

If using auth (e.g. `mkapi {$project_name} --with_auth` or `add_auth` )

| Variable               | Description                                                  | Default                                          |
| ---------------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| ES_AUTH_ADD_BASIC      | When enabled, allows a basic authentication scheme with root/password | No                                               |
| ES_AUTH_ROOT_PASSWORD  | When ES_AUTH_ADD_BASIC is enabled, this is the password the root user uses to gain access to the API. | password                                         |
| ES_AUTH_REALM          | Appears in the `WWW-Authenticate` header in unauthorized requests. | {$project_name}.pointw.com                       |
| ES_AUTH_JWT_DOMAIN     |                                                              | {$project_name}.us.auth0.com                     |
| ES_AUTH_JWT_AUDIENCE   | This is the identifier a client uses when requesting a token from the auth provider.  It is a URI only (identifier only), not an actual URL (i.e. no requests are made to it) | https://pointw.com/{$project_name}               |
| AUTH0_API_AUDIENCE     | When {$project_name} requests a token to use the Auth0 API, this is the audience for the token. | https://{$project_name}.us.auth0.com/api/v2/     |
| AUTH0_API_BASE_URL     | The base of the Auth0 API                                    | https://{$project_name}.us.auth0.com/api/v2      |
| AUTH0_CLAIMS_NAMESPACE | If you configure Auth0 to insert additional claims, use this value as a namespace (prefix). | https://pointw.com/{$project_name}               |
| AUTH0_TOKEN_ENDPOINT   | When {$project_name} needs to call the Auth0 API, it uses this endpoint to request a token. | https://{$project_name}.us.auth0.com/oauth/token |
| AUTH0_CLIENT_ID        | When {$project_name} needs to call the Auth0 API, it uses this client id/secret to authenticate.  These are not the client id/secret of your application. | --your-client-id--                               |
| AUTH0_CLIENT_SECRET    |                                                              | --your-client-secret--                           |

## Project Structure

| File | Description |
| ---- | ----------- |
| eve_service.py     | Defines the EveService class, the http server that powers the API. |
| run.py             | Instantiates an EveService object and starts it (with SIGTERM for docker stop). |
| settings.py        | Where you set the values of Eve [global configuration](https://docs.python-eve.org/en/stable/config.html#global-configuration) settings.  Key values are provided by `configuration/__init__.py` which are overridable by environment variables (or by `_env.conf`) |
| _env.conf          | Set temporary/dev values for settings here.  Will not be added to container build.  If not using containers, be sure not to copy this to production. |
| logging.yml        | Configuration of the Python logging module. |
| requirements.txt   | Standard file for listing python libraries/dependencies - install with `pip install -r requirements.txt` . |
| win_service.py     | *under development* - Lets you deploy the API as a windows service. |
| **configuration**  |   |
| &nbsp;&nbsp; \_\_init\_\_.py      | Settings used by the application (some set default Eve values in `settings.py` . |
| **domain**         | Where your domain resources will be created when you use `mkresource` . |
| &nbsp;&nbsp; common.py        | Fields applied to all resources (skipped if API was created with `--no_common` ). |
| &nbsp;&nbsp; _settings.py     | Defines the `/_settings` endpoint, which you GET to see the application settings. |
| &nbsp;&nbsp; \_\_init\_\_.py      | Wires up all resources and makes them available to `EveService` . |
| **hooks**            | Wires up [Eve event hooks](https://docs.python-eve.org/en/stable/features.html#eventhooks) for logging, relationship navigation, etc. |
| &nbsp;&nbsp; _error_handlers.py |   |
| &nbsp;&nbsp; _logs.py           |   |
| &nbsp;&nbsp; _settings.py       |   |
| &nbsp;&nbsp; \_\_init\_\_.py    | Add your custom hooks/routes here. |
| **log_trace**      | This module provides the @trace function decorator - you don't need to modify anything here. |
| &nbsp;&nbsp; decorators.py    |   |
| &nbsp;&nbsp; trace_level.py   |   |
| &nbsp;&nbsp; \_\_init\_\_.py      |   |
| **utils**          | Add application wide utility functions here. |
| &nbsp;&nbsp; \_\_init\_\_.py       | Defines `make_error_response()` (others coming soon). |
| **validation**     | This module is added when you run `add_val` . |
| &nbsp;&nbsp; validator.py     | Add custom validators to the `EveValidator` class defined here. |
| **auth**           | This module is added when you run `add_auth` (see docs for customization details). |
| &nbsp;&nbsp; auth0.py         | Methods to access/modify users information from Auth0. |
| &nbsp;&nbsp; auth_handlers.py | Where you add/modify authentication handlers, (e.g. if you wish to support Digest or custom auth scheme). |
| &nbsp;&nbsp; es_auth.py       | Defines `EveAuthService` which provides authentication to `EveService` . |
| &nbsp;&nbsp; \_\_init\_\_.py      | Defines the settings used by the `auth` module. |
