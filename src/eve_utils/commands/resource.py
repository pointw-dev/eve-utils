import os
import click
import glob
from pathlib import Path
from .command_help_order import CommandHelpOrder
from eve_utils.code_gen import \
    DomainDefinitionInserter, \
    HooksInserter, \
    DomainResourceRemover, \
    HooksRemover, \
    ParentReferenceRemover, \
    ChildLinksRemover
import eve_utils


@click.group(name='resource',
             help='Manage the resources that make up the domain of the service.',
             cls=CommandHelpOrder)
def commands():
    pass


@commands.command(name='create',
                  short_help='Create a new resource and add it to the domain.',
                  help_priority=1)
@click.argument('resource_name', metavar='<name>')
@click.option('--no_common', '-c', is_flag=True, help='Do not add common fields to this resource')
def create(resource_name, no_common):
    """Create a new resource and add it to the domain.

    <name> of the resource to create.  Enter either singular or plural and eve_utils will choose the other. Or enter both singular and plural separted by a comma.

           e.g. if you enter "cactus" eve-utils mistakenly believes that is the plural of "cactu" so enter "cactus,cactuses" or "cactus,cacti" to override eve-util's decision"""
    try:
        eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    singular, plural = eve_utils.get_singular_plural(resource_name)
    if _is_resource_name_is_invalid(singular, plural):
        return eve_utils.escape(f'The resource name ({resource_name}) is invalid', 701)

    add_common = not no_common

    print(f'Creating {plural} resource')
    if _resource_already_exists(plural):
        eve_utils.escape('This resource already exist', 702)
    else:
        # resource_already_exists() jumps to a different folder, need to jump back.
        # No need to try/except - we know we're in an API folder
        eve_utils.jump_to_api_folder('src/{project_name}')

        _create_resource_domain_file(plural, add_common)
        _insert_domain_definition(plural)
        _create_resource_hook_file(singular, plural)
        _insert_hooks(plural)


@commands.command(name='list',
                  short_help='List the resources in the domain.',
                  help_priority=2)
def list_resources():
    resources_list = _get_resource_list()
    for resource in resources_list:
        print('- ' + resource)


@commands.command(name='remove',
                  short_help='Remove a resource',
                  help_priority=3)
@click.argument('resource_name', metavar='<name>')
def remove(resource_name):
    try:
        eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    singular, plural = eve_utils.get_singular_plural(resource_name)
    if _is_resource_name_is_invalid(singular, plural):
        return eve_utils.escape(f'The resource name ({resource_name}) is invalid', 701)

    if not _resource_already_exists(plural):
        eve_utils.escape('This resource does not exist', 703)

    eve_utils.jump_to_api_folder('src/{project_name}')
    _remove_domain_definition(plural)
    _remove_hooks(plural)
    _delete_resource_files(plural)
    _remove_references_from_children(plural)
    _remove_child_links(plural)


@commands.command(name='check',
                  short_help='See what the singular/plural of the resource will be.',
                  help_priority=4)
@click.argument('resource_name', metavar='<name>')
def check(resource_name):
    """See what the singular or plural of a resource name will be

    <name> of the resource to check.  Enter singular or plural to see what eve-utils will choose for the other."""

    singular, plural = eve_utils.get_singular_plural(resource_name)
    click.echo(f'You entered {resource_name}')
    click.echo(f'- singular: {singular}')
    click.echo(f'- plural:   {plural}')

    click.echo(f'A resource named {plural} ' +
               ('already exists' if _resource_already_exists(plural) else 'does not exist'))


def _resource_already_exists(resource_name):
    resources_list = _get_resource_list()
    return resource_name in resources_list


def _is_resource_name_is_invalid(singular, plural):
    # TODO: check validity of names
    return False


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
        'url': r'regex("[\w]+")',
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
    DomainDefinitionInserter(resource).transform('domain/__init__.py')


def _insert_hooks(resource):
    HooksInserter(resource).transform('hooks/__init__.py',)


def _remove_domain_definition(resource):
    DomainResourceRemover(resource).transform('domain/__init__.py')


def _remove_hooks(resource):
    HooksRemover(resource).transform('hooks/__init__.py')


def _delete_resource_files(resource):
    domain_filename = f'domain/{resource}.py'
    hooks_filename = f'hooks/{resource}.py'

    eve_utils.remove_file_if_exists(domain_filename)
    eve_utils.remove_file_if_exists(hooks_filename)

    domain_file_exists = os.path.exists(domain_filename)
    hooks_file_exists = os.path.exists(hooks_filename)

    if domain_file_exists or hooks_file_exists:
        which = ''
        which += domain_filename if domain_file_exists else ''
        if hooks_file_exists:
            which += ', ' if which else ''
            which += hooks_filename
        eve_utils.escape(f'Could not delete resource files: {which}', 704)


def _remove_references_from_children(resource):
    files = glob.glob('domain/*.py')
    for filename in [file for file in files if not (file.startswith('domain/_') or file.startswith('domain\\_'))]:
        ParentReferenceRemover(resource).transform(filename)


def _remove_child_links(resource):
    files = glob.glob('hooks/*.py')
    for filename in [file for file in files if not (file.startswith('hooks/_') or file.startswith('hooks\\_'))]:
        ChildLinksRemover(resource).transform(filename)
