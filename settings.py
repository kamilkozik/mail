import os
from pathlib import Path


ROOT_DIR = Path(__file__).parent

GOOGLE_CREDENTIALS_PATH = ROOT_DIR / 'data' / 'credentials.json'
GOOGLE_TOKEN_PATH = ROOT_DIR / 'data' / 'token.json'
GOOGLE_INVOICES_BOUGHT_FOLDER = 'faktury kupna'
GOOGLE_INVOICES_SOLD_FOLDER = 'faktury sprzedaży'

O365_TOKEN_PATH = ROOT_DIR / 'data' / 'o365_token.txt'

EMAIL = {
    "EMAIL": str(os.environ.get("EMAIL", None)),
    "PASSWORD": str(os.environ.get("PASSWORD", None))
}

if EMAIL["EMAIL"] is None or EMAIL["PASSWORD"] is None:
    raise RuntimeError("Email credentials not provided")
