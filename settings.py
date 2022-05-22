# vault.py

# about
AUTHOR = 'Alexander Veledzimovich'
EMAIL = 'veledz@gmail.com'
DESCRIPTION = 'Command line password manager'
LICENSE = 'MIT'
VERSION = 1.15
URL = 'https://github.com/schwarzbox/Vault'

# const
VAULT_TITLE = 'Vault'
VAULT_DB = 'vault_data'
# regexp
EMAIL_REGEXP = r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"
PASSWORD_REGEXP = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\_\-@$!%*#?&])[A-Za-z\d\_\-@$!#%*?&]{8,}$"
# colors
WHITE = 'white'
GREEN = 'green'
BRIGHT_GREEN = 'bright_green'
YELLOW = 'yellow'
RED = 'red'
GRAY = '#666666'
# icons
WHO = '👤'
REMOTE = '🌐'
LOCAL = '💾'
ABOUT = 'About'
KEY = '🔑'
COPY = '✏️'
DONE = '🔆'
CLOSE = '✕'
# art
TITLE_FONT = 'lockergnome'
# messages
INFO_MESSAGE = '[green]{}[/green]'
WARNING_MESSAGE = '[yellow]{}[/yellow]'
ERROR_MESSAGE = '[red]{}[/red]'
