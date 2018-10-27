import json
import os

from jsonschema import validate, ValidationError

from patchlib.exc import InvalidPatchDefinitionError

__all__ = ['validate_patch']

dir_path = os.path.dirname(os.path.realpath(__file__))


def _load_json(name):
    with open(os.path.join(dir_path, name), 'r') as f_obj:
        return json.load(f_obj)


patch_schema = _load_json('schema_full_definition.json')
version_schema = _load_json('schema_version.json')


def validate_patch(data, schema=None):
    """Takes a dictionary object and validates it against a JSON schema.

    :param dict data: The JSON to validate as a dictionary object.
    :param str schema: Which schema to validate against. Valid options are:
        patch or version.

    :raises: InvalidPatchDefinitionError
    """
    if schema not in ('patch', 'version'):
        raise ValueError("Argument 'schema' must be 'patch' or 'version'")

    if schema == 'patch':
        use_schema = patch_schema
    else:
        use_schema = version_schema

    try:
        validate(data, use_schema)
    except ValidationError as error:
        message = "Validation error encountered with submitted JSON: {} for " \
                  "item: /{}".format(
                      str(error.message),
                      '/'.join([str(i) for i in error.path]))
        raise InvalidPatchDefinitionError(message)
