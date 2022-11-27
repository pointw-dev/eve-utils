import os
import json
import click
from distutils.dir_util import copy_tree, remove_tree
import importlib
from shutil import copyfile
from . import utils
import addins

import eve_utils

class CommandWithOptionalFlagValues(click.Command):
    def parse_args(self, ctx, args):        
        """ Translate any flag `--opt=value` as flag `--opt` with changed flag_value=value """
        # filter flags
        flags = [o for o in self.params if isinstance(o, click.Option) and o.is_flag and not isinstance(o.flag_value, bool)]
        prefixes = {p: o for o in flags for p in o.opts if p.startswith('--')}
        for i, flag in enumerate(args):
            flag = flag.split('=')
            if flag[0] in prefixes and len(flag) > 1:
                prefixes[flag[0]].flag_value = flag[1]
                args[i] = flag[0]

        return super(CommandWithOptionalFlagValues, self).parse_args(ctx, args)


def _create_api(project_name):
    # TODO: ensure folder is empty? or at least warn if not?
    if project_name == '.':
        project_name = os.path.basename(os.getcwd())

    click.echo(f'Creating {project_name} api')
    settings = {
        'project_name': project_name
    }
    with open('.eve-utils', 'w') as f:
        json.dump(settings, f, indent=4)
        
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

    os.mkdir(project_name)
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
    
    
def _add_addins(add_git, add_docker):
    if add_git:
        addins.git.add(add_git)
        
    if add_docker:
        addins.docker.add()


@click.group(name='api')
def commands():
    pass


@commands.command(cls=CommandWithOptionalFlagValues, name='create', short_help="<name> or '.' to use the current folder's name")
@click.argument('project_name', metavar='<name>')
@click.option('--add_git', '-g', is_flag=True, help='initiaialize local git repository (with optional remote)', flag_value='no remote', metavar='[remote]')
@click.option('--add_docker', '-d', is_flag=True, help='add Dockerfile and supporting files to deploy the API as a container', flag_value='n/a')
def create(project_name, add_git, add_docker):
    """<name> or "." to use the current folder's name"""
    _create_api(project_name)
    _add_addins(add_git, add_docker)


@commands.command(cls=CommandWithOptionalFlagValues, short_help="short help")
@click.option('--add_git', '-g', is_flag=True, help='initiaialize local git repository (with optional remote)', flag_value='no remote', metavar='[remote]')
@click.option('--add_docker', '-d', is_flag=True, help='add Dockerfile and supporting files to deploy the API as a container')
def addin(add_git, add_docker):
    _add_addins(add_git, add_docker)
