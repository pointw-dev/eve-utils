import itertools
from libcst import *
import eve_utils


class DomainDefinitionInserter(CSTTransformer):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    def leave_Module(self, original_node, updated_node):
        """ Adds the following to the top of domain/__init__.py:
               from . import resource
        """
        addition = SimpleStatementLine(
            body=[
                ImportFrom(
                    module=None,
                    names=[
                        ImportAlias(
                            name=Name(f'{self.resource}')
                        ),
                    ],
                    relative=[
                        Dot(),
                    ],
                    whitespace_after_from=SimpleWhitespace(' '),
                    whitespace_before_import=SimpleWhitespace(' '),
                    whitespace_after_import=SimpleWhitespace(' ')
                )
            ],
            trailing_whitespace=eve_utils.code_gen.TWNL
        )

        new_body = eve_utils.code_gen.insert_import(updated_node.body, addition)

        return updated_node.with_changes(
            body=new_body
        )

    def visit_SimpleStatementLine(self, node):
        if not isinstance(node.body[0], Assign):
            return False

        if not node.body[0].targets[0].target.value == 'DOMAIN_DEFINITIONS':
            return False

        return True

    def leave_Dict(self, original_node, updated_node):
        """ Adds the following to domain/__init_.py's DOMAIN_DEFINITIONS:
            'resource': resource.DEFINITION,
        """

        key = SimpleString(f"'{self.resource}'")
        value = Attribute(
            value=Name(f'{self.resource}'),
            dot=Dot(),
            attr=Name('DEFINITION')
        )

        comma = Comma(
            whitespace_before=SimpleWhitespace(
                value='',
            ),
            whitespace_after=ParenthesizedWhitespace(
                first_line=eve_utils.code_gen.TWNL,
                indent=True,
                last_line=SimpleWhitespace('    ')
            )
        )

        addition = DictElement(key, value)

        new_elements = []
        last_element = updated_node.elements[-1].with_changes(comma=comma)

        for item in itertools.chain(updated_node.elements[0:-1], [last_element, addition]):
            new_elements.append(item)

        return updated_node.with_changes(
            elements=new_elements
        )
