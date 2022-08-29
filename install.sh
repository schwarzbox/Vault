#!/bin/bash
# This file should be sourced at the top

echo -e '\nInstall Vault\n'

# create virtual environment to install shiv
python3 -m venv venv-shiv
. venv-shiv/bin/activate
pip3 install shiv
# create vault executable in the current dir
shiv -c vault -o vault --preamble preamble.py . --use-feature=2020-resolver
deactivate

# move vault
read -p 'Move vault to /usr/local/bin? [y/N] ' move
if [[ $move == "y" || $move == "Y" || $move == "yes" || $move == "Yes" ]];
then
    mv vault /usr/local/bin
fi

# remove source
read -p 'Remove source? [y/N] ' rmv
if [[ $rmv == "y" || $rmv == "Y" || $rmv == "yes" || $rmv == "Yes" ]];
then
    cd ../
    rm -rf Vault-master
    rm Vault.zip
fi

echo -e '\nInstalled'
which vault
vault -v

