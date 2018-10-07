import re

from os.path import join, dirname
from setuptools import setup, find_packages


# reading package version (same way the sqlalchemy does)
with open(join(dirname(__file__), 'dolphin', '__init__.py')) as v_file:
    package_version = re.compile('.*__version__ = \'(.*?)\'', re.S).\
        match(v_file.read()).group(1)


dependencies = [
    'restfulpy >= 2.3',
#    'cas-common',

    # Deployment
    'gunicorn',

]


setup(
    name='dolphin',
    version=package_version,
    packages=find_packages(),
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'dolphin = dolphin:dolphin.cli_main'
        ]
    }
)

