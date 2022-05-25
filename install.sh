#!/bin/bash

echo -e '\nInstall Vault\n'

curl -L 'https://github.com/schwarzbox/Vault/archive/master.zip' --output Vault.zip
unzip Vault.zip
rm Vault.zip

cd Vault-master
# create virtual environment to install shiv
python3 -m venv venv-shiv
. venv-shiv/bin/activate
pip3 install shiv
# create vault executable in the current dir
shiv -c vault -o vault --preamble preamble.py . --use-feature=in-tree-build
deactivate

# move vault
mv vault /usr/local/bin

cd ../
rm -rf Vault-master

echo -e '\nInstalled'
which vault
vault -v

