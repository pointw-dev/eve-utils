import json
import sys
import click
from .link_adder import LinkAdder, LinkAdderException
import eve_utils


@click.group(name='link', help='Manage parent/child links amongst resources.')
def commands():
    pass


@commands.command(name='create', help='Create a parent/child link between two resources.')
@click.argument('parent', metavar='<parent>')
@click.argument('child', metavar='<child>')
@click.option('--as_parent_ref', '-p', is_flag=True, help='change name of related ref to "parent" (instead of the name of the parent)')
def create(parent, child, as_parent_ref):
    try:
        settings = eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        print('This command must be run in an eve_service API folder structure')
        sys.exit(1)

    adder = LinkAdder(parent, child, as_parent_ref)

    try:
        adder.execute()
    except LinkAdderException as err:
        print(err)
        sys.exit(err.exit_code)


# TODO: refactor/SLAP
@commands.command(name='list', help='List the relationships amongst the resources.')
@click.option('--plant_uml', '-p', is_flag=True, help='output the rels in PlantUML class notation')
def list(plant_uml):
    try:
        settings = eve_utils.jump_to_api_folder('src/{project_name}/domain')
    except RuntimeError:
        print('This command must be run in an eve_service API folder structure')
        sys.exit(1)

    rels = eve_utils.parent_child_relations()

    if plant_uml:
        print('@startuml')
        print('hide <<resource>> circle')
        print('hide <<remote>> circle')
        print('hide members ')
        print()
        print('skinparam class {')
        print('    BackgroundColor<<remote>> LightBlue')
        print('}')
        print()
        for rel in rels:
            print(f'class {rel} <<resource>>')
            for item in rels[rel]:
                for member in rels[rel][item]:
                    if member.startswith('remote:'):
                        target = member.split(':')[1]
                        print(f'class {target} <<remote>>')
        print()
        for rel in rels:
            for item in rels[rel].get('children', []):
                if item.startswith('remote:'):
                    item = item.split(':')[1]
                print(f'{rel} ||--o{{ {item}')
            for item in rels[rel].get('parents', []):
                if item.startswith('remote:'):
                    item = item.split(':')[1]
                    print(f'{item} ||--o{{ {rel}')
        print('@enduml')
    else:
        for rel in rels:
            print(rel)
            for item in rels[rel].get('parents', []):
                print(f'- belong to a {item}')
            for item in rels[rel].get('children', []):
                print(f'- have {item}')

        print()
        print(json.dumps(rels, indent=4, default=str))


@commands.command(name='remove', help='(not yet implemented)')
def remove():
    click.echo('remove')
