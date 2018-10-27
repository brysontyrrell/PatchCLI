import argparse
import json
import os

from patchlib import __version__
from patchlib.exc import InvalidPatchDefinitionError
from patchlib.patch import make_definition
from patchlib.resources import validate_patch


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

    subparsers = parser.add_subparsers(
        title='Commands'
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


def main():
    args = arguments()
    args.func(args)
    raise SystemExit(0)
