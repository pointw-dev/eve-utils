import os
import click
import importlib
from libcst import parse_module
from .singplu import get_pair
from code_gen import ChildLinksInserter, ParentLinksInserter, DomainChildrenDefinitionInserter, DomainRelationsInserter
from commands import utils


def _add_links_to_child_hooks(parent, child, parents, children, parent_ref):
    with open(f'hooks/{children}.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = ChildLinksInserter(parent, child, parents, children, parent_ref)
    new_tree = tree.visit(inserter)

    with open(f'hooks/{children}.py', 'w') as source:
        source.write(new_tree.code)


def _add_links_to_parent_hooks(parent, child, parents, children, parent_ref):
    with open(f'hooks/{parents}.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = ParentLinksInserter(parent, child, parents, children, parent_ref)
    new_tree = tree.visit(inserter)

    with open(f'hooks/{parents}.py', 'w') as source:
        source.write(new_tree.code)


def _add_to_domain_init(parent, child, parents, children, parent_ref):
    with open('domain/__init__.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = DomainRelationsInserter(parent, child, parents, children, parent_ref)
    new_tree = tree.visit(inserter)

    with open('domain/__init__.py', 'w') as source:
        source.write(new_tree.code)


def _add_to_domain_child(parent, child, parents, children, parent_ref):
    with open(f'domain/{children}.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = DomainChildrenDefinitionInserter(parent, child, parents, children, parent_ref)
    new_tree = tree.visit(inserter)

    with open(f'domain/{children}.py', 'w') as source:
        source.write(new_tree.code)


@click.group(name='rel')
def commands():
    pass


@commands.command(name='create')
@click.argument('parent', metavar='<parent>')
@click.argument('child', metavar='<child>')
@click.option('--as_parent_ref', '-p', is_flag=True, help='change name of related ref to "parent" (instead of the name of the parent)')
def create(parent, child, as_parent_ref):
    try:
        settings = utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        print('This command must be run in an eve_service API folder structure')
        return
        
    parent, parents = singular, plural = get_pair(parent)  # TODO: validate, safe name, etc.
    child, children = singular, plural = get_pair(child)  # TODO: validate, safe name, etc.
    parent_ref = '_parent_ref' if as_parent_ref else f'_{parent}_ref'

    print(f'Creating link rel from {parent} (parent) to {child} (child)')

    _add_to_domain_init(parent, child, parents, children, parent_ref)
    _add_to_domain_child(parent, child, parents, children, parent_ref)
    _add_links_to_parent_hooks(parent, child, parents, children, parent_ref)
    _add_links_to_child_hooks(parent, child, parents, children, parent_ref)


@commands.command(name='list', help='list the relationships amongst the resources')
@click.option('--plant_uml', '-p', is_flag=True, help='output the rels in PlantUML class notation')
def list(plant_uml):    
    try:
        settings = utils.jump_to_api_folder('src/{project_name}/domain')
    except RuntimeError:
        print('This command must be run in an eve_service API folder structure')
        return
        
    with open('__init__.py', 'r') as f:
        lines = f.readlines()
        
    listening = False
    rels = {}
    for line in lines:
        if 'DOMAIN_RELATIONS' in line:
            listening = True
            continue
            
        if not listening:
            continue
            
        if line.startswith('}'):
            break
            
        if line.startswith("    '"):
            rel_name = line.split("'")[1]
            parent, child = rel_name.split('_')
            parent, parents = get_pair(parent)
            child, children = get_pair(child)
            
            if parents not in rels:
                rels[parents] = {}
            if 'children' not in rels[parents]:
                rels[parents]['children'] = set()
            rels[parents]['children'].add(children)
            
            if children not in rels:
                rels[children] = {}
            if 'parents' not in rels[children]:
                rels[children]['parents'] = set()
            rels[children]['parents'].add(parent)    
        
    if plant_uml:
        print('@startuml')
        print('hide <<resource>> circle')
        print('hide members')
        print()
        for rel in rels:
            print(f'class {rel} <<resource>>')
        print()
        for rel in rels:
            for item in rels[rel].get('children', []):
                print(f'{rel} ||--o{{ {item}')
        print('@enduml')
    else:
        for rel in rels:
            print(rel)
            for item in rels[rel].get('parents', []):
                print(f'- belong to a {item}')
            for item in rels[rel].get('children', []):
                print(f'- have {item}')

@commands.command(name='remove')
def remove():
    click.echo('remove')
