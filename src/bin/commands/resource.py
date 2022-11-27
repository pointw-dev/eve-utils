import os
import click
import itertools
from libcst import *
from singplu import get_pair
from .code_gen import DomainDefinitionInserter
from . import utils


class HooksInserter(CSTTransformer):
    def __init__(self, resource):
        self.resource = resource

    def leave_Module(self, original_node, updated_node):
        addition = SimpleStatementLine(
            body=[
                Import(
                    names=[ImportAlias(name=Attribute(value=Name(value='hooks'), attr=Name(value=f'{self.resource}')))],
                    semicolon=MaybeSentinel.DEFAULT,
                    whitespace_after_import=SimpleWhitespace(
                        value=' ',
                    ),
                ),
            ],
            leading_lines=[],
            trailing_whitespace=TrailingWhitespace(
                whitespace=SimpleWhitespace(
                    value='',
                ),
                comment=None,
                newline=Newline(
                    value=None,
                ),
            ),
        )

        new_body = utils.insert_import(updated_node.body, addition)

        return updated_node.with_changes(
            body = new_body
        )

    def leave_FunctionDef(self, original_node, updated_node):
        if not original_node.name.value == 'add_hooks':
            return original_node

        addition = SimpleStatementLine(
            body=[
                Expr(
                    value=Call(
                        func=Attribute(
                            value=Attribute(
                                value=Name(
                                    value='hooks',
                                    lpar=[],
                                    rpar=[],
                                ),
                                attr=Name(
                                    value=f'{self.resource}',
                                    lpar=[],
                                    rpar=[],
                                ),
                                dot=Dot(
                                    whitespace_before=SimpleWhitespace(
                                        value='',
                                    ),
                                    whitespace_after=SimpleWhitespace(
                                        value='',
                                    ),
                                ),
                                lpar=[],
                                rpar=[],
                            ),
                            attr=Name(
                                value='add_hooks',
                                lpar=[],
                                rpar=[],
                            ),
                            dot=Dot(
                                whitespace_before=SimpleWhitespace(
                                    value='',
                                ),
                                whitespace_after=SimpleWhitespace(
                                    value='',
                                ),
                            ),
                            lpar=[],
                            rpar=[],
                        ),
                        args=[
                            Arg(
                                value=Name(
                                    value='app',
                                    lpar=[],
                                    rpar=[],
                                ),
                                keyword=None,
                                equal=MaybeSentinel.DEFAULT,
                                comma=MaybeSentinel.DEFAULT,
                                star='',
                                whitespace_after_star=SimpleWhitespace(
                                    value='',
                                ),
                                whitespace_after_arg=SimpleWhitespace(
                                    value='',
                                ),
                            ),
                        ],
                        lpar=[],
                        rpar=[],
                        whitespace_after_func=SimpleWhitespace(
                            value='',
                        ),
                        whitespace_before_args=SimpleWhitespace(
                            value='',
                        ),
                    ),
                    semicolon=MaybeSentinel.DEFAULT,
                ),
            ],
            leading_lines=[],
            trailing_whitespace=TrailingWhitespace(
                whitespace=SimpleWhitespace(
                    value='',
                ),
                comment=None,
                newline=Newline(
                    value=None,
                ),
            ),
        )

        new_body = []
        for item in itertools.chain(updated_node.body.body, [addition]):  # TODO: if addition is first, prepend with newline
            new_body.append(item)

        return updated_node.with_changes(
            body=updated_node.body.with_changes(
                body=new_body
            )
        )




def create_resource_domain_file(resource, add_common):
    with open(f'domain/{resource}.py', 'w') as file:
        file.write(f'''"""
Defines the {resource} resource.
"""
''')

        if add_common:
            file.write('from domain.common import COMMON_FIELDS\n\n\n')

        file.write('''SCHEMA = {
    'name': {
        'type': 'string',
        'required': True,
        'empty': False,
        'unique': True
    },
    'description': {
        'type': 'string'
    }
}

''')

        if add_common:
            file.write('SCHEMA.update(COMMON_FIELDS)\n\n')

        file.write('''DEFINITION = {
    'schema': SCHEMA,
    'datasource': {
        'projection': {'_tenant': 0}
    },
    'additional_lookup': {
        'url': 'regex("[\w]+")',  # pylint: disable=anomalous-backslash-in-string
        'field': 'name'
    }
}
''')


def create_resource_hook_file(singular, plural):
    with open(f'hooks/{plural}.py', 'w') as file:
        file.write(f'''"""
hooks.{plural}
This module defines functions to add link relations to {plural}.
"""
import json
from log_trace.decorators import trace


@trace
def add_hooks(app):
    """Wire up the hooks for {plural}."""
    app.on_fetched_item_{plural} += _add_links_to_{singular}
    app.on_fetched_resource_{plural} += _add_links_to_{plural}_collection
    app.on_post_POST_{plural} += _post_{plural}


@trace
def _post_{plural}(request, payload):
    if payload.status_code == 201:
        j = json.loads(payload.data)
        if '_items' in j:
            for {singular} in j['_items']:
                _add_links_to_{singular}({singular})
        else:
            _add_links_to_{singular}(j)
        payload.data = json.dumps(j)


@trace
def _add_links_to_{plural}_collection({plural}_collection):
    for {singular} in {plural}_collection['_items']:
        _add_links_to_{singular}({singular})


@trace
def _add_links_to_{singular}({singular}):
    {singular}['_links']['self'] = {{
        'href': f"/{plural}/{{{singular}['_id']}}",
        'title': '{singular}'
    }}
''')


def insert_domain_definition(resource):
    with open('domain/__init__.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = DomainDefinitionInserter(resource)
    new_tree = tree.visit(inserter)

    with open('domain/__init__.py', 'w') as source:
        source.write(new_tree.code)


def insert_hooks(resource):
    with open('hooks/__init__.py', 'r') as source:
        tree = parse_module(source.read())

    inserter = HooksInserter(resource)
    new_tree = tree.visit(inserter)

    with open('hooks/__init__.py', 'w') as source:
        source.write(new_tree.code)




@click.group(name='resource')
def commands():
    pass

@commands.command(name='create')
@click.argument('resource_name', metavar='<name>')
#    parser.add_argument('-c', '--no_common', help='Do not add common fields to this resource', action='store_true', default=False)
def create(resource_name):
    """<name> of the resource to create"""
    singular, plural = get_pair(resource_name)
    add_common = True  # not args.no_common

    if os.path.exists('eve_service.py') and os.path.exists('domain'):
        print(f'Creating {plural} resource')
        create_resource_domain_file(plural, add_common)
        insert_domain_definition(plural)
        create_resource_hook_file(singular, plural)
        insert_hooks(plural)


@commands.command(name='list')
def list():
    click.echo('list')


@commands.command(name='remove')
def remove():
    click.echo('remove')
