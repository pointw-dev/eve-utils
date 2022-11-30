import os
import click
from commands import utils

@click.command(name='run', help='Launch the service.')
def commands():
    try:
        utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        print('This command must be run in an eve_service API folder structure')
        return
    
    os.system('python run.py')
