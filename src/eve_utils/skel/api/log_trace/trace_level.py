"""Defines TRACE logging verbosity"""
import logging

TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, 'TRACE')


def trace(self, message, *args, **kws):
    """Extends logging with TRACE level"""
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kws)  # pylint: disable=protected-access


logging.Logger.trace = trace
