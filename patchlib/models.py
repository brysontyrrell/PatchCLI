"""EXPERIMENTING AND NOT IN USE!!!"""
import base64
from datetime import datetime
import json
import os

from patchlib.resources import validate_patch


class Patch:
    def __init__(self, data, validate=True, server=None):
        """Object representing a Patch Definition

        :param data: Must either be the path to an existing patch definition
            JSON file that will be loaded, or a dictionary object representing
            a patch definition.
        :type data: str or dict

        :param bool validate: Perform a schema validation on the loaded patch
            definition data. Set to ``False`` to skip this validation.

        :param patchlib.api.PatchServer server:
        """
        if os.path.isfile(data):
            with open(data, 'r') as f_obj:
                self._definition = json.load(f_obj)
        elif isinstance(data, dict):
            self._definition = data
        else:
            raise ValueError("'definition' must be a file path or dictionary")

        if validate:
            self.validate()

        self._set_extension_attributes()

        self.server = server

    def _set_extension_attributes(self):
        extension_attributes = [
            ExtensionAttribute(parent=self, data=ea)
            for ea in
            self._definition.get('extensionAttributes', [])
        ]
        self._definition['extensionAttributes'] = extension_attributes

    def validate(self):
        """Run a schema validation on the patch definition."""
        validate_patch(self._definition, 'patch')

    @property
    def definition(self):
        definition = {}
        definition.update(self._definition)

        extension_attributes = [ea.data for ea in self.extension_attributes]
        self._definition['extensionAttributes'] = extension_attributes

        return definition

    @property
    def id(self):
        return self._definition.get('id')

    @property
    def name(self):
        return self._definition.get('name')

    @property
    def publisher(self):
        return self._definition.get('publisher')

    @property
    def app_name(self):
        return self._definition.get('appName')

    @property
    def bundle_id(self):
        return self._definition.get('bundleId')

    @property
    def last_modified(self):
        return datetime.strptime(
            self._definition.get('lastModifier'), '%Y-%m-%dT%H:%M:%SZ')

    @property
    def current_version(self):
        return self._definition.get('currentVersion')

    @property
    def patches(self):
        return []

    @property
    def extension_attributes(self):
        return self._definition.get('extensionAttributes')

    @property
    def requirements(self):
        return []


class Version:
    def __init__(self, parent=None):
        pass


class ExtensionAttribute:
    def __init__(self, display_name=None, key=None,
                 script=None, data=None, parent=None):
        """Object representing an Extension Attribute in a Patch Definition

        :param display_name: The display name for the extension attribute in
            Jamf Pro.
        :param key: A label representing the extension attribute within the
            Patch definition.
        :param script: Must either be the path to a script file that will be
            read and base64 encoded into the extension attribute, or a script
            already encoded as a base64 string.

        :param dict data: A dictionary object of an existing patch definition
            extension attribute. Note: if this parameter is passed,
            ``display_name``, ``key``, and ``script`` will be ignored.

        :param patchlib.models.Patch parent: A Patch object to attach this
            Extension Attribute to.
        """
        self.parent = parent
        self.data = dict()

        if data:
            self.data.update(data)
        else:
            self.data.update(
                {
                    'displayName': display_name or '',
                    'key': key or ''
                }
            )

            if script:
                if os.path.isfile(script):
                    with open(script, 'r') as f_obj:
                        value = base64.b64encode(f_obj.read())
                elif isinstance(script, str):
                    value = script
                else:
                    raise ValueError("'script' must be a base64 encoded string "
                                     "or a file path")

                self.data.update({'value': value})

    def _read_parent_version(self):
        try:
            self.parent._definition.get('version')
        except AttributeError:
            return ''

    @property
    def script(self):
        return base64.b64decode(self.data.get('value', ''))

    @property
    def criteria(self, version=None):
        """Generate the default criteria for this Extension Attribute"""
        return [
            {
                'name': self.data.get('key'),
                'operator': 'is',
                'value': version or self._read_parent_version(),
                'type': 'extensionAttribute',
                'and': True
            }
        ]

    @property
    def requirements(self):
        """Generate the default requirements for a Patch definition based on
        this Extension Attribute
        """
        return [
            {
                'name': self.data.get('key'),
                'operator': 'is not',
                'value': 'Not Installed',
                'type': 'extensionAttribute',
                'and': True
            },
            {
                'name': self.data.get('key'),
                'operator': 'is not',
                'value': '',
                'type': 'extensionAttribute',
                'and': True
            }
        ]

    def set_requirements(self):
        """Set the parent Patch object's requirements to those generated by this
        this Extension Attribute
        """
        if self.parent:
            self.parent._definition['requirements'] = self.requirements
