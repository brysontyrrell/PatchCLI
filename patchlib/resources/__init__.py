from ConfigParser import ConfigParser
import json
import os

from jsonschema import validate, ValidationError

from patchlib.api import CommunityPatch, PatchServer
from patchlib.exc import InvalidPatchDefinitionError, PatchProfileError

__all__ = ['validate_patch', 'PatchApiProfile']

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


class PatchApiProfile(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)
        self.file_path = os.path.join(
            os.path.expanduser('~'), '.patchcli_profiles')

        self.load()

    def load(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as f_obj:
                self.readfp(f_obj)

    def save(self):
        with open(self.file_path, 'w') as f_obj:
            self.write(f_obj)

    def add_profile(self, name, api_token, patch_server=None,
                    community_patch=False, community_patch_beta=False,
                    overwrite=False):
        if name in self.sections() and overwrite:
            self.remove_section(name)
        elif name in self.sections() and not overwrite:
            raise PatchProfileError('Profile Exists')

        self.add_section(name)
        self.set(name, 'patch_server', patch_server or '')
        self.set(name, 'community_patch', community_patch)
        self.set(name, 'community_patch_beta', community_patch_beta)
        self.set(name, 'api_token', api_token)

    def get_profile(self, profile_name):
        profile = dict()
        profile['patch_server'] = self.get(profile_name, 'patch_server')
        profile['community_patch'] = \
            self.getboolean(profile_name, 'community_patch')
        profile['community_patch_beta'] = \
            self.getboolean(profile_name, 'community_patch_beta')
        profile['api_token'] = self.get(profile_name, 'api_token')

        return profile

    def get_api_client(self, profile_name):
        profile = self.get_profile(profile_name)

        if profile.get('patch_server'):
            return PatchServer(profile['patch_server'], profile['api_token'])

        elif profile.get('community_patch'):
            return CommunityPatch(profile['api_token'])

        elif profile.get('community_patch_beta'):
            return CommunityPatch(profile['api_token'], beta=True)
