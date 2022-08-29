# vault.py

# about
AUTHOR = 'Alexander Veledzimovich'
EMAIL = 'veledz@gmail.com'
DESCRIPTION = 'Command line password manager'
LICENSE = 'MIT'
VERSION = 1.2
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
DARK_GREEN = 'dark_green'
BRIGHT_GREEN = 'bright_green'
YELLOW = 'yellow'
RED = '#FF004B'
GRAY = '#666666'
BLUE = '#3B00FF'

# icons
CLOSE = '✕'
WHO = 'Who'
DUMP = 'Dump'
LOAD = 'Load'
SOURCE = 'Source'
EDIT = 'Edit'
FIND = 'Find'
REMOTE = '🌐'
LOCAL = '🟢'
UPDATE = '🟡'
INFO = 'Info'
KEY = '🔑'
COPY = '✏️'
DONE = '🔆'
ADD = '✚'
CLEAR = '−'

# labels
DEFAULT_LABEL = 'Default'
OK_LABEL = 'OK'
CANCEL_LABEL = 'CANCEL'
PASTE_LABEL = 'CTRL+V'
NOTIFICATION_LABEL = 'Notification'
ERROR_LABEL = 'Error'
WARNING_LABEL = 'Warning'
ADD_LABEL = 'Add'
UPDATE_LABEL = 'Update'

# TIMERS
ACTION_TIME = 1
FAST_ACTION_TIME = 0.2
EMPTY_JSON_TIME = 3
NOTIFICATION_TIME = 2

# styles
LOCAL_STYLE = f'{WHITE} on {DARK_GREEN}'
REMOTE_STYLE = f'{WHITE} on {BLUE}'
UPDATE_STYLE = f'{WHITE} on {YELLOW}'

# art font
TITLE_FONT = 'lockergnome'

# messages
NOTIFICATION_MESSAGE = '[' + GREEN + ']{}[/' + GREEN + ']'
WARNING_MESSAGE = '[' + YELLOW + ']{}[/' + YELLOW + ']'
ERROR_MESSAGE = '[' + RED + ']{}[/' + RED + ']'
