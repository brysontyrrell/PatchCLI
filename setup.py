import re
from setuptools import find_packages, setup

regex = re.compile(r'^__\w+__\s*=.*$')


def get_dunders():
    values = dict()
    with open('patchlib/__init__.py', 'r') as f:
        dunders = list()
        for l in f.readlines():
            if regex.match(l):
                dunders.append(l)
        exec('\n'.join(dunders), values)

    return values


def get_readme():
    with open('README.rst', 'r') as f:
        readme = f.read()

    return readme


about = get_dunders()

requirements = [
    "jsonschema>=2.6.0",
    "requests>=2.20.0"
]

setup(
    name=about['__title__'],
    version=about['__version__'],
    description='A command line tool for Jamf Pro patch definition management.',
    long_description=get_readme(),
    author=about['__author__'],
    author_email=about['__author_email__'],
    url='https://github.com/brysontyrrell/PatchCLI',
    license=about['__license__'],
    scripts=[
        'bin/patchcli'
    ],
    packages=find_packages(),
    python_requires='>=2.7',
    include_package_data=True,
    install_requires=requirements,
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
