from libcst import *
import eve_utils


class ChildLinksInserter(CSTTransformer):
    def __init__(self, adder):
        super().__init__()
        self.adder = adder

    def leave_FunctionDef(self, original_node, updated_node):
        if (not original_node.name.value == f'_add_links_to_{self.adder.child}') and (not original_node.name.value == 'add_hooks'):
            return original_node

        new_body = []
        for item in original_node.body.body:
            new_body.append(item)

        if original_node.name.value == f'_add_links_to_{self.adder.child}':
            new_body.append(self.make_parent_link())
        if original_node.name.value == 'add_hooks':
            new_body.extend(self.add_rel_hooks())

        return updated_node.with_changes(
            body=updated_node.body.with_changes(
                body=new_body
            )
        )

    def make_parent_link(self):
        """ This adds the following to hooks.children:_add_links_to_child()
                if child.get('_parent_ref'):
                    child['_links']['parent'] = {  # literally 'parent' here
                        'href': f'/parents/{child["_parent_ref"]}',
                        'title': 'parents'
                    }
                    child['_links']['collection'] = {
                        'href': f'/parents/{child["_parent_ref"]}/children',
                        'title': 'parent_children'
                    }
                else:
                    child['_links']['parent'] = {  # literally 'parent' here
                        'href': '/',
                        'title': 'home'
                    }
                    child['_links']['collection'] = {
                        'href': '/children',
                        'title': 'children'
                    }

        """

        condition = Call(
            func=Attribute(
                value=Name(f'{self.adder.child}'),
                attr=Name('get'),
                dot=Dot()
            ),
            args=[
                Arg(SimpleString(f"'{self.adder.parent_ref}'"))
            ]
        )

        if_block = IndentedBlock(
            body=[
                eve_utils.code_gen.get_link_statement_line(
                    resource=self.adder.child,
                    rel='parent',
                    href=[
                        FormattedStringText(f'/{self.adder.parents}/'),
                        FormattedStringExpression(
                            expression=Subscript(
                                value=Name(f'{self.adder.child}'),
                                slice=[
                                    SubscriptElement(
                                        slice=Index(SimpleString(f'"{self.adder.parent_ref}"'))
                                    ),
                                ],
                                lbracket=LeftSquareBracket(),
                                rbracket=RightSquareBracket()
                            ),
                        )
                    ],
                    title=self.adder.parents
                ),
                eve_utils.code_gen.get_link_statement_line(
                    resource=self.adder.child,
                    rel='collection',
                    href=[
                        FormattedStringText(f'/{self.adder.parents}/'),
                        FormattedStringExpression(
                            expression=Subscript(
                                value=Name(f'{self.adder.child}'),
                                slice=[
                                    SubscriptElement(
                                        slice=Index(SimpleString(f'"{self.adder.parent_ref}"'))
                                    ),
                                ],
                                lbracket=LeftSquareBracket(),
                                rbracket=RightSquareBracket()
                            )
                        ),
                        FormattedStringText(f'/{self.adder.children}')
                    ],
                    title=f'{self.adder.parent}_{self.adder.children}'
                )
            ],
            header=eve_utils.code_gen.TWNL
        )

        else_block = Else(
            body=IndentedBlock(
                body=[
                    eve_utils.code_gen.get_link_statement_line(
                        resource=self.adder.child,
                        rel='parent',
                        href=[FormattedStringText('/')],
                        title='home'
                    ),
                    eve_utils.code_gen.get_link_statement_line(
                        resource=self.adder.child,
                        rel='collection',
                        href=[FormattedStringText(f'/{self.adder.children}')],
                        title=self.adder.children
                    )
                ],
                header=eve_utils.code_gen.TWNL
            )
        )

        return If(
            test=condition,
            body=if_block,
            orelse=else_block,
            whitespace_before_test=SimpleWhitespace(' ')
        )

    def add_rel_hooks(self):
        # Create the first SimpleStatementLine with the on_fetched_item hook.
        on_fetched_item_line = SimpleStatementLine(
            body=[
                AugAssign(
                    target=Attribute(
                        value=Name('app'),
                        attr=Name(f'on_fetched_item_{self.adder.parents}_{self.adder.children}'),
                        dot=Dot(),
                    ),
                    operator=AddAssign(),
                    value=Name(f'_add_links_to_{self.adder.child}'),
                ),
            ],
            leading_lines=[
                # Add an empty line before the next statement.
                EmptyLine(
                    indent=False,
                    whitespace=SimpleWhitespace(''),
                    newline=Newline(),
                ),
            ],
            trailing_whitespace=TrailingWhitespace(
                whitespace=SimpleWhitespace(''),
                newline=Newline(),
            ),
        )

        # Create the second SimpleStatementLine with the on_fetched_resource hook.
        on_fetched_resource_line = SimpleStatementLine(
            body=[
                AugAssign(
                    target=Attribute(
                        value=Name('app'),
                        attr=Name(f'on_fetched_resource_{self.adder.parents}_{self.adder.children}'),
                        dot=Dot(),
                    ),
                    operator=AddAssign(),
                    value=Name(f'_add_links_to_{self.adder.children}_collection'),
                ),
            ],
            leading_lines=[],
            trailing_whitespace=TrailingWhitespace(
                whitespace=SimpleWhitespace(''),
                newline=Newline(),
            ),
        )

        # Create the third SimpleStatementLine with the on_post_POST hook.
        on_post_POST_line = SimpleStatementLine(
            body=[
                AugAssign(
                    target=Attribute(
                        value=Name('app'),
                        attr=Name(f'on_post_POST_{self.adder.parents}_{self.adder.children}'),
                        dot=Dot(),
                    ),
                    operator=AddAssign(),
                    value=Name(f'_post_{self.adder.children}'),
                ),
            ],
            leading_lines=[],
            trailing_whitespace=TrailingWhitespace(
                whitespace=SimpleWhitespace(''),
                newline=Newline(),
            ),
        )

        # Return the list of SimpleStatementLines.
        return [on_fetched_item_line, on_fetched_resource_line, on_post_POST_line]
