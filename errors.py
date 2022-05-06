# vault.py

class VaultException(Exception):
    def __str__(self):
        return self.message


class UserExists(VaultException):
    message = 'User exists'


class LoginFailed(VaultException):
    message = 'User unknown'


class FileNotFound(VaultException):
    def __init__(self, path, message='File not found:'):
        self.message = f'{message} {path}'
        super().__init__(self.message)


class InvalidJSON(VaultException):
    def __init__(self, path, message='Invalid JSON:'):
        self.message = f'{message} {path}'
        super().__init__(self.message)


class InvalidEmail(VaultException):
    message = 'Please use valid email'


class InvalidPassword(VaultException):
    message = 'Please use strong password'
