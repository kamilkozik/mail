import datetime
import pathlib

import click
from googleapiclient.discovery import build

import settings
from files import FileMeta
from gdrive import GoogleOAuth, GoogleDrive
from mail import OutlookMail, O365Auth
from pipelines import InvoicesPipeline


@click.command()
@click.argument('date_from', type=click.DateTime(formats=['%Y.%m.%d']))
@click.argument('date_to', type=click.DateTime(formats=['%Y.%m.%d']))
def main(date_from: datetime.datetime, date_to: datetime.datetime):
    date_to.replace(hour=23, minute=59, second=59)
    [year, month] = date_from.strftime('%Y,%m').split(',')

    # Download files from mail
    o365_auth = O365Auth()
    account = o365_auth.authenticate()
    mail = OutlookMail()
    mail.download_invoices(
        account=account,
        since=date_from,
        till=date_to,
    )

    # Upload files to Google drive
    auth = GoogleOAuth()
    auth.authorize(token_path=settings.GOOGLE_TOKEN_PATH, credentials_path=settings.GOOGLE_CREDENTIALS_PATH)
    service = build('drive', 'v3', credentials=auth.credentials)
    google_drive_pipeline = InvoicesPipeline()

    google_drive = GoogleDrive(drive_service=service)
    target_path = pathlib.Path(settings.GOOGLE_INVOICES_BOUGHT_FOLDER) / year / month
    files = [FileMeta(p) for p in settings.INVOICES_TARGET_BOUGHT_PATH.iterdir() if not p.name.startswith('.')]

    google_drive_pipeline.run(files, target_path, google_drive)

    target_path = pathlib.Path(settings.GOOGLE_INVOICES_SOLD_FOLDER) / year / month
    files = [FileMeta(p) for p in settings.INVOICES_TARGET_SOLD_PATH.iterdir() if not p.name.startswith('.')]
    google_drive_pipeline.run(files, target_path, google_drive)


if __name__ == '__main__':
    main()
