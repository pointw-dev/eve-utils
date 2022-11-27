import os
import click
from distutils.dir_util import copy_tree, remove_tree
import importlib
from shutil import copyfile
from . import utils

import eve_utils

@click.group(name='api')
def commands():
    pass


@commands.command(name='create')
@click.argument('project_name', metavar='<name>') # , help=f'The name of the API [default: {os.path.basename(os.getcwd())}]')
# @click.option('--name', help=f'The name of the API [default: {os.path.basename(os.getcwd())}]')
# @click.option('--name', help='The name of the API', show_default=True, default=os.path.basename(os.getcwd()))
def create(project_name):
    """<name> or "." to use the current folder's name"""
    if project_name == '.':
        project_name = os.path.basename(os.getcwd())

    click.echo(f'Creating {project_name} api')
    with open('.eve-utils', 'w') as f:
        f.write(f'# eve-utils configuration\nproject_name: {project_name}\n')
        
    skel = os.path.join(os.path.dirname(eve_utils.__file__), 'skel')
    readme_filename = os.path.join(skel, 'doc/README.md')
    copyfile(readme_filename, './README.md')   
    os.mkdir('doc')
    readme_filename = os.path.join(skel, 'doc/Setup-Dev-Environment.md')
    copyfile(readme_filename, './doc/Setup-Dev-Environment.md')   
        
    os.mkdir('src')
    os.chdir('src')
    os.mkdir('scripts')
    scripts_folder = os.path.join(skel, 'scripts')
    copy_tree(scripts_folder, 'scripts')
    
    api_folder = os.path.join(skel, 'api')

    os.mkdir(project_name)  # TODO: ensure doesn't already exist, etc
    copy_tree(api_folder, project_name)

    # TODO: can the following remove_tree calls be obviated if skel is packaged differently?
    utils.remove_if_exists(os.path.join(project_name, '__pycache__'))
    utils.remove_if_exists(os.path.join(project_name, 'configuration', '__pycache__'))
    utils.remove_if_exists(os.path.join(project_name, 'domain', '__pycache__'))
    utils.remove_if_exists(os.path.join(project_name, 'hooks', '__pycache__'))
    utils.remove_if_exists(os.path.join(project_name, 'log_trace', '__pycache__'))
    utils.remove_if_exists(os.path.join(project_name, 'utils', '__pycache__'))

    os.chdir('..')
    utils.replace_project_name(project_name, '.')


@commands.command()
def add():
    click.echo('API ADD')
