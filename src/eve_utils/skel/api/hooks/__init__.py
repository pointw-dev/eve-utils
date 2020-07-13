import hooks._error_handlers
import hooks._settings
import hooks._logs
from log_trace.decorators import trace


@trace
def add_hooks(app):
    hooks._error_handlers.add_hooks(app)
    hooks._settings.add_hooks(app)
    hooks._logs.add_hooks(app)
