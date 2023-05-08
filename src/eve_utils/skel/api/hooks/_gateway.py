"""
hooks.logs
This module defines functions to log requests, and to manage log verbosity.
"""
import logging
import json
from flask import current_app as app
# from flask import abort, make_response, jsonify, request as flask_request
from log_trace.decorators import trace
# from utils import make_error_response

LOG = logging.getLogger('hooks.logs')


@trace
def add_hooks(app):
    app.on_post_GET += _embed_remote_parent_resource


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
            if remote_relation.get('embeddable', False):
                response = json.loads(payload.data)
                response[field] = {
                    'remote_id': response[field],
                    'embedded': {
                        'name': 'Stellantis',
                        'address': '123 Chrysler Way'
                    }
                }
                payload.data = json.dumps(response)

