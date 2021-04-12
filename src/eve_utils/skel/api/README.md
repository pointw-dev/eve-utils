# {$project_name}

An Eve-based API, brought to you by **[eve-utils](https://pointw.com/rapid-api-creation-with-eve-utils/)**.

## Getting Started

If you have created this api with docker support (`mkapi {$project_name} --with_docker`) then to launch your API with docker-compose:

`docker-compose up -d`

If you did not add docker support do the following (I recommend you first create a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/)):

```bash
cd {$project_name}
pip install -r requirements.txt
python run.py
```

Either way, the API is now running and its base endpoint is

http://localhost:2112

After making changes to the API, you must stop/start the API service.

## Project Structure


| File | Description |
| ---- | ----------- |
| eve_service.py     | Defines the EveService class, the http server that powers the API. |
| run.py             | Instantiates an EveService object and starts it (with SIGTERM for docker stop). |
| settings.py        | Where you set the values of Eve [global configuration](https://docs.python-eve.org/en/stable/config.html#global-configuration) settings. |
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
