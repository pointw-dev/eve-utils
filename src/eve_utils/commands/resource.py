import sys
import click
import glob
from pathlib import Path
from libcst import *
from eve_utils.code_gen import DomainDefinitionInserter, HooksInserter
import eve_utils


@click.group(name='resource', help='Manage the resources that make up the domain of the service.')
def commands():
    pass


@commands.command(name='create', help='Create a new resource and add it to the domain.')
@click.argument('resource_name', metavar='<name>')
@click.option('--no_common', '-c', is_flag=True, help='Do not add common fields to this resource')
def create(resource_name, no_common):
    """<name> of the resource to create"""
    try:
        eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    singular, plural = eve_utils.get_singular_plural(resource_name)
    add_common = not no_common

    print(f'Creating {plural} resource')
    if _resource_already_exists(plural):
        eve_utils.escape('This resource already exist', 701)
    else:
        # resource_already_exists() jumps to a different folder, need to jump back.
        # No need to try/except - we know we're in an API folder
        eve_utils.jump_to_api_folder('src/{project_name}')

        _create_resource_domain_file(plural, add_common)
        _insert_domain_definition(plural)
        _create_resource_hook_file(singular, plural)
        _insert_hooks(plural)


@commands.command(name='check', help='See what the singular/plural of the resource will be.')
@click.argument('resource_name', metavar='<name>')
def create(resource_name):
    """<name> of the resource to create"""
    singular, plural = eve_utils.get_singular_plural(resource_name)
    click.echo(f'You entered {resource_name}')
    click.echo(f'- singular: {singular}')
    click.echo(f'- plural:   {plural}')


@commands.command(name='list', help='List the resources in the domain.')
def list_resources():
    resources_list = _get_resource_list()
    for resource in resources_list:
        print('- ' + resource)


@commands.command(name='remove', help='(not yet implemented)')
def remove():
    click.echo('remove')


def _resource_already_exists(resource_name):
    resources_list = _get_resource_list()
    return resource_name in resources_list


def _get_resource_list():
    try:
        eve_utils.jump_to_api_folder('src/{project_name}/domain')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    files = glob.glob('./*.py')
    resources = []
    for file in files:
        resource = Path(file).stem
        if resource.startswith('_'):
            continue
        resources.append(file[2:-3])
    return resources


def _create_resource_domain_file(resource, add_common):
    with open(f'domain/{resource}.py', 'w') as file:
        file.write(f'''"""
Defines the {resource} resource.
"""
''')

        if add_common:
            file.write('from domain._common import COMMON_FIELDS\n\n\n')

        file.write('''SCHEMA = {
    'name': {
        'type': 'string',
        'required': True,
        'empty': False,
        'unique': True
    },
    'description': {
        'type': 'string'
    }
}

''')

        if add_common:
            file.write('SCHEMA.update(COMMON_FIELDS)\n\n')

        file.write('''DEFINITION = {
    'schema': SCHEMA,
    'datasource': {
        'projection': {'_tenant': 0}
    },
    'additional_lookup': {
        'url': 'regex("[\w]+")',  # pylint: disable=anomalous-backslash-in-string
        'field': 'name'
    }
}
''')


def _create_resource_hook_file(singular, plural):
    with open(f'hooks/{plural}.py', 'w') as file:
        file.write(f'''"""
hooks.{plural}
This module defines functions to add link relations to {plural}.
"""
import logging
import json
from flask import current_app
from log_trace.decorators import trace
from configuration import SETTINGS
from utils import get_resource_id, get_id_field
from utils.gateway import get_href_from_gateway

LOG = logging.getLogger('hooks.{plural}')


@trace
def add_hooks(app):
    """Wire up the hooks for {plural}."""
    app.on_fetched_item_{plural} += _add_links_to_{singular}
    app.on_fetched_resource_{plural} += _add_links_to_{plural}_collection
    app.on_post_POST_{plural} += _post_{plural}


@trace
def _post_{plural}(request, payload):
    if payload.status_code == 201:
        j = json.loads(payload.data)
        if '_items' in j:
            for {singular} in j['_items']:
                _add_links_to_{singular}({singular})
        else:
            _add_links_to_{singular}(j)
        payload.data = json.dumps(j)


@trace
def _add_links_to_{plural}_collection({plural}_collection):
    for {singular} in {plural}_collection['_items']:
        _add_links_to_{singular}({singular})
        
    if '_links' in {plural}_collection:
        base_url = SETTINGS.get('ES_BASE_URL', '')

        id_field = get_id_field('{plural}')
        if id_field.startswith('_'):
            id_field = id_field[1:]        
                
        {plural}_collection['_links']['item'] = {{
            'href': f'{{base_url}}/{plural}/{{{{{{id_field}}}}}}',
            'title': '{singular}',
            'templated': True
        }}


@trace
def _add_links_to_{singular}({singular}):
    base_url = SETTINGS.get('ES_BASE_URL', '')
    {singular}_id = get_resource_id('{plural}', {singular})

    _add_remote_children_links({singular})
    _add_remote_parent_links({singular})

    {singular}['_links']['self'] = {{
        'href': f"{{base_url}}/{plural}/{{{singular}_id}}",
        'title': '{singular}'
    }}

    
@trace
def _add_remote_children_links({singular}):
    if not SETTINGS['ES_GATEWAY_URL']:
        return
    {singular}_id = get_resource_id('{plural}', {singular})

    # == do not edit this method above this line ==    

    
@trace
def _add_remote_parent_links({singular}):
    if not SETTINGS['ES_GATEWAY_URL']:
        return
    {singular}_id = get_resource_id('{plural}', {singular})

    # == do not edit this method above this line ==    
''')


def _insert_domain_definition(resource):
    with open('domain/__init__.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = DomainDefinitionInserter(resource)
    new_tree = tree.visit(inserter)

    with open('domain/__init__.py', 'w') as source:
        source.write(new_tree.code)


def _insert_hooks(resource):
    with open('hooks/__init__.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = HooksInserter(resource)
    new_tree = tree.visit(inserter)

    with open('hooks/__init__.py', 'w') as source:
        source.write(new_tree.code)
