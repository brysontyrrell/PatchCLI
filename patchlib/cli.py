import argparse
from getpass import getpass
import json
import os

from patchlib import __version__
from patchlib.exc import InvalidPatchDefinitionError, PatchProfileError
from patchlib.patch import make_definition
from patchlib.resources import validate_patch, PatchApiProfile

try:
    # Python 2 and 3 compatibility
    input = raw_input
except NameError:
    pass


class CommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


def arguments():
    parser = argparse.ArgumentParser(
        prog='patchcli',
        description='PatchCLI is a command line tool for Jamf Pro patch '
                    'definition management.',
        formatter_class=CommandHelpFormatter
    )
    parser._optionals.title = 'Global Options'

    parser.add_argument(
        '-v', '--version',
        help='Display version information.',
        action='version',
        version='PatchCLI {}'.format(__version__)
    )
    parser.add_argument(
        '-P', '--profile',
        help='The Patch API profile name to use.'
    )

    subparsers = parser.add_subparsers(
        title='Commands'
    )

    patch_parser = subparsers.add_parser(
        'patch',
        help='Create a new definition JSON file'
    )
    patch_parser.set_defaults(func=patch)

    patch_parser.add_argument(
        'path',
        help='Path to the application',
    )
    patch_parser.add_argument(
        '-o', '--output',
        help='Directory path to write JSON file',
        metavar='<output_dir>'
    )
    patch_parser.add_argument(
        '-p', '--publisher',
        help='Provide publisher name for a full definition',
        default='',
        metavar='<publisher_name>'
    )
    patch_parser.add_argument(
        '-n', '--name',
        help='Provide the display name for a full definition',
        default='',
        metavar='<name>'
    )
    patch_parser.add_argument(
        '-e', '--extension-attribute',
        help='Path to a script to include as an extension attribute\n* You can '
             'include multiple extension attribute arguments',
        action='append',
        metavar='<ext_att_path>'
    )
    patch_parser.add_argument(
        '--app-version',
        help='Provide the version of the app (override '
             'CFBundleShortVersionString)',
        default='',
        metavar='<version>'
    )
    patch_parser.add_argument(
        '--min-sys-version',
        help='Provide the minimum supported version fo macOS for this app '
             '(e.g. 10.9)',
        default='',
        metavar='<version>'
    )
    patch_parser.add_argument(
        '--patch-only', help='Only create a patch, not a full definition',
        action='store_true'
    )

    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate an existing definition JSON file.'
    )
    validate_parser.set_defaults(func=validate)

    validate_parser.add_argument(
        'path',
        help='Path to the definition JSON file.',
        type=argparse.FileType('r')
    )
    validate_parser.add_argument(
        '-p', '--patch',
        help='Validate a patch, not a full definition.',
        action='store_true'
    )

    api_parser = subparsers.add_parser(
        'api',
        help='Perform quick interactions with the Patch APIs.',
        formatter_class=CommandHelpFormatter
    )
    # api_parser.set_defaults(func=cli_api)

    api_commands_parser = api_parser.add_subparsers(
        title='API Commands'
    )
    api_command_list_titles = api_commands_parser.add_parser(
        'list_titles',
        help='List available software titles'
    )
    api_command_list_titles.set_defaults(func=cli_api, command='list_titles')

    api_command_get_title = api_commands_parser.add_parser(
        'get_title',
        help='Get a software title definition'
    )
    api_command_get_title.set_defaults(func=cli_api, command='get_title')
    api_command_get_title.add_argument(
        'title',
        help='The ID of the software title to retrieve'
    )

    create_profile_parser = subparsers.add_parser(
        'create_profile',
        help='Create a profile to use the Patch API integrations.'
    )
    create_profile_parser.set_defaults(func=create_profile)

    create_profile_parser.add_argument(
        '-n', '--name',
        help='Profile name',
        default='',
        metavar='<profile_name>'
    )
    create_profile_parser.add_argument(
        '-t', '--token',
        help='The API token',
        default='',
        metavar='<api_token>'
    )

    profile_server = \
        create_profile_parser.add_mutually_exclusive_group(required=True)
    profile_server.add_argument(
        '--ps', '--patch-server',
        help='The URL to a local Patch Server instance',
        metavar='<patch_server_url>'
    )
    profile_server.add_argument(
        '--cp', '--community-patch',
        help='Use the Community Patch service',
        action='store_true'
    )
    profile_server.add_argument(
        '--cpb', '--community-patch-beta',
        help='Use the Beta Community Patch service',
        action='store_true'
    )

    create_profile_parser.add_argument(
        '--overwrite',
        help='Overwrite an existing profile of the same name.',
        action='store_true'
    )

    return parser.parse_args()


def patch(args):
    app_id, output = make_definition(args)

    if args.output:
        if args.patch_only:
            filename = '{}-patch.json'.format(app_id)
        else:
            filename = '{}.json'.format(app_id)
        with open(os.path.join(args.output, filename), 'w') as f:
            json.dump(output, f)
    else:
        print(json.dumps(output, indent=4))


def validate(args):
    with args.path as f_obj:
        data = json.load(f_obj)

    schema = 'version' if args.patch else 'patch'

    try:
        validate_patch(data, schema)
    except InvalidPatchDefinitionError as err:
        print(err.message)
    else:
        print('Validation passed!')


def cli_api(args):
    if not args.profile:
        print("You must provide a Patch profile for API integrations.\n"
              "To create a Patch profile, use the 'create_profile' command.")
        raise SystemExit(1)

    patch_profile = PatchApiProfile()
    client = patch_profile.get_api_client(args.profile)

    if args.command == 'list_titles':
        return client.list_titles()

    elif args.command == 'get_title':
        return client.get_title(args.title)


def create_profile(args):
    if not args.name:
        args.name = input('Profile Name: ')

    if not args.token:
        args.token = getpass('API Token: ')

    patch_config = PatchApiProfile()

    try:
        patch_config.add_profile(
            args.name, args.token, args.ps, args.cp, args.cpb, args.overwrite)
    except PatchProfileError:
        print("The profile '{}' already exists: "
              "use '--overwrite' option to update".format(args.name))
        raise SystemExit(1)

    patch_config.save()
    print("Saved profile '{}' to {}".format(args.name, patch_config.file_path))


def main():
    args = arguments()
    args.func(args)
    raise SystemExit(0)
