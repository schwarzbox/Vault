# vault.py

from rich import print

from settings import (
    ERROR_MESSAGE,
    INFO_MESSAGE,
    WARNING_MESSAGE
)


class VaultException(Exception):
    def __str__(self):
        return self.message


class UserExists(VaultException):
    message = 'User exists'


class LoginFailed(VaultException):
    message = 'User unknown'


class DataBaseNotFound(VaultException):
    def __init__(self, path, message='Data Base not found:'):
        self.message = f'{message} {path}'
        super().__init__(self.message)


class FileNotFound(VaultException):
    def __init__(self, path, message='File not found:'):
        self.message = f'{message} {path}'
        super().__init__(self.message)


class InvalidJSON(VaultException):
    def __init__(self, path, message='Invalid JSON:'):
        self.message = f'{message} {path}'
        super().__init__(self.message)


class InvalidDataFormat(VaultException):
    def __init__(self, path, message='Invalid Data Format:'):
        self.message = f'{message} {path}'
        super().__init__(self.message)


class InvalidURL(VaultException):
    def __init__(self, path, message='Invalid URL:'):
        self.message = f'{message} {path}'
        super().__init__(self.message)


class InvalidEmail(VaultException):
    message = 'Use valid email'


class InvalidPassword(VaultException):
    help_messages = [
        '- Minimum 8 characters',
        '- The alphabets must be between [a-z]',
        '- At least one alphabet should be of Upper Case [A-Z]',
        '- At least 1 number or digit between [0-9]',
        '- At least 1 character from [_-@$!%*#?&]'
    ]
    help_message = '\n'.join(help_messages)
    message = f'Use strong password:\n{help_message}'


def show_info(message):
    print(INFO_MESSAGE.format(message))


def show_warning(message):
    print(WARNING_MESSAGE.format(message))


def show_error(message):
    print(ERROR_MESSAGE.format(message))
