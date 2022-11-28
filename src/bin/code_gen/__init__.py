from libcst import *
from .domain_definition_inserter import DomainDefinitionInserter
from .hooks_inserter import HooksInserter
from .authorization_inserter import AuthorizationInserter
from .validation_inserter import ValidationInserter
from .child_links_inserter import ChildLinksInserter
from .parent_links_inserter import ParentLinksInserter
from .domain_children_definition_inserter import DomainChildrenDefinitionInserter
from .domain_relations_inserter import DomainRelationsInserter

def get_comma():
    return Comma(
        whitespace_before=SimpleWhitespace(
            value='',
        ),
        whitespace_after=ParenthesizedWhitespace(
            first_line=TrailingWhitespace(
                whitespace=SimpleWhitespace(
                    value='',
                ),
                comment=None,
                newline=Newline(
                    value=None,
                ),
            ),
            empty_lines=[],
            indent=True,
            last_line=SimpleWhitespace(
                value='    ',
            ),
        ),
    )
