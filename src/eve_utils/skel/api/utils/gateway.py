import logging
import requests
from flask import current_app as app
from log_trace.decorators import trace
from requests.exceptions import ConnectionError
import json
from configuration import SETTINGS

LOG = logging.getLogger('gateway')
REGISTRATIONS = {}

def register(app):
    if not SETTINGS['ES_GATEWAY_URL']:
        return

    if not SETTINGS['ES_BASE_URL']:
        LOG.warning('ES_GATEWAY_URL is set, but cannot register because ES_BASE_URL is not set - cancelling')
        return

    url = f"{SETTINGS['ES_GATEWAY_URL']}/registrations"  # TODO: use _links[registrations]
    name = SETTINGS['ES_API_NAME'] if not SETTINGS['ES_NAME_ON_GATEWAY'] else SETTINGS['ES_NAME_ON_GATEWAY']
    base_url = SETTINGS['ES_BASE_URL']
    LOG.info(f'Registering with gateway as {name} at {base_url} to {url}')
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

        try:
            response = requests.get(url + '/' + name)
            if response.status_code == 404:
                response = requests.post(url, data=data, headers=headers)
            else:
                etag = response.json()['_etag']
                url = f"{SETTINGS['ES_GATEWAY_URL']}/{response.json()['_links']['self']['href']}"
                headers = {
                    'content-type': 'application/json',
                    'If-Match': etag
                }
                response = requests.put(url, data=data, headers=headers)
        except ConnectionError:
            LOG.warning(f'Could not connect to API gateway at {url} - cancelling')
        # TODO: handle response
    else:
        LOG.warning('No rels to register - cancelling')


def get_href_from_gateway(rel):
    global REGISTRATIONS
    url = f"{SETTINGS['ES_GATEWAY_URL']}/"
    etag = REGISTRATIONS.get('_etag')
    headers = {}
    if etag:
        headers = {
            'If-Not-Match': etag
        }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        REGISTRATIONS = response.json()

    # TODO: handle the very unlikely event that there are two of the same business resource
    # TODO: document how curies work, and how they are used to manage rel collisions - esp. for the non-business rels
    #  e.g. _logging, _settings, etc.
    return REGISTRATIONS.get('_links', {}).get(rel, {}).get('href', '')  # TODO: robustify


def _handle_post_from_remote(resource, request):
    if 'where' not in request.args:
        return
    where = json.loads(request.args['where'])  # ASSERT: is json format, etc.
    if not len(where) == 1:
        return
    field = list(where.keys())[0]
    remote_id = where[field]
    definition = app.config['DOMAIN'][resource]['schema'][field]
    remote_relation = definition.get('remote_relation', {})
    if not remote_relation:
        return

    j = json.loads(request.get_data())  # ASSERT: is json format, etc
    j[field] = remote_id
    request._cached_data = json.dumps(j).encode('utf-8')


@trace
def _embed_remote_parent_resource(resource, request, payload):
    embed_key = 'embedded'
    if embed_key not in request.args:
        return
    embeddable = json.loads(request.args[embed_key])
    for field in embeddable:
        if embeddable[field]:
            definition = app.config['DOMAIN'][resource]['schema'][field]
            remote_relation = definition.get('remote_relation', {})
            rel = remote_relation.get('rel')
            if rel and remote_relation.get('embeddable', False):
                response = json.loads(payload.data)
                if field in response:
                    response[field] = _get_embedded_resource(response[field], rel)
                elif '_items' in response:
                    for item in response['_items']:
                        if field in item:
                            item[field] = _get_embedded_resource(item[field], rel)

                payload.data = json.dumps(response)


@trace
def _get_embedded_resource(remote_id, rel):
    if not SETTINGS['ES_GATEWAY_URL']:
        return

    url = f'{get_href_from_gateway(rel)}/{remote_id}'
    response = requests.get(url)
    # ASSERT: ok

    return {
        "_remote": {
            "id": remote_id,
            "rel": rel,
            "href": url
        },
        **response.json()
    }
