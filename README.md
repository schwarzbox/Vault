# Vault

v1.3

Command line password manager.

![Screenshot](screenshot/screenshot1.png)

# Install

You need python 3.9 to create executable and run <strong>vault</strong> password manager.

## Manual installation

```bash
curl -L https://github.com/schwarzbox/Vault/archive/master.zip --output Vault.zip
unzip Vault.zip
rm Vault.zip

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

You can move <strong>vault</strong> to /usr/local/bin for Mac and Linux OS.

``` bash
mv vault /usr/local/bin
```

## Use install.sh (bash only)

``` bash
curl -L 'https://github.com/schwarzbox/Vault/archive/master.zip' --output Vault.zip
unzip Vault.zip
cd Vault-master

chmod 744 install.sh
# run in the same process
source ./install.sh
```

# First run

```bash
vault -h
```

![Screenshot](screenshot/screenshot2.png)

## Info

```bash
vault --info
```

## Version

```bash
vault --version
```

# Create vault

```bash
# enter login and run sign-up process
vault av@myemail.com -up
# sign-in with login
vault av@myemail.com -in
# you can omit flag -in
vault av@myemail.com
```

Note: User can use same login with new password to create different vault.

# Prepare JSON with your sensetive data. Try to use emojis in titles.

Use example below or use sample.json to test password manager.

```JSON
{
    "💌 email": {
        "login": "av@myemail.com",
        "password": "1234"
    },
    "☁️ aws": {
        "login": "av@myemail.com",
        "password": "5678"
    },
    "🧰 database": {
        "django-local": "DATABASE_NAME=MYDB\nDATABASE_USER=postgres\nDATABASE_PASSWORD=''\nDATABASE_HOST=127.0.0.1\nDATABASE_PORT=5432\nDATABASE_CONN_MAX_AGE=600"
    },
    "🏠 personal": {
        "WIFI-HOME": "wifi-av"
    }
}
```

Load sample.json using command line or use TUI after sign-in.

```bash
vault av@myemail.com --load sample.json
```

# Dump decrypted data from the source vault to JSON

```bash
vault av@myemail.com --dump
```

# Remove vault from the local database

```bash
vault av@myemail.com -rm
```

# Find local database dir

Iternally <strong>Vault</strong> use python package <strong>appdirs</strong> to determine where to save local encrypted database. For MacOS it is "~/Library/Application Support/VaultDB".

```bash
vault --find
```

# Remote access

<strong>Vault</strong> creates default database and --source flag set to None. You can provide remote or local source for current session.

Upload encrypted database in GitHub or anywere else.

Load database in github repo. It is safe if you upload encrypted data.

```bash
vault av@myemail.com --source 'https://raw.githubusercontent.com/MYGIT/MYREPO/main/vault_data'
```

Load vault database in private github repo. You need to provide token. But this token expired and you need to generate new link.

```bash
vault av@myemail.com --source 'https://raw.githubusercontent.com/MYGIT/MYREPO/main/vault_data?token=TOKEN'
```

You can create secret gist and load encrypted database.

```bash
vault av@myemail.com --source 'https://gist.githubusercontent.com/MYGIT/1234/raw/1234/vault_data'
```

You can switch to remote source at runtime using TUI.

![Screenshot](screenshot/screenshot3.png)

# Use TUI to manage vault.

![Screenshot](screenshot/screenshot4.png)

Add, update and clear data in the local vault

![Screenshot](screenshot/screenshot5.png)

# Use CL to manage vault.

## Get data from the source vault

```bash
vault av@myemail.com -g aws login
```

```bash
vault av@myemail.com -g aws login | wc -c
```

## List all groups and keys

```bash
vault av@myemail.com -l
```

## Add data to the local vault

```bash
vault av@myemail.com -a aws login av@myemail.com
```

## Update data in the local vault (default value for second argument is "vault")

```bash
vault av@myemail.com -u aws
```

You can update group name only

```bash
vault av@myemail.com -u group myaws
```

You can update key name only

```bash
vault av@myemail.com -u myaws myaws login username
```

You should use 5 arguments to update value

```bash
vault av@myemail.com -u myaws myaws username username alex@myemail.com
```

## Clear data in the local vault

```bash
vault av@myemail.com -c myaws username
```

## Erase all data in the local vault

```bash
vault av@myemail.com -e
```

# Encryption

Vault use SHA256 algorithm. Database is a simple JSON file.

1. When user sign-up app creates <strong>safe key</strong> using login and password.
2. App combine login and password in one <strong>credential string</strong>.
3. App uses <strong>safe key</strong> to encode <strong>credential string</strong> and get <strong>user token</strong>.
4. <strong>User token</strong> uses as unique key for the user vault.
5. All data in the user vault encrypted using <strong>safe key</strong>.
6. When user sign-in app creates new safe key from provided login and password.
7. App tries to decode each <strong>user token</strong> in database and compare with provided login and password.
8. User successfully sign-in when provided login and password matches with decoded data from <strong>user token</strong>.

## Restore password and decode data

Vault never save your decrypted password. Still no way to restore it and decode ecrypted data without password.
