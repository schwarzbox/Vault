#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VAULT
"""

# vault.py

# MIT License
# Copyright (c) 2022 Alexander Veledzimovich veledz@gmail.com

# shiv -c vault -o vault --preamble preamble.py -r requirements.txt .

# v0.9 TUI authentication
# v1.0 change vaultDB path & provide access to vault_data.db by http

import argparse
import getpass
import json
import os
import re
import shelve
import time

from art import tprint

from cryptography.fernet import InvalidToken

from rich import print

import crypto

import errors as err
from errors import show_error, show_warning

from settings import (
    EMAIL_REGEXP,
    PASSWORD_REGEXP,
    TITLE_FONT,
    VAULT_DB,
    VAULT_DB_UI,
    VAULT_DIR,
    VAULT_TITLE,
    VERSION
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
    def __init__(self, name):
        if not os.path.isdir(VAULT_DIR):
            os.mkdir(VAULT_DIR)

        self.name = name
        self.vault = {}

    def is_empty(self):
        return not bool(self.vault)

    def set_user(self, login, password):
        self.encoder = crypto.Encoder(login, password)
        self.key = self.get_vault_key(login, password)
        if not self.key:
            self.set_vault_key(login, password)
            self.save_vault()
        else:
            raise err.UserExists()

    def get_user(self, login, password):
        self.encoder = crypto.Encoder(login, password)
        self.key = self.get_vault_key(login, password)
        if self.key is not None:
            self.vault = self.load_vault()
        else:
            raise err.LoginFailed()

    def set_vault_key(self, login, password):
        log_str = f'{login}-{password}'
        self.key = self.encoder.encode(log_str)

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
            vault[self.key] = {
                'DB': VAULT_DIR,
                VAULT_TITLE: self.vault
            }

    def load_vault(self):
        with shelve.open(VAULT_DB) as vault:
            return vault.get(self.key).get(VAULT_TITLE)

    def get_json_path(self):
        return f"{VAULT_DB}-{str(time.time()).replace('.','')}.json"

    def dump_data(self, name, verbose=True):
        with open(name, 'w') as file:
            json.dump(self.decode_vault(), file)
        if verbose:
            show_warning(f'Dump {self.name}: {name}')
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

        return path

    def remove_data(self):
        with shelve.open(VAULT_DB) as vault:
            del vault[self.key]

        show_warning(
            f'Remove {self.name}: {self.encoder.decode(self.key)}'
        )

    def find_database(self, verbose=True):
        if verbose:
            show_warning(f'Find {self.name} DB: {VAULT_DB_UI}')
        else:
            return VAULT_DB_UI

    def version(self):
        show_warning(f'Version: {VERSION}')


def main():
    tprint(f'\n{VAULT_TITLE.upper()}', font=TITLE_FONT)

    parser = argparse.ArgumentParser(description=VAULT_TITLE)

    # requi{RED}
    parser.add_argument(
        'login', metavar='login', type=str, help='user login'
    )

    # actions
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-in', '--sign_in', action='store_true',
        help='use to sign in'
    )
    group.add_argument(
        '-up', '--sign_up', action='store_true',
        help='use to sign up and create empty vault'
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
        '-f', '--find', action='store_true',
        help='find database directory'
    )
    group.add_argument(
        '-v', '--version', action='store_true',
        help='show version'
    )

    args = parser.parse_args()

    vlt = Vault(VAULT_TITLE)

    if args.sign_up:
        lpv = LoginPasswordValidator(args.login)
        try:
            lpv.is_valid()
            vlt.set_user(lpv.login, lpv.password)
            tui.ViewApp.run(title=vlt.name, vlt=vlt)
        except (err.InvalidEmail, err.InvalidPassword) as e:
            show_error(e)
        except err.UserExists as e:
            show_error(e)
    elif args.find:
        vlt.find_database()
    elif args.version:
        vlt.version()
    else:
        lpv = LoginPasswordValidator(args.login)
        try:
            vlt.get_user(lpv.login, lpv.password)

            if args.dump:
                vlt.dump_data(vlt.get_json_path())
            elif args.path:
                try:
                    vlt.load_data(args.path)
                    tui.ViewApp.run(title=vlt.name, vlt=vlt)
                except (err.FileNotFound, err.InvalidJSON) as e:
                    show_error(e)
            elif args.remove:
                vlt.remove_data()
            else:
                tui.ViewApp.run(title=vlt.name, vlt=vlt)

        except err.LoginFailed as e:
            show_error(e)


if __name__ == '__main__':
    print(__version__)
    print(__doc__)
    print(__file__)
    main()
