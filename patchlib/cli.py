import argparse
import json
import os

from patchlib.patch import make_definition


def arguments():
    parser = argparse.ArgumentParser(
        prog='patchcli',
        description='PatchCLI is a command line tool for Jamf Pro patch '
                    'definition management.'
    )
    parser.add_argument(
        'path',
        help='Path to the application',
        type=str
    )
    parser.add_argument(
        '-o', '--output',
        help='Directory path to write JSON file',
        type=str,
        metavar='<output_dir>'
    )
    parser.add_argument(
        '-p', '--publisher',
        help='Provide publisher name for a full definition',
        type=str,
        default='',
        metavar='<publisher_name>'
    )
    parser.add_argument(
        '-n', '--name',
        help='Provide the display name for a full definition',
        type=str,
        default='',
        metavar='<name>'
    )
    parser.add_argument(
        '-e', '--extension-attribute',
        help='Path to a script to include as an extension attribute\n* You can '
             'include multiple extension attribute arguments',
        action='append',
        metavar='<ext_att_path>'
    )
    parser.add_argument(
        '--app-version',
        help='Provide the version of the app (override '
             'CFBundleShortVersionString)',
        type=str,
        default='',
        metavar='<version>'
    )
    parser.add_argument(
        '--min-sys-version',
        help='Provide the minimum supported version fo macOS for this app '
             '(e.g. 10.9)',
        type=str,
        default='',
        metavar='<version>'
    )
    parser.add_argument(
        '--patch-only', help='Only create a patch, not a full definition',
        action='store_true'
    )

    return parser.parse_args()


def main():
    args = arguments()
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
