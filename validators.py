# vault.py

import re
import getpass


import errors as err
from settings import (
    EMAIL_REGEXP,
    PASSWORD_REGEXP
)


class LoginPasswordValidator:
    def __init__(self, login=None):
        self.login = login or input('Login? ')
        self.password = getpass.getpass('Password? ')

    def is_valid(self):
        if not re.fullmatch(EMAIL_REGEXP, self.login):
            raise err.InvalidEmail()
        if not re.fullmatch(PASSWORD_REGEXP, self.password):
            raise err.InvalidPassword()
