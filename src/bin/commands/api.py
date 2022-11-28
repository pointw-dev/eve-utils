import os
import json
import functools
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
    
    
def _add_addins(kwargs):
    for keyword in [kw for kw in kwargs.keys() if kwargs[kw]]:
        addin = keyword[4:]  # remove "add_"
        if addin == 'git':
            continue
        print(f'===== adding {addin}')
        addin_module = importlib.import_module(f'addins.{addin}')
        add = getattr(addin_module, 'add')
        if kwargs[keyword] == 'n/a':
            add()
        else:
            add(kwargs[keyword])
        
    if kwargs['add_git']:
        print(f'===== adding git')    
        addins.git.add(kwargs['add_git'])


def addin_params(func):
    @click.option('--add_git', '-g', is_flag=True, help='initiaialize local git repository (with optional remote)', flag_value='no remote', metavar='[remote]')
    @click.option('--add_docker', '-d', is_flag=True, help='add Dockerfile and supporting files to deploy the API as a container', flag_value='n/a')
    @click.option('--add_auth', '-a', is_flag=True, help='add authorization class and supporting files', flag_value='n/a')
    @click.option('--add_validation', '-v', is_flag=True, help='add custom validation class that you can extend', flag_value='n/a')
    @click.option('--add_web_socket', '-w', is_flag=True, help='add web socket and supporting files', flag_value='n/a')
    @click.option('--add_serverless', '-s', is_flag=True, help='add serverless framework and supporting files', flag_value='n/a')
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@click.group(name='api')
def commands():
    pass


@commands.command(cls=CommandWithOptionalFlagValues, name='create', short_help="<name> or '.' to use the current folder's name")
@click.argument('project_name', metavar='<name>')
@addin_params
def create(**kwargs):
    """<name> or "." to use the current folder's name"""
    _create_api(kwargs['project_name'])
    del kwargs['project_name']
    _add_addins(kwargs)


@commands.command(cls=CommandWithOptionalFlagValues, short_help="Add an addin to an already created API")
@addin_params
def addin(**kwargs):
    """Add an addin to an already created API"""
    _add_addins(kwargs)