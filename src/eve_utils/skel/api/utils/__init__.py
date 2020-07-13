import logging
from flask import jsonify, make_response

LOG = logging.getLogger('utils')


def make_error_response(message, code, issues=[], **kwargs):
    if 'exception' in kwargs:
        ex = kwargs.get('exception')
        LOG.exception(message, ex)

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


