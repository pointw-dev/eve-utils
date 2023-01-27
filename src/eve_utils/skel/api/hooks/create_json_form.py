import json
from log_trace.decorators import trace
from domain import DOMAIN

def generate_json_form(schema):
    """
    This function generated JSON Form of resource's schema
    """
    ui_schema_element_list = []
    type_mapping = {"float": "number", "int": "number", "list": "array", "objectid": "string"}
    for key in schema:
        property_dict = dict()
        property_dict["type"] = type_mapping.get(schema[key]["type"], schema[key]["type"])
        schema[key] = property_dict
        ui_schema_element_list.append({"type": "Control", "scope": f"#/properties/{key}"})
    json_schema = {
        "type": "object",
        "properties": {**schema},
    }
    ui_schema = {"type": "VerticalLayout", "elements": ui_schema_element_list}
    return json_schema, ui_schema


@trace
def add_hooks(app):
    app.on_post_GET_create_json_form += post_get_callback_item


@trace
def post_get_callback_item(request, payload):
    schema_name = request.path.split("/")[2]
    if schema_name not in DOMAIN:
        payload.status_code = 204
    else:
        to_convert = DOMAIN[schema_name]["schema"].copy()
        fields_to_remove = ["_x", "_tags", "_tenant"]
        for field in fields_to_remove:
            to_convert.pop(field, None)
        json_schema, ui_schema = generate_json_form(to_convert)
        payload.data = json.dumps({"json_schema": json_schema, "ui_schema": ui_schema})
