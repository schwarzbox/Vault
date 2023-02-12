from setuptools import find_packages, setup

from settings import (
    AUTHOR, DESCRIPTION, EMAIL, LICENSE, URL, VAULT_TITLE, VERSION
)


with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name=VAULT_TITLE,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    license=LICENSE,
    py_modules=[
        'vault', 'settings',
        'crypto', 'errors', 'mixins', 'tui', 'validators', 'widgets'
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    python_requires='>=3.9',
    entry_points={
        'console_scripts': ['vault=vault:main'],
    },
)
