import os

from O365 import Account

from settings import ATTACHMENTS_PATH, DEFAULT_RECIPIENT


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


def send_mail(
        account: Account,
        subject: str,
        body: str,
        to: str = DEFAULT_RECIPIENT,
        attachments: list = None
):
    if not attachments:
        attachments = [ATTACHMENTS_PATH / path for path in os.listdir(ATTACHMENTS_PATH)]
    message = compose_mail(account, to, subject, body, attachments)
    message.send()
