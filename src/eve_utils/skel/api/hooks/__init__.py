import logging
import json
from utils import echo_message
import hooks._gateway
import hooks._error_handlers
import hooks._settings
import hooks._logs
from log_trace.decorators import trace
from configuration import SETTINGS

LOG = logging.getLogger('hooks')


@trace
def add_hooks(app):
    app.on_post_GET += _fix_links
    app.on_post_POST += _post_POST
    app.on_post_PATCH += _fix_links

    if SETTINGS.has_enabled('ES_ADD_ECHO'):
        @app.route('/_echo', methods=['PUT'])
        def _echo_message():
            return echo_message()

    hooks._gateway.add_hooks(app)
    hooks._error_handlers.add_hooks(app)
    hooks._settings.add_hooks(app)
    hooks._logs.add_hooks(app)


@trace
def _post_POST(resource, request, payload):
    if payload.status_code == 201:
        j = json.loads(payload.data)
        if '_items' in j:
            for item in j['_items']:
                _remove_unnecessary_links(item)
        else:
            _remove_unnecessary_links(j)

        if 'pretty' in request.args:
            payload.data = json.dumps(j, indent=4)
        else:
            payload.data = json.dumps(j)


@trace
def _fix_links(resource, request, payload):
    if payload.status_code in [200, 201]:
        j = json.loads(payload.data)

        if resource is None:
            _rewrite_schema_links(j)
        else:
            if '_items' in j:
                for item in j['_items']:
                    _process_item_links(item)
            else:
                _add_parent_link(j, resource)
            _process_item_links(j)

        payload.data = json.dumps(j, indent=4 if 'pretty' in request.args else None)


@trace
def _process_item_links(item):
    _remove_unnecessary_links(item)
    _add_missing_slashes(item)
    _insert_base_url(item)


@trace
def _rewrite_schema_links(item):
    base_url = SETTINGS.get('ES_BASE_URL') or ''

    if '_links' in item and 'child' in item['_links'] and len(item['_links']) == 1:
        old = item['_links']['child']
        del item['_links']['child']
        new_links = _create_new_schema_links(base_url, old)
        item['_links'] = new_links


@trace
def _create_new_schema_links(base_url, old_links):
    new_links = {
        'self': {'href': f'{base_url}/', 'title': 'endpoints'},
        'logging': {'href': f'{base_url}/_logging', 'title': 'logging'}
    }

    for link in old_links:
        if '<' not in link['href'] and not link['title'] == '_schema':
            rel = link['title'][1:] if link['title'].startswith('_') else link['title']
            link['href'] = f'{base_url}/{link["href"]}'
            new_links[rel] = link

    return new_links


@trace
def _remove_unnecessary_links(item):
    if 'related' in item.get('_links', {}):
        del item['_links']['related']


@trace
def _add_missing_slashes(item):
    if '_links' not in item:
        return
    for link in item['_links'].values():
        href = link.get('href')
        if href and not (href.startswith('/') or href.startswith('http://') or href.startswith('https://')):
            link['href'] = '/' + href


@trace
def _insert_base_url(item):
    if '_links' not in item:
        return
    base_url = SETTINGS.get('ES_BASE_URL') or ''
    for link in item['_links'].values():
        if link['href'].startswith('/'):
            link['href'] = f'{base_url}{link["href"]}'


@trace
def _add_parent_link(item, resource):
    item['_links']['parent'] = {
        'href': item['_links']['collection']['href'],
        'title': resource
    }
