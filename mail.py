import os

from O365 import Account, MSOffice365Protocol

from consts import ATTACHMENTS_PATH, DEFAULT_RECIPIENT, o365_credentials, O365_DEFAULT_SCOPES, O365_DEFAULT_TOKEN_PATH


def init_o365(
        protocol: MSOffice365Protocol = MSOffice365Protocol(),
        credentials: tuple = o365_credentials,
        token_path: str = O365_DEFAULT_TOKEN_PATH
):
    account = Account(credentials, protocol=protocol)

    if not account.is_authenticated and os.path.exists(token_path):
        account.con.refresh_token()
    elif not account.is_authenticated:
        account.authenticate(scopes=O365_DEFAULT_SCOPES, grant_type='client_credentials')
    return account


def compose_mail(
        account:    Account,
        to:         str = 'kamil.kozik.kzq@gmail.com',
        subject:    str = None,
        body:       str = None,
        attachments: list = None
):
    """

    :param account:
    :param to:
    :param subject:
    :param body:
    :param attachments:
    :return:
    """
    mail = account.new_message()
    mail.to.add(to)
    if subject:
        mail.subject = subject
    if body:
        mail.body = body
    if attachments:
        for a in attachments:
            mail.attachments.add(a)
    return mail


def gather_files():
    return [os.path.join(ATTACHMENTS_PATH, path) for path in os.listdir(ATTACHMENTS_PATH)]


def send_mail(
        account: Account,
        subject: str,
        body: str,
        to: str = DEFAULT_RECIPIENT,
        attachments: list = None
):
    if not attachments:
        attachments = gather_files()
    message = compose_mail(account, to, subject, body, attachments)
    message.send()
