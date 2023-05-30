from libcst import *
from .file_transformer import FileTransformer
import eve_utils


class ParentLinksRemover(FileTransformer):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    def leave_Assign(self, original_node, updated_node):
        target = original_node.targets[0].target
        if not isinstance(target, Subscript) or target.slice[0].slice.value.value[1:-1] != self.resource:
            return original_node

        return RemoveFromParent()

# TODO: is anyone using this???