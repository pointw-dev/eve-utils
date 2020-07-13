import logging
from eve import Eve
from flask_cors import CORS
import hooks
from configuration import SETTINGS

LOG = logging.getLogger('{$project_name}')


class EveService:
    def __init__(self):
        self._name = SETTINGS.get('ES_API_NAME', '{$project_name}')
        self._app = Eve(import_name=self._name)  # , auth=Auth, validator=Validator
        CORS(self._app)
        hooks.add_hooks(self._app)

    def start(self):
        border = '-' * (23 + len(self._name))
        LOG.info(border)
        LOG.info(f'****** STARTING {self._name} ******')
        LOG.info(border)
        try:
            self._app.run(host='0.0.0.0', port=SETTINGS.get('ES_API_PORT'), threaded=True)
        except Exception as ex:  # pylint: disable=broad-except
            LOG.exception(ex)
        finally:
            LOG.info(border)
            LOG.info(f'****** STOPPING {self._name} ******')
            LOG.info(border)

    def stop(self):
        self._app.do_teardown_appcontext()
