import logging
from eve import Eve
from flask_cors import CORS
from flask_socketio import SocketIO
import hooks
import web_socket
from configuration import SETTINGS


LOG = logging.getLogger('myapi')


class EveService:
    def __init__(self):
        self._name = SETTINGS.get('ES_API_NAME', 'myapi')
        self._app = Eve(import_name=self._name)
        self._socket = SocketIO(self._app, async_mode=None, path='/_ws/socket.io', cors_allowed_origins='*')
        CORS(self._app)
        hooks.add_hooks(self._app)
        web_socket.initialize(self._app, self._socket)

    def start(self):
        border = '-' * (23 + len(self._name))
        LOG.info(border)
        LOG.info(f'****** STARTING {self._name} ******')
        LOG.info(border)
        try:
            self._socket.run(self._app, host='0.0.0.0', port=SETTINGS.get('ES_API_PORT'))
        except Exception as ex:  # pylint: disable=broad-except
            LOG.exception(ex)
        finally:
            LOG.info(border)
            LOG.info(f'****** STOPPING {self._name} ******')
            LOG.info(border)

    def stop(self):
        self._app.do_teardown_appcontext()
