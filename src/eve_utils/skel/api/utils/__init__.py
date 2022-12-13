import logging
import requests
import json
from flask import jsonify, make_response
from flask import current_app, request
from . import log_setup
from configuration import SETTINGS

LOG = logging.getLogger('utils')

unauthorized_message = {
    "_status": "ERR",
    "_error": {
        "message": "Please provide proper credentials",
        "code": 401
    }
}


def get_db():
    return current_app.data.driver.db


def get_api():
    return current_app.test_client()


def make_error_response(message, code, issues=[], **kwargs):
    if 'exception' in kwargs:
        ex = kwargs.get('exception')
        LOG.exception(message, ex)

        if ex:
            issues.append({
                'exception': {
                    'name': type(ex).__name__,
                    'type': ".".join([type(ex).__module__, type(ex).__name__]),
                    'args': ex.args
                }
            })

    resp = {
        '_status': 'ERR',
        '_error': {
            'message': message,
            'code': code
        }
    }

    if issues:
        resp['_issues'] = issues

    return make_response(jsonify(resp), code)


def register_with_gateway(app):
    if not SETTINGS['ES_API_GATEWAY']:
        return

    if not SETTINGS['ES_BASE_URL']:
        LOG.warning('ES_API_GATEWAY is set, but cannot register with gateway because ES_BASE_URL is not set')
        return

    url = f"{SETTINGS['ES_API_GATEWAY']}/registrations"
    name = SETTINGS['ES_API_NAME'] if not SETTINGS['ES_API_GATEWAY_NAME'] else SETTINGS['ES_API_GATEWAY_NAME']
    base_url = SETTINGS['ES_BASE_URL']
    LOG.info(f'registering with gateway as {name} at {base_url} to {url}')
    api = app.test_client()
    response = api.get('/')
    j = response.json
    rels = j.get('_links', {})

    if rels:
        body = {
            'name': name,
            'baseUrl': base_url,
            'rels': rels
        }
        data = json.dumps(body)
        headers = {'content-type': 'application/json'}

        response = requests.get(url + '/' + name)
        if response.status_code == 404:
            response = requests.post(url, data=data, headers=headers)
        else:
            etag = response.json()['_etag']
            url = f"{SETTINGS['ES_API_GATEWAY']}/{response.json()['_links']['self']['href']}"
            headers = {
                'content-type': 'application/json',
                'If-Match': etag
            }
            print('=====>', data, '<====')
            response = requests.put(url, data=data, headers=headers)
        # TODO: handle response
    else:
        LOG.warning('No rels to register - cancelling')


def echo_message():
    log = logging.getLogger('echo')
    message = 'PUT {"message": {}/"", "status_code": int}, content-type: "application/json"'
    status_code = 400
    if request.is_json:
        try:
            status_code = int(request.json.get('status_code', status_code))
            message = request.json.get('message', message)
        except ValueError:
            pass

    if status_code < 400:
        log.info(message)
    elif status_code < 500:
        log.warning(message)
    else:
        log.error(message)

    return make_response(jsonify(message), status_code)
