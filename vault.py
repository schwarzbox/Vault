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

# protection when load data
# check warning and errors
# refactor TUI update readme

import argparse
import json
import os
import sys
import time

from appdirs import user_data_dir

from art import tprint

from cryptography.fernet import InvalidToken

import requests

import crypto
import errors as err
from settings import (
    AUTHOR,
    DESCRIPTION,
    EMAIL,
    LICENSE,
    TITLE_FONT,
    URL,
    VAULT_DB,
    VAULT_TITLE,
    VERSION,
)
import tui
import validators


class Vault:
    def __init__(self, source=None, is_piped=False):
        self.vault = {}

        self.local_dir = user_data_dir(f'{VAULT_TITLE}DB')
        self.set_source()
        self.set_default_database()

        self.set_source(source)

        self.is_piped = is_piped

    @property
    def is_empty(self):
        return not bool(self.vault)

    @property
    def is_local_source(self):
        return not self.vault_db.startswith('http')

    def get_default_source(self):
        return f'{self.local_dir}/{VAULT_DB}'

    def set_source(self, source=None):
        if source is not None:
            self.vault_db = source
        else:
            self.vault_db = self.get_default_source()

    def set_default_database(self):
        if not os.path.isdir(self.local_dir):
            os.mkdir(self.local_dir)
        if not os.path.isfile(self.vault_db):
            with open(self.vault_db, 'w') as file:
                json.dump(self.vault, file)

    def get_key_str(self, login, password):
        return f'{login} {password}'

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
            raise err.LocalDataBaseNotFound(
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
        for group in self.vault:
            crt_group = self.encoder.encode(group)
            crt_vault[crt_group] = {}
            for key in self.vault[group]:
                crt_key = self.encoder.encode(key)
                crt_val = self.encoder.encode(self.vault[group][key])
                crt_vault[crt_group][crt_key] = crt_val
        return crt_vault

    def decode_vault(self):
        cln_vault = {}
        for group in self.vault:
            cln_group = self.encoder.decode(group)
            cln_vault[cln_group] = {}
            for key in self.vault[group]:
                cln_key = self.encoder.decode(key)
                cln_val = self.encoder.decode(self.vault[group][key])
                cln_vault[cln_group][cln_key] = cln_val
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
            raise err.LocalDataBaseNotFound(
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
            raise err.LocalDataBaseNotFound(
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
        if not self.is_local_source:
            raise err.ActionNotAllowedForRemote()

        with open(path, 'w') as file:
            json.dump(self.decode_vault(), file)
        if verbose:
            err.show_warning(f'Dump JSON: "{path}"')
        else:
            return f'"{path}"'

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

    def get_database_path(self):
        if self.is_local_source and not os.path.exists(self.vault_db):
            return 'Database not found'
        return self.vault_db

    def find_database(self, path, verbose=True):
        if verbose:
            err.show_warning(f'Find DB: "{path}"')
        else:
            return f'"{path}"'

    def info(self, verbose=True):
        info = f'{VAULT_TITLE} v{VERSION} {LICENSE}'
        desc = f'{DESCRIPTION}\n{URL}'
        author = f'{AUTHOR}\n{EMAIL}'
        message = f'{info}\n\n{desc}\n\n{author}'
        if verbose:
            err.show_notification(f'Info:\n\n{message}\n')
        else:
            return message

    def version(self):
        err.show_notification(f'Version: {VERSION}')

    def get_data(self, group, value):
        decoded = self.decode_vault()
        group = decoded.get(group, {})

        end = '\n'
        if self.is_piped:
            end = ''

        err.show_notification(group.get(value, ''), end=end)

    def add_data(self, group, key, value):
        decoded = self.decode_vault()

        decoded[group] = decoded.get(group, {})

        if not (decoded[group].get(key, None) is not None):
            decoded[group][key] = value
            self.vault = decoded
            self.save_vault()
        else:
            raise err.KeyAlreadyExists(key)

    def update_data(
        self,
        group,
        new_group=VAULT_TITLE,
        key=None,
        new_key=None,
        new_value=None
    ):
        decoded = self.decode_vault()
        if decoded.get(group, None) is not None:
            data = {**decoded[group]}
            del decoded[group]
            if decoded.get(new_group.lower(), None) is not None:
                raise err.GroupAlreadyExists(new_group)

            decoded[new_group] = data
        else:
            raise err.GroupNotExists(group)

        if key is not None and new_key is not None:
            if decoded[new_group].get(key, None) is not None:
                data = decoded[new_group][key]
                del decoded[new_group][key]
                if decoded[new_group].get(new_key, None) is not None:
                    raise err.KeyAlreadyExists(new_key)

                decoded[new_group][new_key] = data
            else:
                raise err.KeyNotExists(key)

        if new_value is not None:
            decoded[new_group][new_key] = new_value

        self.vault = decoded
        self.save_vault()

    def clear_data(self, group, key):
        decoded = self.decode_vault()
        if decoded.get(group, None) is not None:
            if decoded[group].get(key, None) is not None:
                del decoded[group][key]
                if len(decoded[group]) == 0:
                    del decoded[group]

                self.vault = decoded
                self.save_vault()
            else:
                raise err.KeyNotExists(key)
        else:
            raise err.GroupNotExists(group)

    def erase_data(self):
        self.vault = {}
        self.save_vault()


def main():
    is_piped = True
    if sys.stdout.isatty():
        is_piped = False
        tprint(f'\n{VAULT_TITLE.upper()}', font=TITLE_FONT)

    parser = argparse.ArgumentParser(
        description=DESCRIPTION
    )

    # required
    parser.add_argument(
        'login', nargs='?', metavar='login', type=str,
        help='user login'
    )

    # actions
    main_group = parser.add_mutually_exclusive_group()
    main_group.add_argument(
        '-in', '--sign_in', action='store_true',
        help='use to sign in'
    )
    main_group.add_argument(
        '-up', '--sign_up', action='store_true',
        help='use to sign up and create an empty vault in the local DB'
    )
    main_group.add_argument(
        '-dp', '--dump', action='store_true',
        help='dump decrypted data from the source vault to JSON'
    )
    main_group.add_argument(
        '-ld', '--load', dest='path', type=str,
        help='load decrypted data from JSON to the local vault'
    )
    main_group.add_argument(
        '-rm', '--remove', action='store_true',
        help='remove vault from the local DB'
    )

    # info actions
    main_group.add_argument(
        '-f', '--find', action='store_true',
        help='find DB'
    )
    main_group.add_argument(
        '-i', '--info', action='store_true',
        help='show info'
    )
    main_group.add_argument(
        '-v', '--version', action='store_true',
        help='show version'
    )

    # select source
    parser.add_argument(
        '-s', '--source', dest='source', type=str,
        help='load encrypted vault from the source DB'
    )
    parser.add_argument(
        '-g', '--get', nargs=2, dest='get', type=str,
        metavar=('GROUP', 'KEY'),
        help='get data from the source vault'
    )
    main_group.add_argument(
        '-a', '--add', nargs=3, dest='add', type=str,
        metavar=('GROUP', 'KEY', 'VALUE'),
        help='add data to the local vault'
    )
    main_group.add_argument(
        '-u', '--update', nargs='+', dest='update', type=str,
        metavar=('GROUP', 'NEW_GROUP',),
        help='update data in the local vault'
    )
    main_group.add_argument(
        '-c', '--clear', nargs=2, dest='clear', type=str,
        metavar=('GROUP', 'KEY'),
        help='clear data in the local vault'
    )
    main_group.add_argument(
        '-e', '--erase', action='store_true',
        help='erase all data in the local vault'
    )

    args = parser.parse_args()

    if (
        not args.login
        and not (
            args.find or args.version or args.info
        )
    ):
        parser.error('the following arguments are required: login')

    vlt = Vault(args.source, is_piped)

    if args.sign_up:
        lpv = validators.LoginPasswordValidator(args.login)
        try:
            lpv.is_valid()
            vlt.set_user(lpv.login, lpv.password)
            tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
        except (
            err.ActionNotAllowedForRemote,
            err.LocalDataBaseNotFound,
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
    elif args.info:
        vlt.info()
    else:

        lpv = validators.LoginPasswordValidator(args.login)
        try:
            vlt.get_user(lpv.login, lpv.password)

            if args.dump:
                vlt.dump_data(vlt.get_json_path())
            elif args.path:
                vlt.load_data(args.path)
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
            elif args.remove:
                vlt.remove_vault()
            elif args.get:
                vlt.get_data(*args.get)
            elif args.add:
                vlt.add_data(*args.add)
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
            elif args.update:
                vlt.update_data(*args.update)
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
            elif args.clear:
                vlt.clear_data(*args.clear)
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
            elif args.erase:
                vlt.erase_data()
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
            else:
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)

        except (
            err.ActionNotAllowedForRemote,
            err.LocalDataBaseNotFound,
            err.FileNotFound,
            err.InvalidJSON,
            err.InvalidDataFormat,
            err.InvalidURL,
            err.LoginFailed,
            err.GroupNotExists,
            err.GroupAlreadyExists,
            err.KeyNotExists,
            err.KeyAlreadyExists
        ) as e:
            try:
                err.show_error(e)
            except BrokenPipeError:
                pass


if __name__ == '__main__':
    main()
