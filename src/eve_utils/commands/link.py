import json
import sys
import click
from .command_help_order import CommandHelpOrder
from .link_adder import LinkAdder, LinkAdderException
from eve_utils.code_gen import ChildLinksRemover, ParentReferenceRemover, DomainRelationsRemover
import eve_utils


@click.group(name='link',
             help='Manage parent/child links amongst resources.',
             cls=CommandHelpOrder)
def commands():
    pass


@commands.command(name='create',
                  short_help='Create a parent/child link between two resources.  If one of the resources is in the '
                       'domain of a different EveService, add "remote:" in front of the name of that resource.',
                  help_priority=1)
@click.argument('parent', metavar='<parent|remote:parent>')
@click.argument('child', metavar='<child|remote:child>')
@click.option('--as_parent_ref', '-p',
              is_flag=True,
              help='Change name of related ref to "parent" (instead of the name of the parent).')
def create(parent, child, as_parent_ref):
    try:
        settings = eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    adder = LinkAdder(parent, child, as_parent_ref)

    try:
        adder.execute()
    except LinkAdderException as err:
        print(err)
        sys.exit(err.exit_code)


# TODO: refactor/SLAP
@commands.command(name='list',
                  short_help='List the relationships amongst the resources.',
                  help_priority=2)
@click.option('output', '--format', '-f',
              type=click.Choice(['english', 'json', 'python_dict', 'plant_uml']),
              default='english',
              help='Choose the output format of the relationships list')
def list_rels(output):
    try:
        settings = eve_utils.jump_to_api_folder('src/{project_name}/domain')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    rels = eve_utils.parent_child_relations()

    if output == 'english':
        for rel in rels:
            print(rel)
            for item in rels[rel].get('parents', []):
                print(f'- belong to a {item}')
            for item in rels[rel].get('children', []):
                print(f'- have {item}')
    elif output == 'json':
        print(json.dumps(rels, indent=4, default=list))
    elif output == 'python_dict':
        print(rels)
    elif output == 'plant_uml':
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
                    if member.startswith(eve_utils.REMOTE_PREFIX):
                        target = member[len(eve_utils.REMOTE_PREFIX):]
                        print(f'class {target} <<remote>>')
        print()
        for rel in rels:
            for item in rels[rel].get('children', []):
                if item.startswith(eve_utils.REMOTE_PREFIX):
                    item = item[len(eve_utils.REMOTE_PREFIX):]
                print(f'{rel} ||--o{{ {item}')
            for item in rels[rel].get('parents', []):
                if item.startswith(eve_utils.REMOTE_PREFIX):
                    item = item[len(eve_utils.REMOTE_PREFIX):]
                    print(f'{item} ||--o{{ {rel}')
        print('@enduml')


@commands.command(name='remove',
                  short_help='(not yet implemented)',
                  help_priority=3)
@click.argument('parent', metavar='<parent|remote:parent>')
@click.argument('child', metavar='<child|remote:child>')
def remove(parent, child):
    try:
        eve_utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

    parent, parents = eve_utils.get_singular_plural(parent)
    child, children = eve_utils.get_singular_plural(child)
    adder = LinkAdder(parent, child)
    if not adder.link_already_exists():
        eve_utils.escape(f'There is no link from {parent} to {children}', 804)
    click.echo(f'Removing link from {parent} to {children}')
    # if _is_resource_name_is_invalid(singular, plural):
    #     return eve_utils.escape(f'The resource name ({resource_name}) is invalid', 701)

    eve_utils.jump_to_api_folder('src/{project_name}')
    DomainRelationsRemover(parents, children).transform('domain/__init__.py')
    ParentReferenceRemover(parents).transform(f'domain/{children}.py')
    ChildLinksRemover(parents).transform(f'hooks/{children}.py')
    ChildLinksRemover(children).transform(f'hooks/{parents}.py')
