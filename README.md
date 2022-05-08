# vault

v0.4

Command line password manager.

![Screenshot](screenshot/screenshot1.png)

# Installation

You need python3 to create executable and run vault password manager.

```bash
curl -L https://github.com/schwarzbox/Vault/archive/master.zip --output Vault.zip
unzip Vault.zip
cd Vault-master
# create virtual environment to install shiv
python3 -m venv venv-shiv
. venv-shiv/bin/activate
pip3 install shiv
shiv -c vault -o vault --preamble preamble.py .
deactivate
# remove venv-shiv
rm -rf venv-shiv
```

# First run

![Screenshot](screenshot/screenshot2.png)

```bash
# run vault help
./vault -h
# sign-up and create empty vault
./vault av@gmail.com Vault-96 -up
# load data to vault
./vault av@gmail.com Vault-96 -ld <your.json>
# sign-in
./vault av@gmail.com Vault-96 -in
```

# Copy to /usr/local/bin

After first run <strong>./vault</strong> you get <strong>vault_data.db</strong>.
You can copy this files together to /usr/local/bin for MacOS and Linux.

``` bash
cp vault /usr/local/bin
cp vault_data.db /usr/local/bin
vault av@gmail.com Vault-96 -in
```
