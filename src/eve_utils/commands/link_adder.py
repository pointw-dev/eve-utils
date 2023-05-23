import os
from libcst import parse_module

from eve_utils.code_gen import \
    ChildLinksInserter, \
    ParentLinksInserter, \
    DomainChildrenDefinitionInserter, \
    DomainRelationsInserter

import eve_utils


class LinkAdder:
    def __init__(self, parent, child, as_parent_ref):
        self.remote_parent = self.remote_child = False

        if parent.startswith(eve_utils.REMOTE_PREFIX):
            parent = parent[len(eve_utils.REMOTE_PREFIX):]
            self.remote_parent = True

        if child.startswith(eve_utils.REMOTE_PREFIX):
            child = child[len(eve_utils.REMOTE_PREFIX):]
            self.remote_child = True

        self.parent, self.parents = eve_utils.get_singular_plural(parent)  # TODO: validate, safe name, etc.
        self.child, self.children = eve_utils.get_singular_plural(child)  # TODO: validate, safe name, etc.
        self.parent_ref = '_parent_ref' if as_parent_ref else f'_{parent}_ref'

    def _add_links_to_child_hooks(self):
        with open(f'hooks/{self.children}.py', 'r') as source:
            tree = parse_module(source.read())

        inserter = ChildLinksInserter(self)
        new_tree = tree.visit(inserter)

        with open(f'hooks/{self.children}.py', 'w') as source:
            source.write(new_tree.code)

    def _add_links_to_parent_hooks(self):
        with open(f'hooks/{self.parents}.py', 'r') as source:
            tree = parse_module(source.read())

        inserter = ParentLinksInserter(self)
        new_tree = tree.visit(inserter)

        with open(f'hooks/{self.parents}.py', 'w') as source:
            source.write(new_tree.code)

    def _add_to_domain_init(self):
        with open('domain/__init__.py', 'r') as source:
            tree = parse_module(source.read())

        inserter = DomainRelationsInserter(self)
        new_tree = tree.visit(inserter)

        with open('domain/__init__.py', 'w') as source:
            source.write(new_tree.code)

    def _add_to_domain_child(self):
        with open(f'domain/{self.children}.py', 'r') as source:
            tree = parse_module(source.read())

        inserter = DomainChildrenDefinitionInserter(self)
        new_tree = tree.visit(inserter)

        with open(f'domain/{self.children}.py', 'w') as source:
            source.write(new_tree.code)

    def _link_already_exists(self):
        rels = eve_utils.parent_child_relations()

        if 'children' in rels.get(self.parents, {}):
            needle = eve_utils.REMOTE_PREFIX + self.children if self.remote_child else self.children
            if needle in rels[self.parents]['children']:
                return True  # i.e. link does exist

        if self.remote_parent and 'parents' in rels.get(self.children, {}):
            needle = eve_utils.REMOTE_PREFIX + self.parent
            if needle in rels[self.children]['parents']:
                return True

        return False  # i.e. link does not exist

    def _list_missing_resources(self):
        try:
            eve_utils.jump_to_api_folder('src/{project_name}/domain')
        except RuntimeError:
            return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

        rtn = ''
        if not self.remote_parent and not os.path.exists(f'./{self.parents}.py'):
            rtn += self.parents

        if not self.remote_child and not os.path.exists(f'./{self.children}.py'):
            if rtn:
                rtn += ', '

            rtn += self.children

        return rtn

    def _validate(self):
        if self._link_already_exists():
            raise LinkAdderException(801, 'This link already exists')

        missing = self._list_missing_resources()
        if missing:
            raise LinkAdderException(802, f'missing local resource: {missing}')

        if self.remote_parent and self.remote_child:
            raise LinkAdderException(803, 'Both parent and child cannot be remote')

    def execute(self):
        try:
            eve_utils.jump_to_api_folder('src/{project_name}')
        except RuntimeError:
            return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

        self._validate()
        print(
            f'Creating link rel from {"remote " if self.remote_parent else ""}{self.parent} (parent) '
            f'to {"remote " if self.remote_child else ""}{self.children} (children)'
        )

        if self.remote_parent:
            eve_utils.commands.api._add_addins({'add_validation': 'n/a'}, silent=True)

        eve_utils.jump_to_api_folder('src/{project_name}')
        # update parent code
        if not self.remote_parent:
            self._add_links_to_parent_hooks()

        # update child code
        if not self.remote_child:
            self._add_to_domain_init()
            self._add_to_domain_child()
            self._add_links_to_child_hooks()


class LinkAdderException(Exception):
    def __init__(self, exit_code, message):
        super().__init__(message)
        self.exit_code = exit_code


