# vault.py

from appdirs import user_data_dir

VAULT_TITLE = 'Vault'
VAULT_DIR = user_data_dir(f'{VAULT_TITLE}DB', 'Alex Veledzimovich')
VAULT_DB = f'{VAULT_DIR}/vault_data'
# regexp
EMAIL_REGEXP = r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"
PASSWORD_REGEXP = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\_\-@$!%*#?&])[A-Za-z\d\_\-@$!#%*?&]{8,}$"
# colors
GREEN = 'green'
BRIGHT_GREEN = 'bright_green'
YELLOW = 'yellow'
GRAY = '#666666'
