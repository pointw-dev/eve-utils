"""
Defines custom validations used in domain.
"""
import re
import logging

from eve.utils import config
from eve.io.mongo import Validator
from flask import current_app as app
from bson.objectid import ObjectId

from log_trace.decorators import trace

LOG = logging.getLogger('validator')


# TODO: alias app.data.driver.db


class EveValidator(Validator):
    """Validator for custom types and validations."""
    @trace
    def _validate_unique_ignorecase(self, unique, field, value):
        """ Validates that a field value is unique.
            NOTE: this method was copy/pasted from Eve io/mongo/validation, then made
                  case insensitive

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        query = {}
        if unique:
            query = {
                field: re.compile('^' + re.escape(value) + '$', re.IGNORECASE)
            }

            resource_config = config.DOMAIN[self.resource]

            # exclude soft deleted documents if applicable
            if resource_config["soft_delete"]:
                # be aware that, should a previously (soft) deleted document be
                # restored, and because we explicitly ignore soft deleted
                # documents while validating 'unique' fields, there is a chance
                # that a unique field value will end up being now duplicated
                # in two documents: the restored one, and the one which has
                # been stored with the same field value while the original
                # document was in 'deleted' state.

                # we make sure to also include documents which are missing the
                # DELETED field. This happens when soft deletes are enabled on
                # an a resource with existing documents.
                query[config.DELETED] = {"$ne": True}

            # exclude current document
            if self.document_id:
                id_field = resource_config["id_field"]
                query[id_field] = {"$ne": self.document_id}

            # we perform the check on the native mongo driver (and not on
            # app.data.find_one()) because in this case we don't want the usual
            # (for eve) query injection to interfere with this validation. We
            # are still operating within eve's mongo namespace anyway.

            datasource, _, _, _ = app.data.datasource(self.resource)
            if app.data.driver.db[datasource].find_one(query):
                self._error(field, "value '%s' is not unique (case-insensitive)" % value)

    @trace
    def _validate_unique_to_parent(self, unique_to_parent, field, value):
        """
        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        if not unique_to_parent:
            return

        resource = self.resource
        rel = resource.split('_')
        if len(rel) > 1:
            resource = rel[1]

        parent_ref_field = f'_{unique_to_parent}_ref'  # TODO: must be singular for now - fix this

        # TODO: assert(parent_ref_field in self.schema.schema)
        # TODO: assert('data_relation' in self.schema.schema[parent_ref_field])
        parent_resource = self.schema.schema[parent_ref_field]['data_relation'].get('resource')
        # TODO: assert(parent_resource)
        parent_ref = self.document.get(parent_ref_field)

        collection = app.data.driver.db[resource]
        query = {
            field: re.compile('^' + re.escape(value) + '$', re.IGNORECASE)
        }
        if parent_ref:
            query[parent_ref_field] = ObjectId(parent_ref)
        else:
            query[parent_ref_field] = None

        prior = collection.find_one(query)
        if prior and unique_to_parent:
            prior_name = prior.get('name')
            message = f'/{parent_resource}/{parent_ref}/{resource} already has an item whose {field} is {prior_name}'
            if not parent_ref:
                message = f'/{resource} already has an item whose {field} is {prior_name}'
            self._error(field, message)
