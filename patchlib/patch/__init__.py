import base64
from datetime import datetime
import json
import os
import plistlib
import subprocess
import xml

try:
    # Python 2 and 3 compatibility
    input = raw_input
except NameError:
    pass


def read_binary_plist(plist_path):
    process = subprocess.Popen(
        ['plutil', '-convert', 'json', '-o', '-', plist_path],
        stdout=subprocess.PIPE
    )
    response = process.communicate()
    try:
        return json.loads(response[0])
    except ValueError:
        print('ERROR: Unable to read the application plist!')
        raise SystemExit(1)


def make_definition(args):
    app_filename = os.path.basename(args.path.rstrip('/'))
    info_plist_path = os.path.join(args.path, 'Contents', 'Info.plist')

    try:
        info_plist = plistlib.readPlist(info_plist_path)
    except EnvironmentError as err:
        print('ERROR: {}'.format(err))
        raise SystemExit(1)
    except xml.parsers.expat.ExpatError:
        info_plist = read_binary_plist(info_plist_path)

    if args.name:
        app_name = args.name
    else:
        try:
            app_name = info_plist['CFBundleName']
        except KeyError:
            app_name = str(app_filename.split('.app')[0])

    app_id = app_name.replace(' ', '')
    app_bundle_id = info_plist['CFBundleIdentifier']

    if args.app_version:
        app_version = args.app_version
    else:
        try:
            app_version = info_plist['CFBundleShortVersionString']
        except KeyError:
            print("Could not find 'CFBundleShortVersionString', please provide "
                  "a value for the application version")
            app_version = input("[]: ") or None
            if not app_version:
                print('ERROR: The application version is required')
                raise SystemExit(1)

    if args.min_sys_version:
        app_min_os = args.min_sys_version
    else:
        try:
            app_min_os = info_plist['LSMinimumSystemVersion']
        except KeyError:
            print("Could not find 'LSMinimumSystemVersion', please provide a "
                  "value for the minimum OS version")
            app_min_os = input("[10.9]: ") or '10.9'

    app_last_modified = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    app_timestamp = datetime.utcfromtimestamp(
        os.path.getmtime(args.path)).strftime('%Y-%m-%dT%H:%M:%SZ')

    patch = {
        "version": app_version,
        "releaseDate": app_timestamp,
        "standalone": True,
        "minimumOperatingSystem": app_min_os,
        "reboot": False,
        "killApps": [
            {
                "bundleId": app_bundle_id,
                "appName": app_filename
            }
        ],
        "components": [
            {
                "name": app_name,
                "version": app_version,
                "criteria": [
                    {
                        "name": "Application Bundle ID",
                        "operator": "is",
                        "value": app_bundle_id,
                        "type": "recon",
                        "and": True
                    },
                    {
                        "name": "Application Version",
                        "operator": "is",
                        "value": app_version,
                        "type": "recon"
                    }
                ]
            }
        ],
        "capabilities": [
            {
                "name": "Operating System Version",
                "operator": "greater than or equal",
                "value": app_min_os,
                "type": "recon"
            }
        ],
        "dependencies": []
    }

    if args.patch_only:
        return app_id, patch

    patch_def = {
        "id": app_id,
        "name": app_name,
        "publisher": args.publisher or app_name,
        "appName": app_filename,
        "bundleId": app_bundle_id,
        "lastModified": app_last_modified,
        "currentVersion": app_version,
        "requirements": [
            {
                "name": "Application Bundle ID",
                "operator": "is",
                "value": app_bundle_id,
                "type": "recon",
                "and": True
            }
        ],
        "patches": [],
        "extensionAttributes": []
    }

    patch_def['patches'].append(patch)

    if args.extension_attribute:
        for ext_att in args.extension_attribute:
            try:
                with open(ext_att, 'rb') as f:
                    ext_att_content = base64.b64encode(f.read())
            except IOError as err:
                print('ERROR: {}'.format(err))
                raise SystemExit(1)
            else:
                patch_def['extensionAttributes'].append(
                    {
                        "key": app_name.lower().replace(' ', '-'),
                        "value": ext_att_content.decode('ascii'),
                        "displayName": app_name
                    }
                )

    return app_id, patch_def
