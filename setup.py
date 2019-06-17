import re

from os.path import join, dirname
from setuptools import setup, find_packages


# reading package version (same way the sqlalchemy does)
with open(join(dirname(__file__), 'dolphin', '__init__.py')) as v_file:
    package_version = re.compile('.*__version__ = \'(.*?)\'', re.S).\
        match(v_file.read()).group(1)


# FIXME: Must be change dependency when the restfulpy release.
dependencies = [
    'sqlalchemy_media >= 0.17.1',
#    'restfulpy >= 3.0.0',
    'oathcy',

    # Deployment
    'gunicorn',
]


setup(
    name='dolphin',
    version=package_version,
    packages=find_packages(),
    install_requires=dependencies,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dolphin = dolphin:dolphin.cli_main'
        ]
    }
)

