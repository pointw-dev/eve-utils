"""
hooks.logs
This module defines functions to log requests, and to manage log verbosity.
"""
import logging
import json
from flask import abort, make_response, jsonify, request
from log_trace.decorators import trace
from utils import make_error_response

LOG = logging.getLogger('hooks.logs')


@trace
def add_hooks(app):
    """Wire up the events for logging"""
    app.on_post_GET += _log_request
    app.on_post_POST += _log_request
    app.on_post_PATCH += _log_request
    app.on_post_PUT += _log_request
    app.on_post_DELETE += _log_request

    @app.route('/_logging', methods=['GET'])
    def get_logging_config():
        """Returns the current verbosity levels for logging handlers."""
        if app.auth and not app.auth.authorized(None, '_logging', 'GET'):
            return make_error_response('Please provide proper credentials', 401)

        return _get_logging_config()

    @app.route('/_logging', methods=['PUT'])
    def put_logging_config():
        """PUT logging level to handlers."""
        if app.auth and not app.auth.authorized(None, '_logging', 'PUT'):
            return make_error_response('Please provide proper credentials', 401)

        return _put_logging_config(request)


@trace
def _log_request(resource, request, payload):
    """Event hook to log all requests."""
    LOG.info(f'Request for {resource}: {request} [{payload.status_code}]')
    LOG.debug(f'Request for {resource}: {request} [{payload.status_code}] '
              f'{request.values} {payload.data} [{request.headers}]')


@trace
def _get_logging_config():
    """Returns the verbosity for all handlers."""
    response = {}
    logger = logging.getLogger()
    for handler in logger.handlers:
        response[handler.name] = logging.getLevelName(handler.level)

    return make_response(jsonify(response), 200)


@trace
def _put_logging_config(request):
    """PUTs the verbosity for handlers."""
    try:
        if not request.content_type == 'application/json':
            raise TypeError('The request body must be application/json')

        payload = json.loads(request.data)

        logger = logging.getLogger()
        # first loop through to ensure everything is valid
        for key in payload:
            handler = [x for x in logger.handlers if x.name == key]
            if not handler:
                raise ValueError(f'{key} is not a valid log handler')
            try:
                getattr(logging, payload[key])
            except AttributeError:
                raise ValueError(f'{payload[key]} is not a valid log verbosity level')

        # now it's safe to iterate and change levels
        for key in payload:
            handler = [x for x in logger.handlers if x.name == key][0]
            handler.setLevel(getattr(logging, payload[key]))

        response = {}
        for handler in logger.handlers:
            response[handler.name] = logging.getLevelName(handler.level)

        return make_response(jsonify(response), 200)

    except (TypeError, ValueError) as ex:
        resp = make_error_response('Invalid log setting specification', 422, ex)
        abort(resp)

    except Exception as ex:
        resp = make_error_response('Could not change log settings', 500, ex)
        abort(resp)
