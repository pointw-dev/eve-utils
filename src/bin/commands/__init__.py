import click

# from . import utils
from . import api
from . import resource
from . import rel
from . import integration
from . import affordance
from . import endpoint
from . import setting

@click.group()
def main():
    pass


def initialize():        
    main.add_command(api.commands)
    main.add_command(resource.commands)
    main.add_command(rel.commands)
    main.add_command(integration.commands)
    main.add_command(affordance.commands)
    main.add_command(endpoint.commands)
    main.add_command(setting.commands)
    main()
