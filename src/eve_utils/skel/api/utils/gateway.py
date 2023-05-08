import logging
import requests
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
