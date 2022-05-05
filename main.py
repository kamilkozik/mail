import datetime
import enum
import pathlib
import tempfile
from typing import List

import click
import pytz
from googleapiclient.discovery import build

import settings
from files import FileMeta, GoogleFileMeta
from gdrive import GoogleOAuth, GoogleDrive
from ksbr import download_ksbr_invoice, get_jmr_file_name, JMR_DATE_PREFIX
from logger import get_logger
from mail import OutlookMail, O365Auth, send_mail, JMR_EMAIL_ADDRESS, JMR_SUBJECT
from pipelines import InvoicesPipeline

logger = get_logger(__name__)

KSBR_EMAIL_ADDRESS = "pawel.zdeb@ksbr.pl"
#KSBR_EMAIL_ADDRESS = "kamil.kozik@outlook.com"
KSBR_MAIL_BODY = """
Panie Pawle,

w załączniku przesyłam faktury za okres {date}.

Pozdrawiam,
Kamil Kozik
"""


class Companies(enum.Enum):
    KSBR = 'KSBR'
    JRM = 'JMR'


@click.group()
def main():
    pass


@main.command('upload_to_drive')
@click.argument('date_from', type=click.DateTime(formats=['%Y.%m.%d']))
@click.argument('date_to', type=click.DateTime(formats=['%Y.%m.%d']))
def upload_to_drive(date_from: datetime.datetime, date_to: datetime.datetime):
    date_to.replace(hour=23, minute=59, second=59)
    [year, month] = date_from.strftime('%Y,%m').split(',')

    # Download files from mail
    o365_auth = O365Auth()
    account = o365_auth.authenticate()
    mail = OutlookMail()
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        bought = tmp_dir / 'bought'
        sold = tmp_dir / 'sold'
        bought.mkdir()
        sold.mkdir()
        mail.download_invoices(
            account=account,
            since=date_from,
            till=date_to,
            bought_directory=bought,
            sold_directory=sold,
        )

        for f in sold.iterdir():
            print(f)
        for f in bought.iterdir():
            print(f)

        # Upload files to Google drive
        auth = GoogleOAuth()
        auth.authorize(token_path=settings.GOOGLE_TOKEN_PATH, credentials_path=settings.GOOGLE_CREDENTIALS_PATH)
        service = build('drive', 'v3', credentials=auth.credentials)
        google_drive_pipeline = InvoicesPipeline()

        google_drive = GoogleDrive(drive_service=service)
        target_path = pathlib.Path(settings.GOOGLE_INVOICES_BOUGHT_FOLDER) / year / month
        files = [FileMeta(p) for p in bought.iterdir() if not p.name.startswith('.')]

        google_drive_pipeline.run(files, target_path, google_drive)

        target_path = pathlib.Path(settings.GOOGLE_INVOICES_SOLD_FOLDER) / year / month
        files = [FileMeta(p) for p in sold.iterdir() if not p.name.startswith('.')]
        google_drive_pipeline.run(files, target_path, google_drive)


@main.command('send_invoices')
@click.argument('to', type=click.Choice([Companies.KSBR.value, Companies.JRM.value]))
@click.argument('date_from', type=click.DateTime(formats=['%Y.%m.%d']))
@click.argument('date_to', type=click.DateTime(formats=['%Y.%m.%d']))
def send_invoices(to: str, date_from: datetime.datetime, date_to: datetime.datetime):
    date_to.replace(hour=23, minute=59, second=59)

    if to == Companies.JRM.value:
        send_invoices_to_jmr(date_from, date_to)
    elif to == Companies.KSBR.value:
        send_invoices_to_ksbr(date_from, date_to)


def send_invoices_to_jmr(since: datetime.datetime, till: datetime.datetime):
    o365_auth = O365Auth()
    account = o365_auth.authenticate()
    mail = OutlookMail()
    since: datetime.datetime = pytz.utc.localize(since)
    till = pytz.utc.localize(till)
    folders = mail.get_folders(account)
    messages = mail.get_mails_with_attachments_by_folders(folders, since, till)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        download_ksbr_invoice(messages, tmp_dir, since)

        jmr_invoice_file_path = None
        for invoice_path in tmp_dir.iterdir():
            if get_jmr_file_name(since) == invoice_path.name:
                logger.info(f'Found invoice: {invoice_path.name}')
                jmr_invoice_file_path = invoice_path
                break

        if not jmr_invoice_file_path:
            logger.info('No invoice file found')
            return

        subject = JMR_SUBJECT.format(date=since.strftime(JMR_DATE_PREFIX))
        body = ''
        send_mail('kamil.kozik@outlook.com', [JMR_EMAIL_ADDRESS], subject, body, [jmr_invoice_file_path])


def send_invoices_to_ksbr(date_from: datetime.datetime, date_to: datetime.datetime):
    date_to.replace(hour=23, minute=59, second=59)
    [year, month] = date_from.strftime('%Y,%m').split(',')

    auth = GoogleOAuth()
    auth.authorize(token_path=settings.GOOGLE_TOKEN_PATH, credentials_path=settings.GOOGLE_CREDENTIALS_PATH)
    service = build('drive', 'v3', credentials=auth.credentials)
    google_drive_pipeline = InvoicesPipeline()

    google_drive = GoogleDrive(drive_service=service)
    google_bought_folder_path = pathlib.Path(settings.GOOGLE_INVOICES_BOUGHT_FOLDER) / year / month
    google_sold_folder_path = pathlib.Path(settings.GOOGLE_INVOICES_SOLD_FOLDER) / year / month

    bought_folder = google_drive_pipeline._get_folder_by_path(google_bought_folder_path, google_drive)
    sold_folder = google_drive_pipeline._get_folder_by_path(google_sold_folder_path, google_drive)
    files: List[GoogleFileMeta] = \
        list(google_drive.iterate_folder_content(bought_folder)) + \
        list(google_drive.iterate_folder_content(sold_folder))

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = pathlib.Path(temp_dir)
        for file in files:
            google_drive.download_file(file, temp_dir)

        subject = f'Faktury za {date_from.strftime("%m.%Y")}'
        body = KSBR_MAIL_BODY.format(date=date_from.strftime("%m.%Y"))
        send_mail(
            'kamil.kozik@outlook.com', [KSBR_EMAIL_ADDRESS], subject, body, list(temp_dir.iterdir())
        )


if __name__ == '__main__':
    main()
