import json
import hooks._error_handlers
import hooks._settings
import hooks._logs
from log_trace.decorators import trace


@trace
def add_hooks(app):
    app.on_post_GET += _post_GET
    app.on_post_POST += _post_POST

    hooks._error_handlers.add_hooks(app)
    hooks._settings.add_hooks(app)
    hooks._logs.add_hooks(app)


def _post_POST(resource, request, payload):
    if payload.status_code == 201:
        j = json.loads(payload.data)
        if '_items' in j:
            for item in j['_items']:
                _edit_collection_link(request, item)
        else:
            _edit_collection_link(request, j)
        payload.data = json.dumps(j)


def _post_GET(resource, request, payload):
    if payload.status_code == 200:
        j = json.loads(payload.data)
        if '_items' in j:
            for item in j['_items']:
                _remove_unnecessary_links(item)
        else:
            _remove_unnecessary_links(j)

        if resource is None:
            _rewrite_schema_links(j)

        payload.data = json.dumps(j)


def _rewrite_schema_links(j):
    if '_links' in j and 'child' in j['_links'] and len(j['_links']) == 1:
        old = j['_links']['child']
        del j['_links']['child']
        new = {
            'self': {
                'href': '/',
                'title': 'endpoints'
            },
            'logging': {
                'href': '/_logging',
                'title': 'logging'
            }
        }

        for link in old:
            if '<' not in link['href'] and not link['title'] == '_schema':
                rel = link['title']
                if rel.startswith('_'):
                    rel = rel[1:]
                link['href'] = '/' + link['href']
                new[rel] = link
        j['_links'] = new


def _remove_unnecessary_links(item):
    if 'related' in item['_links']:
        del item['_links']['related']


def _edit_collection_link(request, item):
    _remove_unnecessary_links(item)

    item['_links']['collection'] = {
        'href': request.path
    }
