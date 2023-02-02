import logging
from flask import jsonify, make_response
from flask import current_app, request
from . import log_setup

LOG = logging.getLogger("utils")

unauthorized_message = {
    "_status": "ERR",
    "_error": {"message": "Please provide proper credentials", "code": 401},
}


def get_db():
    return current_app.data.driver.db


def get_api():
    return current_app.test_client()


def make_error_response(message, code, issues=[], **kwargs):
    if "exception" in kwargs:
        ex = kwargs.get("exception")
        LOG.exception(message, ex)

        if ex:
            issues.append(
                {
                    "exception": {
                        "name": type(ex).__name__,
                        "type": ".".join([type(ex).__module__, type(ex).__name__]),
                        "args": ex.args,
                    }
                }
            )

    resp = {"_status": "ERR", "_error": {"message": message, "code": code}}

    if issues:
        resp["_issues"] = issues

    return make_response(jsonify(resp), code)


def echo_message():
    log = logging.getLogger("echo")
    message = (
        'PUT {"message": {}/"", "status_code": int}, content-type: "application/json"'
    )
    status_code = 400
    if request.is_json:
        try:
            status_code = int(request.json.get("status_code", status_code))
            message = request.json.get("message", message)
        except ValueError:
            pass

    if status_code < 400:
        log.info(message)
    elif status_code < 500:
        log.warning(message)
    else:
        log.error(message)

    return make_response(jsonify(message), status_code)


def get_type_mapping_dict():
    type_mapping = {
        "float": "number",
        "integer": "number",
        "int": "number",
        "list": "array",
        "objectid": "string",
        "dict": "object",
        "datetime": "string",
    }
    return type_mapping


def add_validations(property_dict, schema_key):
    mapping = {
        "minlength": "minLength",
        "maxlength": "maxLength",
        "allowed": "enum",
        "min": "minimum",
        "max": "maximum",
    }
    for key in mapping:
        if key in schema_key:
            property_dict[mapping[key]] = schema_key[key]
