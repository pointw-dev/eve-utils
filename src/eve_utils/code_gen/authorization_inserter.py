from libcst import *
from .file_transformer import FileTransformer
import eve_utils


class AuthorizationInserter(FileTransformer):
    def __init__(self):
        super().__init__()

    def leave_Module(self, original_node, updated_node):
        """ Adds to the top of eve_service.py the following:
                from auth.authorization import EveServiceAuthorization
        """

        addition = SimpleStatementLine(
            body=[
                ImportFrom(
                    module=Attribute(
                        value=Name('auth'),
                        dot=Dot(),
                        attr=Name('authorization')
                    ),
                    names=[
                        ImportAlias(
                            name=Name('EveServiceAuthorization')
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
        return eve_utils.code_gen.is_app_assignment(node)

    def leave_Assign(self, original_node, updated_node):
        """ Adds the following kwarg to eve_service.py:EveService:__init__() self._app = Eve(...) assignment:
                auth=EveServiceAuthorization
        """

        addition = Arg(
            value=Name('EveServiceAuthorization'),
            equal=AssignEqual(
                whitespace_before=SimpleWhitespace(''),
                whitespace_after=SimpleWhitespace('')
            ),
            keyword=Name('auth')
        )
        
        new_value = eve_utils.code_gen.get_new_param_list(addition, updated_node)

        return updated_node.with_changes(
            value=new_value
        )
