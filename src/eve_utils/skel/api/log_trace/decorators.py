"""
Function decorators used in this project
- @trace - log_trace entries and exits of decorated function
"""
import sys
import traceback
import logging
from functools import wraps

from io import StringIO
from six import reraise
from configuration import SETTINGS

LOG = logging.getLogger('trace')


def _trace(target):
    """
    This is a decorator that log_trace when the decorated function is entered and exited.
    Any unhandled exceptions raised by the decorated function are logged and re-raised.
    """

    @wraps(target)
    def _wrapper(*args, **kwargs):
        global return_value
        LOG.trace(
            'Entering function: [{0}].[{1}]'
                .format(
                target.__module__,
                target.__name__
            )
        )

        try:
            return_value = target(*args, **kwargs)
        except Exception as ex:  # pylint: disable=broad-except
            exc_type, exc_value, tr_back = sys.exc_info()
            LOG.trace(
                'Exiting function: [%s].[%s] by unhandled exception "%s"',
                target.__module__,
                target.__name__,
                ex
            )
            sbuf = StringIO()
            traceback.print_stack(file=sbuf)
            sbuf.seek(0)
            LOG.trace(sbuf.read())
            reraise(exc_type, exc_value, tr_back)

        LOG.trace(
            'Exiting function: [{0}].[{1}] by return'
                .format(
                target.__module__,
                target.__name__
            )
        )

        return return_value

    return _wrapper


def _trace_disabled():
    pass


trace = _trace_disabled
if SETTINGS.get('ES_TRACE_LOGGING') == 'Enabled':
    trace = _trace
