import os
import re
import glob
import click
from .command_help_order import CommandHelpOrder
from .optional_flags import OptionalFlags
from eve_utils.code_gen import AffordanceInserter
import eve_utils


ROUTE_TEMPLATE = """    @app.route("/{plural}/<{singular}_id>/{affordance_name}", methods=["PUT"])
    def do_{affordance_name}_{singular}({singular}_id):
        if app.auth and (not app.auth.authorized(None, "{affordance_name}", "PUT")):
            return make_error_response(unauthorized_message, 401)

        return _do_{affordance_name}_{singular}({singular}_id)
"""

HANDLER_TEMPLATE = """def _do_{affordance_name}_{singular}({singular}_id):
    LOG.info(f'_do_{affordance_name}_{singular}: {{{singular}_id}}')
"""


@click.group(name='affordance',
             help='Manage link rels that operate on the state of resources.',
             cls=CommandHelpOrder)
def commands():
    pass


@commands.command(name='create',
                  short_help='Creates an affordance, adds a route, and _links to a resource',
                  cls=OptionalFlags,
                  help_priority=1)
@click.argument('affordance_name', metavar='<name>')
@click.argument('resource_name', metavar='<resource>')
def create(affordance_name, resource_name):
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
    # TODO: refactor affordance/folder parse
    folder = None
    if '.' in affordance_name:
        # ASSERT: folder was not specified (else warn? abort?)
        # ASSERT: only one dot in affordance_name
        folder, affordance_name = affordance_name.split('.')
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


@commands.command(name='list',
                  short_help='List the affordances in the API',
                  help_priority=2)
def list_affordances():
    """
    Lists affordances previously created
    """
    try:
        eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    if not os.path.exists('affordances'):
        click.echo('There are no affordances')
        return

    os.chdir('affordances')
    files = glob.glob('**/*.py', recursive=True)
    for filename in files:
        with open(filename, 'r') as f:
            contents = f.read()
        if 'def add_affordance(app):' in contents:
            affordance = filename.replace('\\', '.').replace('/', '.')[:-3]
            attaches = re.findall(r'@app\.route\(\"\/(.*?)\/', contents)
            click.echo(f'- affordances.{affordance}')
            click.echo('   attached to:')
            for attached in attaches:
                click.echo(f'   - {attached}')


@commands.command(name='remove',
                  short_help='(not yet implemented)',
                  help_priority=3)
def remove():
    click.echo('remove')


@commands.command(name='attach',
                  short_help='(not yet implemented)',
                  cls=OptionalFlags,
                  help_priority=4)
@click.argument('affordance_name', metavar='<name>')
@click.argument('resource_name', metavar='<resource>')
def attach(affordance_name, resource_name):
    """
    Creates a route to previously created affordance for a resource, and wires the affordance's
    route into the _links of the resource.
    """
    try:
        eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    # TODO: SLAP!
    # TODO: Use LinkAdder pattern
    # TODO: refactor affordance/folder parse
    folder = None
    if '.' in affordance_name:
        # ASSERT: folder was not specified (else warn? abort?)
        # ASSERT: only one dot in affordance_name
        folder, affordance_name = affordance_name.split('.')
    affordance = f'affordances.{folder + "." if folder else ""}{affordance_name}'
    attaching = f'Attaching {affordance} to {resource_name}'
    if folder == 'root':
        folder = None
    affordance_filename = f'affordances{"/"+folder if folder else ""}/{affordance_name}.py'
    if not os.path.exists(affordance_filename):
        return eve_utils.escape(f'{affordance} does not exist', 1002)
    click.echo(attaching)

    singular, plural = eve_utils.get_singular_plural(resource_name)
    route = ROUTE_TEMPLATE.format(affordance_name=affordance_name, plural=plural, singular=singular)
    handler = HANDLER_TEMPLATE.format(affordance_name=affordance_name, singular=singular)

    with open(affordance_filename, 'r') as f:
        lines = f.readlines()

    with open(affordance_filename, 'w') as f:
        for line in lines:
            f.write(line)
            if line.startswith('def add_affordance('):
                f.write(route)
                f.write('\n')
        f.write('\n\n')
        f.write(handler)

    _add_affordance_resource(affordance_name, folder, resource_name)


def _write_affordance_file(affordance_name, resource_name):
    singular, plural = eve_utils.get_singular_plural(resource_name)
    bracketed_id = f'{{{singular}_id}}'
    route = ROUTE_TEMPLATE.format(affordance_name=affordance_name, plural=plural, singular=singular)
    handler = HANDLER_TEMPLATE.format(affordance_name=affordance_name, singular=singular)
    with open(f'{affordance_name}.py', 'w') as file:
        file.write(f'''"""
This module defines functions to add the {affordance_name} affordance.
"""
import logging
from utils import make_error_response, unauthorized_message, get_resource_id, get_id_field

LOG = logging.getLogger("affordances.{affordance_name}")


def add_affordance(app):
{route}

def add_link({singular}):
    base_url = SETTINGS.get('ES_BASE_URL', '')
    {singular}_id = get_resource_id('{plural}', {singular})

    {singular}['_links']['{affordance_name}'] = {{
        'href': f'/{plural}/{bracketed_id}/{affordance_name}',
        'title': 'PUT to do {affordance_name}'    
    }}


{handler}''')


def _add_affordance_resource(affordance_name, folder, resource):
    singular, plural = eve_utils.get_singular_plural(resource)
    AffordanceInserter(affordance_name, folder, singular, plural).transform(f'hooks/{plural}.py')
