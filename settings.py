import os
from pathlib import Path


# # # # # # # # # # #
#      GENERAL      #
# # # # # # # # # # #

ROOT_DIR = Path(".")
LOG_DIR = ROOT_DIR / "logs"
LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s %(message)s"
STATIC_PATH = ATTACHMENTS_PATH = ROOT_DIR / 'static'


# # # # # # # # # # #
#      OUTLOOK      #
# # # # # # # # # # #

O365_CLIENT_ID = os.getenv("O365_CLIENT_ID", None)
O365_CLIENT_SECRET = os.getenv("O365_CLIENT_SECRET", None)
O365_DEFAULT_SCOPES = ['basic', 'message_all']
O365_DEFAULT_TOKEN_PATH = ROOT_DIR / 'usr'
O365_DEFAULT_TOKEN_FILE_NAME = 'o365_token.txt'


# # # # # # # # # # #
#      GOOGLE       #
# # # # # # # # # # #

DEFAULT_RECIPIENT = 'kamil.kozik@outlook.com'
GOOGLE_DRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.activity.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]
GOOGLE_CREDENTIALS_PATH = ROOT_DIR / 'usr' / 'credentials.json'
GOOGLE_TOKEN_PICKLE_PATH = ROOT_DIR / 'usr'
GOOGLE_TOKEN_PICKLE_FILE_NAME = 'token.pickle'
GOOGLE_TOKEN_PICKLE_FILE_PATH = GOOGLE_TOKEN_PICKLE_PATH / GOOGLE_TOKEN_PICKLE_FILE_NAME
