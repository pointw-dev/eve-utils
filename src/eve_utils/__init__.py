import os
import sys
import subprocess
import inflect
import json
import glob
from distutils.dir_util import copy_tree, remove_tree

from . import addins
from . import commands
from . import code_gen


def jump_to_api_folder(path=None):
    keep_going = True
    while keep_going:
        if os.path.isfile('.eve-utils'):
            keep_going = False
            break

        current_dir = os.getcwd()
        if os.path.isdir('..'):
            os.chdir('..')
            if os.getcwd() == current_dir:
                raise RuntimeError('Not in an eve_service API folder')            
        else:
            raise RuntimeError('Not in an eve_service API folder')

    with open('.eve-utils', 'r') as f:
        settings = json.load(f)

    if path:
        project_name = settings['project_name']
        path = eval("f'" + f'{path}' + "'")
        os.chdir(path)
    
    return settings


def add_to_settings(key, value):
    try:
        settings = jump_to_api_folder()
    except RuntimeError:
        return escape('This command must be run in an eve_service API folder structure', 1)

    settings[key] = value

    with open('.eve-utils', 'w') as f:
        to_write = json.dumps(settings) + '\n'
        f.write(to_write)


def install_packages(packages, command):
    trigger = 'Successfully installed '
    subprocess.check_output([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    with open('requirements.txt', 'a') as f:
        f.write(f'\n# start: added by {command}\n')
        for package in packages:
            subprocess.check_output([sys.executable, "-m", "pip", "install", package]).decode('utf-8')
            out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode('utf-8')
            for line in out.split('\n'):
                if package in line:
                    f.write(f'{line}\n')

        f.write(f'# end: added by {command}\n')


def copy_skel(project_name, skel_folder, target_folder=None, replace=None, silent=False):
    if not silent: print(f'Adding {skel_folder} to {project_name} API')

    source = os.path.join(os.path.dirname(__file__), f'skel/{skel_folder}')
    destination = skel_folder if not target_folder else target_folder

    if not target_folder:
        if not os.path.isdir(skel_folder):
            os.mkdir(skel_folder)  # TODO: ensure doesn't already exist, etc
    copy_tree(source, destination)

    # TODO: can the following remove_tree calls be obviated if skel is packaged differently?
    remove_folder_if_exists(os.path.join(destination, '__pycache__'))
    
    if replace is None:
        replace = {}
    replace['project_name'] = project_name
    
    for item in replace:
        for dname, dirs, files in os.walk(destination):
            for fname in files:
                fpath = os.path.join(dname, fname)
                if fname.endswith('.pyc') or fname.endswith('.ico'):
                    continue
                with open(fpath, 'r') as f:
                    try:
                        s = f.read()
                    except UnicodeDecodeError as ex:
                        continue
                changed = False
                if f'{{${item}}}' in s:
                    s = s.replace(f'{{${item}}}', replace[item])
                    changed = True
                if changed:
                    with open(fpath, 'w') as f:
                        f.write(s)


# TODO: refactor with similar functionality in copy_skel()
def replace_project_name(project_name, folder=None):
    if not folder:
        folder = f'./{project_name}'
    for dname, dirs, files in os.walk(folder):
        for fname in files:
            # do not process if traversing nested venv folder
            if os.path.abspath(dname).startswith(sys.prefix):
              continue
            if '__pycache__' in dname:
              continue
            if '.idea' in dname:
              continue
            fpath = os.path.join(dname, fname)
            try:
              with open(fpath) as f:
                  s = f.read()
              s = s.replace("{$project_name}", project_name)
              with open(fpath, "w") as f:
                  f.write(s)
            except UnicodeDecodeError as ex:
              print(f'Skipping unprocessable file: {dname}/{fname}')


def remove_file_if_exists(filename):
    if os.path.exists(filename):
        os.remove(filename)


def remove_folder_if_exists(folder):
    if os.path.exists(folder):
        remove_tree(folder)


def escape(message, code, silent=False):
    if silent:
        return code
    print(message)
    sys.exit(code)


def urljoin(*parts):
    trailing_slash = '/' if parts[-1].endswith('/') else ''
    return "/".join([str(part).strip("/") for part in parts]) + trailing_slash


def get_singular_plural(word):
    if ',' in word:
        # ASSERT word.count(',') == 1
        a = word.split(',')
        return a[0], a[1]

    p = inflect.engine()

    singular = word if not p.singular_noun(word) else p.singular_noun(word)
    plural = word if p.singular_noun(word) else p.plural_noun(word)

    if singular == plural:  # in case of words like moose, fish
        plural = plural + 's'

    return singular, plural
