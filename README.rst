PatchCLI
========

A command line tool for generating Jamf Pro patch definitions, patch updates,
and built-in integration to Patch Server and CommunityPatch APIs.

**WARNING:** This tool is under active development and the CLI interface and
features will be changing frequently between updates.

Install
-------

PatchCLI can be installed from the Python Package Index:

::

    $ pip install patchlib

The ``patchlib`` module contains the ``patchcli`` command.

About
-----

Basic Usage
-----------

::

    $ patchcli -h
    usage: patchcli [-h] [-v] {validate,patch} ...

    PatchCLI is a command line tool for Jamf Pro patch definition management.

    Global Options:
      -h, --help        show this help message and exit
      -v, --version     Display version information.

    Commands:
        validate        Validate an existing definition JSON file.
        patch           Create a new definition JSON file

Patch Command
^^^^^^^^^^^^^

::

    $ patchcli patch -h
    usage: patchcli patch [-h] [-o <output_dir>] [-p <publisher_name>] [-n <name>]
                          [-e <ext_att_path>] [--app-version <version>]
                          [--min-sys-version <version>] [--patch-only]
                          path

    positional arguments:
      path                  Path to the application

    optional arguments:
      -h, --help            show this help message and exit
      -o <output_dir>, --output <output_dir>
                            Directory path to write JSON file
      -p <publisher_name>, --publisher <publisher_name>
                            Provide publisher name for a full definition
      -n <name>, --name <name>
                            Provide the display name for a full definition
      -e <ext_att_path>, --extension-attribute <ext_att_path>
                            Path to a script to include as an extension attribute
                            * You can include multiple extension attribute
                            arguments
      --app-version <version>
                            Provide the version of the app (override
                            CFBundleShortVersionString)
      --min-sys-version <version>
                            Provide the minimum supported version fo macOS for
                            this app (e.g. 10.9)
      --patch-only          Only create a patch, not a full definition

Validate Command
^^^^^^^^^^^^^^^^

::

    $ patchcli validate -h
    usage: patchcli validate [-h] [-p] path

    positional arguments:
      path         Path to the definition JSON file.

    optional arguments:
      -h, --help   show this help message and exit
      -p, --patch  Validate a patch, not a full definition.

Server Configs
--------------

PatchLib
========

Import and use the API clients for Patch Server and CommunityPatch.


History
=======

Versions
--------

0.2.2 (2018-10-29)
^^^^^^^^^^^^^^^^^^

Fix ``setup.py`` issues preventing installation via ``pip``.

0.2.1 (2018-10-29)
^^^^^^^^^^^^^^^^^^

Readme typos.

0.2.0 (2018-10-27)
^^^^^^^^^^^^^^^^^^

Updated CLI interface to use sub-commands. All previous functionality of the
``patchstarter.py`` script has been moved into the ``patch`` command.

Added a ``validate`` command that allows a user to perform a schema validation
on manually created/edited definition files prior to uploading to a patch
server.

0.1.0 (2018-10-25)
^^^^^^^^^^^^^^^^^^

Repository setup. Port existing patchstarter.py functionality as-is.
