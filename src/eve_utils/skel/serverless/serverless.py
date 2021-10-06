import logging
from eve import Eve
from flask_cors import CORS
import hooks
from configuration import SETTINGS

LOG = logging.getLogger('{$project_name}')

name = SETTINGS.get('ES_API_NAME', '{$project_name}')
app = Eve(import_name=name)
CORS(app)
hooks.add_hooks(app)

LOG.info('Starting serverless')
