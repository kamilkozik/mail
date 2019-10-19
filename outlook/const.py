import os

from settings.base import ROOT_PATH

O365_CLIENT_ID = os.getenv("O365_CLIENT_ID", None)
O365_CLIENT_SECRET = os.getenv("O365_CLIENT_SECRET", None)
O365_DEFAULT_SCOPES = ['basic', 'message_all']
O365_DEFAULT_TOKEN_PATH = os.path.join(ROOT_PATH, 'usr')
O365_DEFAULT_TOKEN_FILE_NAME = 'o365_token.txt'


DEFAULT_RECIPIENT = 'kamil.kozik@outlook.com'
