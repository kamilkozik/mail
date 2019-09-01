import os

ROOT_PATH = os.getcwd()
STATIC_PATH = os.path.join(ROOT_PATH, 'files')
ATTACHMENTS_PATH = STATIC_PATH

O365_CLIENT_ID = os.getenv("O365_CLIENT_ID", None)
O365_CLIENT_SECRET = os.getenv("O365_CLIENT_SECRET", None)
O365_DEFAULT_SCOPES = ['basic', 'message_all']
O365_DEFAULT_TOKEN_PATH = os.path.join(ROOT_PATH, 'o365_token.txt')


DEFAULT_RECIPIENT = 'kamil.kozik@outlook.com'


GOOGLE_DRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.activity.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]


@property
def o365_credentials():
    return O365_CLIENT_ID, O365_CLIENT_SECRET

