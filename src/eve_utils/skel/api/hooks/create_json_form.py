import json
from log_trace.decorators import trace
from domain import DOMAIN
from utils import get_type_mapping_dict, add_validations

def remove_unnecessary_keys(resource_obj):
    fields_to_remove = ["_x", "_tags", "_tenant"]
    for field in fields_to_remove:
        resource_obj.pop(field, None)
    return resource_obj


def generate_json_form(schema):
    """
    This function generated JSON Form of resource's schema
    """
    ui_schema_element_list = []
    required_fields = []
    type_mapping = get_type_mapping_dict()
    for key in schema:
        property_dict = dict()
        if "required" in schema[key] and schema[key]["required"]:
            required_fields.append(key)
        add_validations(property_dict, schema[key])
        property_dict["type"] = type_mapping.get(
            schema[key]["type"], schema[key]["type"]
        )
        if property_dict["type"] is "object" and "schema" in schema[key]:
            json_schema, ui_schema = generate_json_form(schema[key]["schema"])
            property_dict["properties"] = json_schema["properties"]
        schema[key] = property_dict
        ui_schema_element_list.append(
            {"type": "Control", "scope": f"#/properties/{key}"}
        )
    json_schema = {
        "type": "object",
        "required": required_fields,
        "properties": {**schema},
    }
    ui_schema = {"type": "VerticalLayout", "elements": ui_schema_element_list}

    return json_schema, ui_schema


@trace
def add_hooks(app):
    app.on_post_GET_create_json_form += post_get_callback


@trace
def post_get_callback(request, payload):
    schema_name = request.path.split("/")[2]
    if schema_name not in DOMAIN:
        payload.status_code = 204
        return

    cerberus_schema = DOMAIN[schema_name]["schema"].copy()
    remove_unnecessary_keys(cerberus_schema)
    json_schema, ui_schema = generate_json_form(cerberus_schema)
    payload.data = json.dumps({"json_schema": json_schema, "ui_schema": ui_schema})
