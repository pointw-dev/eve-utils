import os
import click
from libcst import parse_module

from .optional_flags import OptionalFlags
from .singplu import get_pair
import eve_utils

from ..code_gen.affordance_inserter import AffordanceInserter


@click.group(name='affordance', help='Manage link rels that operate on the state of resources.')
def commands():
    pass


@commands.command(cls=OptionalFlags, name='create',
                  help='Creates an affordance, adds a route, and _links to a resource')
@click.argument('affordance_name', metavar='<name>')
@click.argument('resource_name', metavar='<resource>')
@click.option('folder', '--folder', is_flag=True, flag_value='root', help='Which folder to put this affordance in.')
def create(affordance_name, resource_name, folder):
    """
    Creates an affordance, adds a route from a resource, and wires the affordance's
    path into the _links of a given resource.
    """
    try:
        eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    # TODO: SLAP!
    # TODO: Use LinkAdder pattern
    affordance = f'affordances.{folder + "." if folder else ""}{affordance_name}'
    creating = f'Creating {affordance} and attaching to {resource_name}'
    if folder == 'root':
        folder = None
    if os.path.exists(f'affordances{"/"+folder if folder else ""}/{affordance_name}.py'):
        return eve_utils.escape(f'{affordance} already exists', 1001)
    click.echo(creating)

    if not os.path.exists('affordances'):
        os.mkdir('affordances')
    os.chdir('affordances')

    if folder:
        if not os.path.exists(folder):
            os.mkdir(folder)
        os.chdir(folder)

    _write_affordance_file(affordance_name, resource_name)

    with open(f'__init__.py', 'a') as file:
        file.write(f'from . import {affordance_name}\n')
    if folder:
        os.chdir('..')
        with open(f'__init__.py', 'a') as file:
            file.write(f'from . import {folder}\n')
    os.chdir('..')

    _add_affordance_resource(affordance_name, folder, resource_name)


@commands.command(cls=OptionalFlags, name='attach', help='(not yet implemented)')
@click.argument('affordance_name', metavar='<name>')
@click.argument('resource_name', metavar='<resource>')
@click.option('folder', '--folder', is_flag=True, flag_value='root', help='Which folder to put this affordance in.')
def attach(affordance_name, resource_name, folder):
    """
    Creates a route to previously created affordance for a resource, and wires the affordance's
    route into the _links of the resource.
    """
    click.echo(f'Attaching affordances.{folder + "." if folder else ""}{affordance_name} to {resource_name}')


@commands.command(name='list', help='(not yet implemented)')
def list_affordances():
    click.echo('list')


@commands.command(name='remove', help='(not yet implemented)')
def remove():
    click.echo('remove')


def _write_affordance_file(affordance_name, resource_name):
    singular, plural = get_pair(resource_name)
    bracketed_id = f'{{{singular}_id}}'
    with open(f'{affordance_name}.py', 'w') as file:
        file.write(f'''"""
This module defines functions to add the {affordance_name} affordance.
"""
import logging
from utils import make_error_response, unauthorized_message, get_resource_id, get_id_field

LOG = logging.getLogger("affordances.{affordance_name}")


def add_affordance(app):
    @app.route("/{plural}/<{singular}_id>/{affordance_name}", methods=["PUT"])
    def do_{affordance_name}({singular}_id):
        if app.auth and (not app.auth.authorized(None, "{affordance_name}", "PUT")):
            return make_error_response(unauthorized_message, 401)

        return _do_{affordance_name}({singular}_id)


def add_link({singular}):
    base_url = SETTINGS.get('ES_BASE_URL', '')
    {singular}_id = get_resource_id('{plural}', {singular})

    {singular}['_links']['{affordance_name}'] = {{
        'href': f'/{plural}/{bracketed_id}/{affordance_name}',
        'title': 'PUT to do {affordance_name}'    
    }}


def _do_{affordance_name}({singular}_id):
    LOG.info(f'_do_{affordance_name}: {singular}_id')

''')


def _add_affordance_resource(affordance_name, folder, resource):
    singular, plural = get_pair(resource)
    with open(f'hooks/{plural}.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = AffordanceInserter(affordance_name, folder, singular, plural)
    new_tree = tree.visit(inserter)

    with open(f'hooks/{plural}.py', 'w') as source:
        source.write(new_tree.code)


