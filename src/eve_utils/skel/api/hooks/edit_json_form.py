import json
from datetime import date, datetime
from bson.objectid import ObjectId
from create_json_form import generate_json_form, remove_unnecessary_keys
from domain import DOMAIN
from log_trace.decorators import trace
from utils import get_db


class JSONEncoder(json.JSONEncoder):
    def default(self, obj_id):
        if isinstance(obj_id, ObjectId):
            return str(obj_id)

        if isinstance(obj_id, (datetime, date)):
            return obj_id.isoformat()
        return json.JSONEncoder.default(self, obj_id)


def get_instance(resource_name, resource_id):
    resources = eval(f"get_db().{resource_name}")
    resource = resources.find_one({"_id": ObjectId(resource_id)})
    return resource


@trace
def add_hooks(app):
    app.on_post_GET_edit_json_form += post_get_callback


@trace
def post_get_callback(request, payload):
    schema_name = request.path.split("/")[2]
    obj_id = request.path.split("/")[3]
    if schema_name not in DOMAIN:
        payload.status_code = 204
        return

    cerberus_schema = DOMAIN[schema_name]["schema"].copy()
    remove_unnecessary_keys(cerberus_schema)
    instance = get_instance(schema_name, obj_id)
    json_schema, ui_schema = generate_json_form(cerberus_schema)
    payload.data = json.dumps(
        {
            "json_schema": json_schema,
            "ui_schema": ui_schema,
            "data": json.loads(JSONEncoder().encode(instance)),
        }
    )
