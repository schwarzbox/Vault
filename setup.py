from setuptools import find_packages, setup

from settings import (
    AUTHOR, DESCRIPTION, EMAIL, LICENSE, VAULT_TITLE, VERSION, URL
)


with open('README.md', 'r') as f:
    long_description = f.read()

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
        'vault', 'crypto', 'errors',
        'tui', 'mixins', 'widgets',
        'settings'
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'art', 'cryptography', 'pyperclip', 'textual', 'appdirs'
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': ['vault=vault:main'],
    },
)
