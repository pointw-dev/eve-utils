import os
import click
import itertools
import glob
from pathlib import Path
from libcst import *
from singplu import get_pair
from .code_gen import DomainDefinitionInserter, HooksInserter
from . import utils


def create_resource_domain_file(resource, add_common):
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


def create_resource_hook_file(singular, plural):
    with open(f'hooks/{plural}.py', 'w') as file:
        file.write(f'''"""
hooks.{plural}
This module defines functions to add link relations to {plural}.
"""
import json
from log_trace.decorators import trace


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


@trace
def _add_links_to_{singular}({singular}):
    {singular}['_links']['self'] = {{
        'href': f"/{plural}/{{{singular}['_id']}}",
        'title': '{singular}'
    }}
''')


def insert_domain_definition(resource):
    with open('domain/__init__.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = DomainDefinitionInserter(resource)
    new_tree = tree.visit(inserter)

    with open('domain/__init__.py', 'w') as source:
        source.write(new_tree.code)


def insert_hooks(resource):
    with open('hooks/__init__.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = HooksInserter(resource)
    new_tree = tree.visit(inserter)

    with open('hooks/__init__.py', 'w') as source:
        source.write(new_tree.code)


@click.group(name='resource')
def commands():
    pass


@commands.command(name='create')
@click.argument('resource_name', metavar='<name>')
@click.option('--no_common', '-c', is_flag=True, help='Do not add common fields to this resource')
def create(resource_name, no_common):
    """<name> of the resource to create"""  
    try:
        utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        print('This command must be run in an eve_service API folder structure')
        return

    singular, plural = get_pair(resource_name)    
    add_common = not no_common
    
    print(f'Creating {plural} resource')
    create_resource_domain_file(plural, add_common)
    insert_domain_definition(plural)
    create_resource_hook_file(singular, plural)
    insert_hooks(plural)


@commands.command(name='list')
def list():
    try:
        utils.jump_to_api_folder('src/{project_name}/domain')
    except RuntimeError:
        print('This command must be run in an eve_service API folder structure')
        return
        
    files = glob.glob('./*.py')
    for file in files:
        resource = Path(file).stem
        if resource.startswith('_'):
            continue
        print('- ' + file[2:-3])
        


@commands.command(name='remove')
def remove():
    click.echo('remove')
