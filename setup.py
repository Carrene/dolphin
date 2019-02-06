import re

from os.path import join, dirname
from setuptools import setup, find_packages


# reading package version (same way the sqlalchemy does)
with open(join(dirname(__file__), 'dolphin', '__init__.py')) as v_file:
    package_version = re.compile('.*__version__ = \'(.*?)\'', re.S).\
        match(v_file.read()).group(1)


dependencies = [
    'restfulpy >= 2.6.14',

    # FIXME: Remove this line when the bug on bddrest v2.2.0 fixed
    'bddrest == 2.1.5',
    'sqlalchemy_media >= 0.17.1',
#    'cas-common',

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

