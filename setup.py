from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='Vault',
    version='0.65',
    description='Password manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/schwarzbox/Vault',
    author='Alex Veledzimovich',
    author_email='veledz@gmail.com',
    license='MIT',
    py_modules=[
        'vault', 'crypto', 'errors', 'ui', 'mixins', 'settings'
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'art', 'cryptography', 'pyperclip', 'textual', 'appdirs'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': ['vault=vault:main'],
    },
)
