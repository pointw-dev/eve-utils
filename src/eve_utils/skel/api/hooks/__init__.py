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
        payload.data = json.dumps(j)


def _remove_unnecessary_links(item):
    if 'related' in item['_links']:
        del item['_links']['related']


def _edit_collection_link(request, item):
    _remove_unnecessary_links(item)

    item['_links']['collection'] = {
        'href': request.path
    }
