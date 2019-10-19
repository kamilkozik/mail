import os
from typing import Callable

from O365 import MSOffice365Protocol, Account, FileSystemTokenBackend

from outlook.const import O365_DEFAULT_TOKEN_PATH, O365_DEFAULT_SCOPES, O365_DEFAULT_TOKEN_FILE_NAME
from outlook.utils import o365_credentials


def init_o365(
        protocol: MSOffice365Protocol = MSOffice365Protocol(),
        credentials: Callable = o365_credentials,
        token_path: str = O365_DEFAULT_TOKEN_PATH
):
    token_backend = FileSystemTokenBackend(token_path=token_path)
    account = Account(credentials(), protocol=protocol, token_backend=token_backend)

    if not account.is_authenticated and os.path.exists(os.path.join(token_path, O365_DEFAULT_TOKEN_FILE_NAME)):
        account.con.refresh_token()
    elif not account.is_authenticated:
        account.authenticate(scopes=O365_DEFAULT_SCOPES, grant_type='client_credentials')
    return account
