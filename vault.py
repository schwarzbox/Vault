#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VAULT
"""

# vault.py

# MIT License
# Copyright (c) 2022 Alexander Veledzimovich veledz@gmail.com

# shiv -c vault -o vault --preamble preamble.py -r requirements.txt .

# v1.0 TUI authentication?

import argparse
import getpass
import json
import os
import re
import time

from art import tprint

from cryptography.fernet import InvalidToken

import requests

from rich import print

import crypto
import errors as err
from settings import (
    AUTHOR,
    DESCRIPTION,
    EMAIL,
    EMAIL_REGEXP,
    LICENSE,
    PASSWORD_REGEXP,
    TITLE_FONT,
    VAULT_DB,
    VAULT_DIR,
    VAULT_TITLE,
    VERSION,
    URL
)
import tui


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
    def __init__(self):
        self.vault = {}
        self.vault_db = VAULT_DB

        if not os.path.isdir(VAULT_DIR):
            os.mkdir(VAULT_DIR)
        if not os.path.isfile(self.vault_db):
            with open(self.vault_db, 'w') as file:
                json.dump(self.vault, file)

    def is_empty(self):
        return not bool(self.vault)

    def set_user(self, login, password):
        self.encoder = crypto.Encoder(login, password)
        database = self.get_database()
        self.key = self.get_vault_key(login, password, database)
        if not self.key:
            self.set_vault_key(login, password)
            self.save_vault()
        else:
            raise err.UserExists()

    def get_user(self, login, password, url=None):
        self.encoder = crypto.Encoder(login, password)
        database = self.get_database(url)
        self.key = self.get_vault_key(login, password, database)
        if self.key is not None:
            self.vault = self.load_vault(database)
        else:
            raise err.LoginFailed()

    def set_vault_key(self, login, password):
        log_str = f'{login}-{password}'
        self.key = self.encoder.encode(log_str)

    def get_database(self, url=None):
        path = None
        try:
            if url:
                path = url
                response = requests.get(path)
                if response.ok:
                    return json.loads(response.content)
                else:
                    raise err.FileNotFound(path)
            else:
                path = self.vault_db
                with open(path, 'r') as file:
                    return json.load(file)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            raise err.InvalidJSON(path)

    def get_vault_key(self, login, password, database):
        log_str = f'{login}-{password}'
        for key in database.keys():
            try:
                if self.encoder.decode(key) == log_str:
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
        with open(self.vault_db, 'r') as file:
            data = json.load(file)

        with open(self.vault_db, 'w') as file:
            data[self.key] = self.vault
            json.dump(data, file)

    def load_vault(self, database):
        return database.get(self.key)

    def remove_vault(self):
        data = {}
        with open(self.vault_db, 'r') as file:
            data = json.load(file)

        with open(self.vault_db, 'w') as file:
            del data[self.key]
            json.dump(data, file)

        err.show_warning(
            f'Remove vault: {self.encoder.decode(self.key)}'
        )

    def get_json_path(self):
        return f"{VAULT_DB}-{str(time.time()).replace('.','')}.json"

    def dump_data(self, name, verbose=True):
        with open(name, 'w') as file:
            json.dump(self.decode_vault(), file)
        if verbose:
            err.show_warning(f'Dump JSON: {name}')
        else:
            return name

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
        return path

    def erase_data(self):
        self.vault = {}
        self.save_vault()

    def find_database(self, verbose=True):
        if verbose:
            err.show_warning(f'Find DB: {self.vault_db}')
        else:
            return self.vault_db

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

    # actions
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-in', '--sign_in', action='store_true',
        help='use to sign in'
    )
    # remote url
    parser.add_argument(
        '-u', '--url', dest='url', type=str,
        help='load encrypted data from remote DB to local vault'
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
        help='find local DB'
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

    vlt = Vault()

    if args.sign_up:
        lpv = LoginPasswordValidator(args.login)
        try:
            lpv.is_valid()
            vlt.set_user(lpv.login, lpv.password)
            tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
        except (err.InvalidEmail, err.InvalidPassword) as e:
            err.show_error(e)
        except err.UserExists as e:
            err.show_error(e)
    elif args.find:
        vlt.find_database()
    elif args.version:
        vlt.version()
    elif args.about:
        vlt.about()
    else:

        lpv = LoginPasswordValidator(args.login)
        try:
            vlt.get_user(lpv.login, lpv.password, args.url)

            if args.remove:
                vlt.remove_vault()
            elif args.dump:
                vlt.dump_data(vlt.get_json_path())
            elif args.path:
                try:
                    vlt.load_data(args.path)
                    tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
                except (
                    err.FileNotFound,
                    err.InvalidJSON,
                    err.InvalidDataFormat
                ) as e:
                    err.show_error(e)
            elif args.erase:
                vlt.erase_data()
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)
            else:
                tui.ViewApp.run(title=VAULT_TITLE, vlt=vlt)

        except (
            err.FileNotFound, err.InvalidJSON, err.LoginFailed
        ) as e:
            err.show_error(e)


if __name__ == '__main__':
    print(__version__)
    print(__doc__)
    print(__file__)
    main()
