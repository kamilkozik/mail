import os

from settings.base import ROOT_PATH

GOOGLE_DRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.activity.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]
GOOGLE_CREDENTIALS_PATH = os.path.join(ROOT_PATH, 'usr', 'credentials.json')
GOOGLE_TOKEN_PICKLE_PATH = os.path.join(ROOT_PATH, 'usr')
GOOGLE_TOKEN_PICKLE_FILE_NAME = 'token.pickle'
GOOGLE_TOKEN_PICKLE_FILE_PATH = os.path.join(GOOGLE_TOKEN_PICKLE_PATH, GOOGLE_TOKEN_PICKLE_FILE_NAME)
