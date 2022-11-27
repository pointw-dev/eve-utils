import os
import sys
import subprocess
from distutils.dir_util import copy_tree, remove_tree
import eve_utils

def jump_to_api_root():
    pass
    
def insert_import(original_body, addition):
    rtn = []
    state = 'on-top'
    for item in original_body:
        if state == 'on-top':
            if hasattr(item, 'body') and hasattr(item.body, '__iter__') and type(item.body[0]).__name__ in ['Import', 'ImportFrom', 'Expr']:
                pass
            else:
                state = 'in-position'

        if state == 'in-position':
            rtn.append(addition)  # TODO: if no other appends before, add newline after here
            state = 'on-bottom'

        rtn.append(item)

    return rtn


def install_packages(packages, command):
    trigger = 'Successfully installed '
    subprocess.check_output([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    with open('requirements.txt', 'a') as f:
        f.write(f'\n# start: added by {command}\n')
        for package in packages:
            out = subprocess.check_output([sys.executable, "-m", "pip", "install", package]).decode('utf-8')
            for line in out.split('\n'):
                if line.startswith(trigger):
                    installed_packages = line[len(trigger):].split(' ')

                    for installed_package in installed_packages:
                        if package in installed_package:
                            hyphen = installed_package.rfind('-')
                            f.write(f'{installed_package[:hyphen]}=={installed_package[hyphen+1:]}\n')

        f.write(f'# end: added by {command}\n')


def copy_skel(project_name, skel_folder, target_folder=None):
    print(f'Adding {skel_folder} to {project_name} API')

    source = os.path.join(os.path.dirname(eve_utils.__file__), f'skel/{skel_folder}')
    destination = skel_folder if not target_folder else target_folder

    if not target_folder:
        os.mkdir(skel_folder)  # TODO: ensure doesn't already exist, etc
    copy_tree(source, destination)

    # TODO: can the following remove_tree calls be obviated if skel is packaged differently?
    remove_if_exists(os.path.join(destination, '__pycache__'))

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
            if '{$project_name}' in s:
                s = s.replace("{$project_name}", project_name)
                changed = True
            if changed:
                with open(fpath, "w") as f:
                    f.write(s)


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
            fpath = os.path.join(dname, fname)
            try:
              with open(fpath) as f:
                  s = f.read()
              s = s.replace("{$project_name}", project_name)
              with open(fpath, "w") as f:
                  f.write(s)
            except UnicodeDecodeError as ex:
              print(f'Skipping unprocessable file: {dname}/{fname}')



def remove_if_exists(folder):
    if os.path.exists(folder):
        remove_tree(folder)
