import os.path
import os.path
import pickle

import google.auth.exceptions
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from settings import GOOGLE_DRIVE_SCOPES, GOOGLE_CREDENTIALS_PATH, GOOGLE_TOKEN_PICKLE_FILE_PATH
from utils import get_logger


logger = get_logger(__name__)


def get_credentials():
    credentials = None
    if os.path.exists(GOOGLE_TOKEN_PICKLE_FILE_PATH):
        with open(GOOGLE_TOKEN_PICKLE_FILE_PATH, 'rb') as token:
            credentials = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            refresh_credentials(credentials=credentials)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_PATH, GOOGLE_DRIVE_SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(GOOGLE_TOKEN_PICKLE_FILE_PATH, 'wb') as token:
            pickle.dump(credentials, token)

    return credentials


def refresh_credentials(credentials):
    try:
        credentials.refresh(Request())
    except google.auth.exceptions.RefreshError:
        logger.warning(f"RefreshError: removing {GOOGLE_TOKEN_PICKLE_FILE_PATH}")
        os.remove(GOOGLE_TOKEN_PICKLE_FILE_PATH)
        logger.warning(f"Refresh credentials")
        refresh_credentials(credentials)
