import datetime
import pathlib
from typing import List

import O365.mailbox
import O365.message
import O365.utils
import pytz
from O365 import FileSystemTokenBackend

from ksbr import download_ksbr_invoice
from logger import get_logger
from settings import O365_TOKEN_PATH, INVOICES_TARGET_BOUGHT_PATH, \
    INVOICES_TARGET_SOLD_PATH

SECRET = 'N9R7Q~4Cus_2DemW8d1hflaiCsIoBWX7hGAsk'
CLIENT = 'd9168cad-34e2-431a-adfd-ab617b4568f6'
SCOPES = ['basic', 'message_all']
FOLDERS = ['Volkswagen', 'Orange', 'Leaselink - Laptop', 'Ksbr', 'BNP Paribas']
RECEIVED_DATE_TIME = datetime.datetime(year=2021, month=10, day=1, tzinfo=pytz.UTC)


class AuthenticationFailure(Exception):
    pass


class O365Auth:
    @staticmethod
    def _get_account(client: str, secret: str) -> O365.Account:
        params = {}
        if O365_TOKEN_PATH.exists():
            params = {
                'token_backend': FileSystemTokenBackend(
                    token_path=str(O365_TOKEN_PATH.parent),
                    token_filename=O365_TOKEN_PATH.name
                )
            }
        return O365.Account((client, secret), **params)

    def authenticate(self):
        account = self._get_account(CLIENT, SECRET)
        if not account.is_authenticated:
            success = account.authenticate(scopes=SCOPES)
            if not success:
                raise AuthenticationFailure()
        return account


class OutlookMail:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def get_folders(self, account: O365.Account) -> List[O365.mailbox.Folder]:
        mailbox = self.get_mailbox(account)
        query = self.get_folders_query(mailbox)
        return mailbox.get_folders(query=query)

    @staticmethod
    def get_mailbox(account: O365.Account) -> O365.mailbox.MailBox:
        return account.mailbox()

    @staticmethod
    def get_folders_query(mailbox: O365.mailbox.MailBox) -> O365.utils.Query:
        query = mailbox.new_query()
        query.on_attribute('displayName')
        for index, folder_name in enumerate(FOLDERS):
            if index == 0:
                query.contains(folder_name)
            else:
                query.chain('or').contains(folder_name)
        return query

    @staticmethod
    def get_mails_with_attachments_by_folders(
        folders: List[O365.mailbox.Folder],
        since: datetime.datetime,
        till: datetime.datetime,
    ) -> List[O365.message.Message]:
        messages = []
        for folder in folders:
            query = folder.new_query('received_date_time')\
                .greater_equal(since)\
                .chain('and')\
                .on_attribute('received_date_time')\
                .less_equal(till)

            messages.extend(list(folder.get_messages(query=query)))
        return messages

    def download_attachments(self, message: O365.message.Message, path: pathlib.Path):
        message.attachments.download_attachments()
        for attachment in message.attachments:
            if attachment.name.split('.')[-1].lower() in ['pdf']:
                self.logger.info(f'Downloading {attachment}')
                attachment.save(location=str(path))

    def download_invoices(
            self,
            account,
            since: datetime.datetime,
            till: datetime.datetime
    ):
        since = pytz.utc.localize(since)
        till = pytz.utc.localize(till)
        folders = self.get_folders(account)
        messages = self.get_mails_with_attachments_by_folders(folders, since, till)

        for message in messages:
            self.download_attachments(message, INVOICES_TARGET_BOUGHT_PATH)

        download_ksbr_invoice(messages, INVOICES_TARGET_SOLD_PATH, since)
