import logging
from flask import jsonify, make_response
from flask import current_app


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


def is_enabled(setting):
    return setting[0].lower() in 'yte'
    # i.e. the following means setting is enabled:
    # - 'Yes' or 'yes' or 'Y' or 'y'
    # - 'True' or 'true' or 'T' or 't'
    # - 'Enabled' or 'enabled' or 'E' or 'e'

