#!/usr/bin/env python
"""Adds authorization module to the API project.

Usage:
    add_auth

Examples:
    add_auth

License:
    MIT License

    Copyright (c) 2021 Michael Ottoson

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import os
import argparse
import itertools
from libcst import *
import importlib

from commands import utils
import eve_utils

# TODO: script getting default values (e.g. client keys)
# TODO: provide non Auth0

class EveServiceInserter(CSTTransformer):
    def __init__(self):
        pass

    def leave_Module(self, original_node, updated_node):
        addition = SimpleStatementLine(
            body=[
                ImportFrom(
                    module=Attribute(
                        value=Name(
                            value='auth',
                            lpar=[],
                            rpar=[],
                        ),
                        attr=Name(
                            value='es_auth',
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
                    names=[
                        ImportAlias(
                            name=Name(
                                value='EveServiceAuth',
                                lpar=[],
                                rpar=[],
                            ),
                            asname=None,
                            comma=MaybeSentinel.DEFAULT,
                        ),
                    ],
                    relative=[],
                    lpar=None,
                    rpar=None,
                    semicolon=MaybeSentinel.DEFAULT,
                    whitespace_after_from=SimpleWhitespace(
                        value=' ',
                    ),
                    whitespace_before_import=SimpleWhitespace(
                        value=' ',
                    ),
                    whitespace_after_import=SimpleWhitespace(
                        value=' ',
                    ),
                ),
            ])

        new_body = eve_utils.insert_import(updated_node.body, addition)

        return updated_node.with_changes(
            body = new_body
        )

    def visit_SimpleStatementLine(self, node):
        if not isinstance(node.body[0], Assign):
            return False
            
        target = node.body[0].targets[0].target
        
        if not isinstance(target, Attribute):
            return False
            
        if not (target.value.value == 'self' and target.attr.value == '_app'):
            return False
            
        return True
        
    def leave_Assign(self, original_node, updated_node):
        addition = Arg(
            value=Name(
                value='EveServiceAuth',
                lpar=[],
                rpar=[],
            ),
            keyword=Name(
                value='auth',
                lpar=[],
                rpar=[],
            ),
            equal=AssignEqual(
                whitespace_before=SimpleWhitespace(
                    value='',
                ),
                whitespace_after=SimpleWhitespace(
                    value='',
                ),
            ),
            comma=MaybeSentinel.DEFAULT,
            star='',
            whitespace_after_star=SimpleWhitespace(
                value='',
            ),
            whitespace_after_arg=SimpleWhitespace(
                value='',
            ),
        )
        
        comma = Comma(
            whitespace_before=SimpleWhitespace(
                value='',
            ),
            whitespace_after=SimpleWhitespace(
                value=' ',
            ),
        )       

        new_args = []
        last_arg = updated_node.value.args[-1].with_changes(comma=comma)

        for item in itertools.chain(updated_node.value.args[0:-1], [last_arg, addition]):
            new_args.append(item)

        new_value = updated_node.value.with_changes(args=new_args)

        return updated_node.with_changes(
            value = new_value
        )


def wire_up_service():
    with open('eve_service.py', 'r') as source:
        tree = parse_module(source.read())
    
    inserter = EveServiceInserter()
    new_tree = tree.visit(inserter)
    
    with open('eve_service.py', 'w') as source:
        source.write(new_tree.code)


def add():
    try:
        settings = utils.jump_to_api_folder('src/{project_name}')
    except RuntimeError:
        print('This command must be run in an eve_service API folder structure')
        return

    eve_utils.copy_skel(settings['project_name'], 'auth')
    eve_utils.install_packages(['eve-negotiable-auth', 'PyJWT', 'cryptography', 'requests'], 'add_auth')
    # eve_negotiable_auth also installs authparser and pyparsing    
    # cryptography also installs cffi, pycparser
    # requests also installs certifi, chardet, idna, urllib3
    
    wire_up_service()
    
    print('auth modules added')
