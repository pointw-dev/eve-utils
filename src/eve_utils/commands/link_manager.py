import os
import glob
from eve_utils.code_gen import \
    ChildLinksInserter, \
    ParentLinksInserter, \
    DomainChildrenDefinitionInserter, \
    DomainRelationsInserter, \
    ChildLinksRemover, \
    ParentReferenceRemover, \
    DomainRelationsRemover
import eve_utils


class LinkManager:

    REMOTE_PREFIX = 'remote:'

    def __init__(self, parent, child, as_parent_ref=False):
        self.remote_parent = self.remote_child = False

        if parent.startswith(LinkManager.REMOTE_PREFIX):
            parent = parent[len(LinkManager.REMOTE_PREFIX):]
            self.remote_parent = True

        if child.startswith(LinkManager.REMOTE_PREFIX):
            child = child[len(LinkManager.REMOTE_PREFIX):]
            self.remote_child = True

        self.parent, self.parents = eve_utils.get_singular_plural(parent)  # TODO: validate, safe name, etc.
        self.child, self.children = eve_utils.get_singular_plural(child)  # TODO: validate, safe name, etc.
        self.parent_ref = '_parent_ref' if as_parent_ref else f'_{parent}_ref'

    def _link_already_exists(self):
        rels = LinkManager.get_relations()

        if 'children' in rels.get(self.parents, {}):
            needle = LinkManager.REMOTE_PREFIX + self.children if self.remote_child else self.children
            if needle in rels[self.parents]['children']:
                return True  # i.e. link does exist

        if self.remote_parent and 'parents' in rels.get(self.children, {}):
            needle = LinkManager.REMOTE_PREFIX + self.parent
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
            raise LinkManagerException(801, 'This link already exists')

        missing = self._list_missing_resources()
        if missing:
            raise LinkManagerException(802, f'missing local resource: {missing}')

        if self.remote_parent and self.remote_child:
            raise LinkManagerException(803, 'Both parent and child cannot be remote')

    @staticmethod
    def get_relations():
        try:
            settings = eve_utils.jump_to_api_folder('src/{project_name}/domain')
        except RuntimeError:
            return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

        with open('__init__.py', 'r') as f:
            lines = f.readlines()

        listening = False
        rels = {}
        for line in lines:
            if 'DOMAIN_RELATIONS' in line:
                listening = True
                continue

            if not listening:
                continue

            if line.startswith('}'):
                break

            if line.startswith("    '"):
                rel_name = line.split("'")[1]
                continue

            if line.startswith("        'url':"):
                if not line.split('/')[1].startswith('<'):
                    listening = False
                    continue

            if line.startswith("        'resource_title':"):
                child = line.split("'")[3]
                parent = rel_name.replace(f"_{child}", "")
                parent, parents = eve_utils.get_singular_plural(parent)
                child, children = eve_utils.get_singular_plural(child)

                if parents not in rels:
                    rels[parents] = {}
                if 'children' not in rels[parents]:
                    rels[parents]['children'] = set()
                rels[parents]['children'].add(children)

                if children not in rels:
                    rels[children] = {}
                if 'parents' not in rels[children]:
                    rels[children]['parents'] = set()
                rels[children]['parents'].add(parent)

        LinkManager._add_remote_relations(rels)

        return rels

    @staticmethod
    def _add_remote_relations(rels):
        try:
            settings = eve_utils.jump_to_api_folder('src/{project_name}/hooks')
        except RuntimeError:
            return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

        files = [file for file in glob.glob('*.py') if not file.startswith('_')]

        for file in files:
            resource = file.split('.')[0]  # TODO: replace with more elegant basename or something
            with open(file, 'r') as f:
                lines = f.readlines()

            my_relationship = ''
            its_relationship = ''
            for line in lines:
                if line.startswith('def _add_remote_'):
                    my_relationship = line.split('_')[3]
                    if my_relationship == 'parent':
                        my_relationship = 'parents'
                    its_relationship = 'children' if my_relationship == 'parents' else 'parents'
                    continue
                elif line.startswith('def '):
                    my_relationship = ''
                    continue

                if my_relationship and '_links' in line:
                    remote = line.split("'")[3]
                    singular, plural = eve_utils.get_singular_plural(remote)
                    remote = 'remote:' + (singular if my_relationship == 'parents' else plural)
                    remotes = 'remote:' + plural
                    singular, plural = eve_utils.get_singular_plural(resource)
                    if resource not in rels:
                        rels[resource] = {}
                    if my_relationship not in rels[resource]:
                        rels[resource][my_relationship] = set()
                    rels[resource][my_relationship].add(remote)

                    if remotes not in rels:
                        rels[remotes] = {}
                    if resource not in rels[remotes]:
                        rels[remotes][its_relationship] = set()
                    rels[remotes][its_relationship].add(singular if its_relationship == 'parents' else plural)

    def add(self):
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
            ParentLinksInserter(self).transform(f'hooks/{self.parents}.py', )

        # update child code
        if not self.remote_child:
            DomainRelationsInserter(self).transform('domain/__init__.py', )
            DomainChildrenDefinitionInserter(self).transform(f'domain/{self.children}.py')
            ChildLinksInserter(self).transform(f'hooks/{self.children}.py')

    def remove(self):
        try:
            eve_utils.jump_to_api_folder('src/{project_name}')
        except RuntimeError:
            return eve_utils.escape('This command must be run in an eve_service API folder structure', 1)

        if not self._link_already_exists():
            raise LinkManagerException(804, f'There is no link from {self.parent} to {self.children}')

        print(f'Removing link from {self.parent} to {self.children}')

        eve_utils.jump_to_api_folder('src/{project_name}')
        DomainRelationsRemover(self.parents, self.children).transform('domain/__init__.py')
        if not self.remote_parent:
            ChildLinksRemover(self.children).transform(f'hooks/{self.parents}.py')

        # update child code
        if not self.remote_child:
            ParentReferenceRemover(self.parents).transform(f'domain/{self.children}.py')
            ChildLinksRemover(self.parents).transform(f'hooks/{self.children}.py')


class LinkManagerException(Exception):
    def __init__(self, exit_code, message):
        super().__init__(message)
        self.exit_code = exit_code


