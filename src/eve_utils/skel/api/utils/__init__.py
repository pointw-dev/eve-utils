import logging
from flask import jsonify, make_response
from flask import current_app


LOG = logging.getLogger('utils')


def get_db():
    return current_app.data.driver.db


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


