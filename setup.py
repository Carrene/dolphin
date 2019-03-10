import re

from os.path import join, dirname
from setuptools import setup, find_packages


# reading package version (same way the sqlalchemy does)
with open(join(dirname(__file__), 'dolphin', '__init__.py')) as v_file:
    package_version = re.compile('.*__version__ = \'(.*?)\'', re.S).\
        match(v_file.read()).group(1)


dependencies = [
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
    dependency_links=[
           "git+ssh://git@github.com/Carrene/restfulpy@390f2379b979daa96355eb8e22e8af3477ba0e27"
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dolphin = dolphin:dolphin.cli_main'
        ]
    }
)

