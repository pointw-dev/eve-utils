import itertools
from libcst import *
# from eve_utils.code_gen import insert_import
import eve_utils


class AuthorizationInserter(CSTTransformer):
    def __init__(self):
        super().__init__()

    def leave_Module(self, original_node, updated_node):
        """ Adds to the top of eve_service.py the following:
                from auth.es_auth import EveAuthorization
        """

        addition = SimpleStatementLine(
            body=[
                ImportFrom(
                    module=Attribute(
                        value=Name('auth'),
                        dot=Dot(),
                        attr=Name('es_auth')
                    ),
                    names=[
                        ImportAlias(
                            name=Name('EveAuthorization')
                        )
                    ],
                    whitespace_after_from=SimpleWhitespace(' '),
                    whitespace_before_import=SimpleWhitespace(' '),
                    whitespace_after_import=SimpleWhitespace(' ')
                )
            ])

        new_body = eve_utils.code_gen.insert_import(updated_node.body, addition)

        return updated_node.with_changes(
            body=new_body
        )

    def visit_SimpleStatementLine(self, node):
        return eve_utils.is_app_assignment(node)

    def leave_Assign(self, original_node, updated_node):
        """ Adds the following kwarg to eve_service.py:EveService:__init__() self._app = Eve(...) assignment:
                auth=EveAuthorization
        """

        addition = Arg(
            value=Name('EveAuthorization'),
            equal=AssignEqual(),
            keyword=Name('auth')
        )
        
        new_value = eve_utils.get_new_param_list(addition, updated_node)

        return updated_node.with_changes(
            value=new_value
        )
