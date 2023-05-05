from libcst import *
import eve_utils


class ValidationInserter(CSTTransformer):
    def __init__(self):
        super().__init__()

    def leave_Module(self, original_node, updated_node):
        """ Adds to the top of eve_service.py the following:
                from validation.validator import EveValidator
        """
        addition = SimpleStatementLine(
            body=[
                ImportFrom(
                    module=Attribute(
                        value=Name('validation'),
                        dot=Dot(),
                        attr=Name('validator')
                    ),
                    names=[
                        ImportAlias(
                            name=Name('EveValidator')
                        ),
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
                validator=EveValidator
        """

        addition = Arg(
            value=Name('EveValidator'),
            equal=AssignEqual(),
            keyword=Name('validator')
        )

        new_value = eve_utils.get_new_param_list(addition, updated_node)

        return updated_node.with_changes(
            value=new_value
        )
