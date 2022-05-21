#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VAULT
"""

# vault.py

# MIT License
# Copyright (c) 2022 Alexander Veledzimovich veledz@gmail.com

# shiv -c vault -o vault --preamble preamble.py -r requirements.txt .
# shiv -c vault -o vault --preamble preamble.py .


from appdirs import user_data_dir

import tui
from settings import (
    AUTHOR,
    DESCRIPTION,
    EMAIL,
    EMAIL_REGEXP,
    LICENSE,
    LOCAL,
    PASSWORD_REGEXP,
    TITLE_FONT,
    VAULT_DB,
    VAULT_TITLE,
    VERSION,
    URL
)
import errors as err
import crypto
import requests
from cryptography.fernet import InvalidToken
from art import tprint
import time
import re
import os
import json
import getpass
import argparse


__version__ = VERSION


class LoginPasswordValidator:
    def __init__(self, login):
        self.login = login
        self.password = getpass.getpass('Password? ')

    def is_valid(self):
        if not re.fullmatch(EMAIL_REGEXP, self.login):
            raise err.InvalidEmail()
        if not re.fullmatch(PASSWORD_REGEXP, self.password):
            raise err.InvalidPassword()


class Vault:
    def __init__(self, source=LOCAL):
        self.vault = {}
        self.source = source
        self.local_dir = user_data_dir(f'{VAULT_TITLE}DB')
        if self.is_local_source:
            self.set_local_source()
        else:
            self.set_remote_source()

    @property
    def is_empty(self):
        return not bool(self.vault)

    @property
    def is_local_source(self):
        return self.source == LOCAL

    def get_key_str(self, login, password):
        return f'{login} {password}'

    def set_local_source(self):
        self.vault_dir = self.local_dir
        self.vault_db = f'{self.vault_dir}/{VAULT_DB}'
        if not os.path.isdir(self.vault_dir):
            os.mkdir(self.vault_dir)
        if not os.path.isfile(self.vault_db):
            with open(self.vault_db, 'w') as file:
                json.dump(self.vault, file)

    def set_remote_source(self):
        self.vault_dir = os.path.dirname(self.source)
        self.vault_db = self.source

    def set_user(self, login, password):
        self.encoder = crypto.Encoder(login, password)
        database = self.get_database()
        self.key = self.get_vault_key(login, password, database)
        if not self.key:
            self.set_vault_key(login, password)
            self.save_vault()
        else:
            raise err.UserExists()

    def get_user(self, login, password):
        self.encoder = crypto.Encoder(login, password)
        database = self.get_database()
        self.key = self.get_vault_key(login, password, database)
        if self.key is not None:
            self.vault = self.load_vault(database)
        else:
            raise err.LoginFailed()

    def set_vault_key(self, login, password):
        self.key = self.encoder.encode(
            self.get_key_str(login, password)
        )

    def get_database(self):
        try:
            if self.is_local_source:
                with open(self.vault_db, 'r') as file:
                    return json.load(file)
            else:
                response = requests.get(self.vault_db)

                if response.ok:
                    return json.loads(response.content)
                else:
                    raise err.FileNotFound(self.vault_db)

        except FileNotFoundError:
            raise err.DataBaseNotFound(
                os.path.basename(self.vault_db)
            )
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            raise err.InvalidJSON(self.vault_db)
        except requests.exceptions.InvalidURL:
            raise err.InvalidURL(self.vault_db)
        except requests.exceptions.MissingSchema:
            raise err.InvalidURL(self.vault_db)
        except AttributeError:
            raise err.InvalidDataFormat(self.vault_db)

    def get_vault_key(self, login, password, database):
        key_str = self.get_key_str(login, password)
        for key in database.keys():
            try:
                if self.encoder.decode(key) == key_str:
                    return key
            except InvalidToken:
                pass

    def encode_vault(self):
        crt_vault = {}
        for folder in self.vault:
            crt_folder = self.encoder.encode(folder)
            crt_vault[crt_folder] = {}
            for key in self.vault[folder]:
                crt_key = self.encoder.encode(key)
                crt_val = self.encoder.encode(self.vault[folder][key])
                crt_vault[crt_folder][crt_key] = crt_val
        return crt_vault

    def decode_vault(self):
        cln_vault = {}
        for folder in self.vault:
            cln_folder = self.encoder.decode(folder)
            cln_vault[cln_folder] = {}
            for key in self.vault[folder]:
                cln_key = self.encoder.decode(key)
                cln_val = self.encoder.decode(self.vault[folder][key])
                cln_vault[cln_folder][cln_key] = cln_val
        return cln_vault

    def save_vault(self):
        self.vault = self.encode_vault()
        data = {}

        if not self.is_local_source:
            raise err.ActionNotAllowedForRemote()
        try:
            with open(self.vault_db, 'r') as file:
                data = json.load(file)

            with open(self.vault_db, 'w') as file:
                data[self.key] = self.vault
                json.dump(data, file)
        except FileNotFoundError:
            raise err.DataBaseNotFound(
                os.path.basename(self.vault_db)
            )

    def load_vault(self, database):
        return database.get(self.key)

    def remove_vault(self):
        data = {}
        if not self.is_local_source:
            raise err.ActionNotAllowedForRemote()
        try:
            with open(self.vault_db, 'r') as file:
                data = json.load(file)

            with open(self.vault_db, 'w') as file:
                del data[self.key]
                json.dump(data, file)

        except FileNotFoundError:
            raise err.DataBaseNotFound(
                os.path.basename(self.vault_db)
            )

        err.show_warning(
            f'Remove vault: {self.encoder.decode(self.key)}'
        )

    def get_json_path(self):
        name = str(time.time()).replace('.', '')
        return (
            f'{self.local_dir}/vault_decrypted-{name}.json'
        )

    def dump_data(self, path, verbose=True):
        with open(path, 'w') as file:
            json.dump(self.decode_vault(), file)
        if verbose:
            err.show_warning(f'Dump JSON: {path}')
        else:
            return path

    def load_data(self, path):
        try:
            with open(path, 'r') as file:
                self.vault = json.load(file)
                self.save_vault()
        except FileNotFoundError:
            raise err.FileNotFound(path)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            raise err.InvalidJSON(path)
        except AttributeError:
            raise err.InvalidDataFormat(path)

    def erase_data(self):
        self.vault = {}
        self.save_vault()

    def get_database_path(self):
        return self.vault_db

    def find_database(self, path, verbose=True):
        if verbose:
            err.show_warning(f'Find DB: {path}')
        else:
            return path

    def about(self, verbose=True):
        info = f'{VAULT_TITLE} v{VERSION} {LICENSE}'
        desc = f'{DESCRIPTION}\n{URL}'
        author = f'{AUTHOR}\n{EMAIL}'
        message = f'{info}\n\n{desc}\n\n{author}'
        if verbose:
            err.show_info(f'About:\n\n{message}\n')
        else:
            return message

    def version(self):
        err.show_warning(f'Version: {VERSION}')


def main():
    tprint(f'\n{VAULT_TITLE.upper()}', font=TITLE_FONT)

    parser = argparse.ArgumentParser(description=VAULT_TITLE)

    # required
    parser.add_argument(
        'login', nargs='?', metavar='login', type=str,
        help='user login'
    )
    # select source
    parser.add_argument(
        '-src', '--source', dest='source', type=str, default=LOCAL,
        help='load encrypted data from remote DB to local vault'
    )

    # actions
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-in', '--sign_in', action='store_true',
        help='use to sign in'
    )

    group.add_argument(
        '-up', '--sign_up', action='store_true',
        help='use to sign up and create empty vault in local DB'
    )

    group.add_argument(
        '-rm', '--remove', action='store_true',
        help='remove vault from local DB'
    )

    group.add_argument(
        '-dp', '--dump', action='store_true',
        help='dump decrypted data from local vault to JSON'
    )
    group.add_argument(
        '-ld', '--load', dest='path', type=str,
        help='load decrypted data from JSON to local vault'
    )
    group.add_argument(
        '-er', '--erase', action='store_true',
        help='erase data in local vault'
    )

    # info actions
    group.add_argument(
        '-f', '--find', action='store_true',
        help='find DB dir'
    )
    group.add_argument(
        '-a', '--about', action='store_true',
        help='show about'
    )
    group.add_argument(
        '-v', '--version', action='store_true',
        help='show version'
    )

    args = parser.parse_args()

    if (
        not args.login and not (
            args.find or args.version or args.about
        )
    ):
        parser.error('the following arguments are required: login')

    vlt = Vault(args.source)

    if args.sign_up:
        lpv = LoginPasswordValidator(args.login)
        try:
            lpv.is_valid()
            vlt.set_user(lpv.login, lpv.password)
            tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
        except (
            err.ActionNotAllowedForRemote,
            err.DataBaseNotFound,
            err.FileNotFound,
            err.InvalidJSON,
            err.InvalidEmail,
            err.InvalidPassword,
            err.InvalidURL,
            err.UserExists
        ) as e:
            err.show_error(e)
    elif args.find:
        vlt.find_database(vlt.get_database_path())
    elif args.version:
        vlt.version()
    elif args.about:
        vlt.about()
    else:

        lpv = LoginPasswordValidator(args.login)
        try:
            vlt.get_user(lpv.login, lpv.password)

            if args.remove:
                vlt.remove_vault()
            elif args.dump:
                vlt.dump_data(vlt.get_json_path())
            elif args.path:
                vlt.load_data(args.path)
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
            elif args.erase:
                vlt.erase_data()
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
            else:
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)

        except (
            err.ActionNotAllowedForRemote,
            err.DataBaseNotFound,
            err.FileNotFound,
            err.InvalidJSON,
            err.InvalidDataFormat,
            err.InvalidURL,
            err.LoginFailed
        ) as e:
            err.show_error(e)


if __name__ == '__main__':
    print(__version__)
    print(__doc__)
    print(__file__)
    main()
