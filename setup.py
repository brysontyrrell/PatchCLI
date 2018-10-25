import json
import re
from setuptools import find_packages, setup

import toml

regex = re.compile(r'^__\w+__\s*=.*$')

about = dict()
with open('patchlib/__init__.py', 'r') as f:
    dunders = list()
    for l in f.readlines():
        if regex.match(l):
            dunders.append(l)
    exec('\n'.join(dunders), about)

with open('README.rst', 'r') as f:
    readme = f.read()


def get_requirements():
    pipfile = toml.load('Pipfile')
    with open('Pipfile.lock', 'r') as f:
        pipfile_lock = json.load(f)

    requirements = list()
    for r in pipfile_lock['default'].keys():
        if r in pipfile['packages'].keys():
            requirements.append('{}{}'.format(
                r, pipfile_lock['default'][r]['version'].replace('==', '>=')))

    return requirements


setup(
    name=about['__title__'],
    version=about['__version__'],
    description='A command line tool for Jamf Pro patch definition management.',
    long_description=readme,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url='https://github.com/brysontyrrell/PatchCLI',
    license=about['__license__'],
    scripts=[
        'bin/patchcli'
    ],
    packages=find_packages(),
    python_requires='>=2.7',
    install_requires=get_requirements(),
    extras_require={},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ],
    zip_safe=False
)
