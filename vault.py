#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VAULT
"""

__version__ = 0.5

# vault.py

# MIT License
# Copyright (c) 2022 Alexander Veledzimovich veledz@gmail.com

# shiv -c vault -o vault --preamble preamble.py -r requirements.txt .

# v0.6 show --locate in TUI
# v0.7 reset password with email or with CLI
# v1.0 TUI authentication & TUI --load

import argparse
import json
import os
import re
import shelve
import time

from cryptography.fernet import InvalidToken

import crypto
import errors as err
import ui
from settings import (
    EMAIL_REGEXP, PASSWORD_REGEXP, VAULT_DB, VAULT_DIR, VAULT_TITLE
)


class Vault:
    def __init__(self, name):
        self.name = name
        self.vault = {}

    def _is_valid_credentials(self, email, password):
        if not re.fullmatch(EMAIL_REGEXP, email):
            raise err.InvalidEmail()
        if not re.fullmatch(PASSWORD_REGEXP, password):
            raise err.InvalidPassword()

    def set_user(self, login, password):
        self._is_valid_credentials(login, password)

        self.encoder = crypto.Encoder(login, password)
        self.key = self.get_vault_key(login, password)
        if not self.key:
            self.key = self.set_vault_key(login, password)
            self.save_vault()

            print(f'Empty {self.name}:', self.vault)
            print(f'Please upload data to the {self.name}')
        else:
            raise err.UserExists()

    def get_user(self, login, password):
        self.encoder = crypto.Encoder(login, password)
        self.key = self.get_vault_key(login, password)
        if self.key is not None:
            self.vault = self.load_vault()
        else:
            raise err.LoginFailed()

    def set_folder(self, key, value: dict):
        self.vault[key] = value

    def get_folder(self, key):
        return self.vault.get(key) or {}

    def set_vault_key(self, login, password):
        log_str = f'{login}-{password}'
        return self.encoder.encode(log_str)

    def get_vault_key(self, login, password):
        log_str = f'{login}-{password}'
        with shelve.open(VAULT_DB) as vault:
            for key in vault.keys():
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
        with shelve.open(VAULT_DB) as vault:
            vault[self.key] = self.vault

    def load_vault(self):
        with shelve.open(VAULT_DB) as vault:
            return vault.get(self.key)

    def dump_data(self, verbose=True):
        name = f"{VAULT_DB}-{str(time.time()).replace('.','')}.json"
        with open(name, 'w') as file:
            json.dump(self.decode_vault(), file)
        if verbose:
            print(f'Dump {self.name}: {name}')

    def load_data(self, path):
        try:
            with open(path, 'r') as file:
                self.vault = json.load(file)
                self.save_vault()
        except FileNotFoundError:
            raise err.FileNotFound(path)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            raise err.InvalidJSON(path)
        print(f'Load {self.name}: {path}')

    def remove_data(self):
        with shelve.open(VAULT_DB) as vault:
            del vault[self.key]
        print(f'Remove {self.name}: {self.encoder.decode(self.key)}')

    def locate_database(self):
        print(f'Locate {self.name} database dir: {VAULT_DIR}')


def main():
    parser = argparse.ArgumentParser(description='Vault')
    parser.add_argument(
        'login', metavar='login', type=str, help='user login'
    )
    parser.add_argument(
        'password', metavar='password', type=str, help='user password'
    )
    # actions
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-in', '--sign_in', action='store_true',
        help='use to sign in'
    )
    group.add_argument(
        '-up', '--sign_up', action='store_true',
        help='use to sign up and create vault'
    )
    group.add_argument(
        '-dp', '--dump', action='store_true',
        help='dump data to JSON'
    )
    group.add_argument(
        '-ld', '--load', dest='path', type=str,
        help='load data from JSON'
    )
    group.add_argument(
        '-rm', '--remove', action='store_true',
        help='remove vault from DB'
    )
    # info actions
    group.add_argument(
        '--locate', action='store_true',
        help='get database dir'
    )

    args = parser.parse_args()

    if not os.path.isdir(VAULT_DIR):
        os.mkdir(VAULT_DIR)

    vlt = Vault(VAULT_TITLE)
    if args.sign_up:
        try:
            vlt.set_user(args.login, args.password)
        except (err.InvalidEmail, err.InvalidPassword) as e:
            print(e)
        except err.UserExists as e:
            print(e)
    else:
        try:
            vlt.get_user(args.login, args.password)

            if args.sign_in:
                ui.ViewApp.run(title=vlt.name, vlt=vlt)
            elif args.dump:
                vlt.dump_data()
            elif args.path:
                try:
                    vlt.load_data(args.path)
                    ui.ViewApp.run(title=vlt.name, vlt=vlt)
                except (err.FileNotFound, err.InvalidJSON) as e:
                    print(e)
            elif args.remove:
                vlt.remove_data()
            elif args.locate:
                vlt.locate_database()
            else:
                parser.print_help()

        except err.LoginFailed as e:
            print(e)


if __name__ == '__main__':
    print(__version__)
    print(__doc__)
    print(__file__)
    main()
