# vault

v0.6

Command line password manager.

![Screenshot](screenshot/screenshot1.png)

# Install

You need python 3.9 to create executable and run <strong>vault</strong> password manager.

```bash
curl -L https://github.com/schwarzbox/Vault/archive/master.zip --output Vault.zip
unzip Vault.zip
cd Vault-master
# create virtual environment to install shiv
python3 -m venv venv-shiv
. venv-shiv/bin/activate
pip3 install shiv
# create vault executable in the current dir
shiv -c vault -o vault --preamble preamble.py .
deactivate
# remove venv-shiv
rm -rf venv-shiv
```

# Move to /usr/local/bin

You can move <strong>vault</strong> to /usr/local/bin for Mac and Linux OS.

``` bash
mv vault /usr/local/bin
```

After moving <strong>vault</strong> you can remove Vault-master and Vault.zip.

# First run

```bash
vault -h
```

![Screenshot](screenshot/screenshot2.png)

```bash
# sign-up and create empty vault
vault av@myemail.com Vault-96 -up
# sign-in and check that vault is empty
vault av@myemail.com Vault-96 -in
# you can omit flag -in
vault av@myemail.com Vault-96
```

# Prepare JSON with your sensetive data

See example below or use sample.json for testing password manager.

```JSON
{
    "email": {
        "login": "av@myemail.com",
        "password": "1234"
    },
    "aws": {
        "login": "av@myemail.com",
        "password": "5678"
    },
    "database": {
        "django-local": "DATABASE_NAME=MYDB\nDATABASE_USER=postgres\nDATABASE_PASSWORD=''\nDATABASE_HOST=127.0.0.1\nDATABASE_PORT=5432\nDATABASE_CONN_MAX_AGE=600"
    },
    "personal": {
        "WIFI-HOME": "wifi-av"
    }
}
```

```bash
# load data from json to your vault and auto sign-in
vault av@myemail.com Vault-96 --load sample.json
```

# Database location

Iternally <strong>vault</strong> use python package <strong>appdirs</strong> to determine where to save encrypted database. For MacOS it is "/Users/whoami/Library/Application Support/VaultDB" dir.

```bash
# find VaultDB location
vault av@myemail.com Vault-96 --find
```

# Remove data

```bash
vault av@myemail.com Vault-96 -rm
```

# Road map

v0.65 spinner for load JSON pop-up, change icons, add info about encryption in README.md

v0.7 reset password with email, add about page

v0.8 change scroll color, move login validator to separate class

v1.0 TUI authentication

v1.1 setup cloud access to vault_data.db
