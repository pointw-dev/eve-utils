"""
Defines the resources that comprise the {$project_name} domain.
"""
from . import _settings


DOMAIN_DEFINITIONS = {
    '_settings': _settings.DEFINITION
}


DOMAIN_RELATIONS = {
    "create_json_form": {
        "url": 'create-form/<regex("[\w]+"):_resource>',
    },
    "edit_json_form": {
        "url": 'edit-form/<regex("[\w]+"):_resource>/<regex("[a-f0-9]{24}"):_resource_ref>/',
    },
}


DOMAIN = {**DOMAIN_DEFINITIONS, **DOMAIN_RELATIONS}
