import datetime
import pathlib
from typing import List, Optional

import O365.message
import bs4
import requests

KSBR_EMAIL = 'wiadomosctaxxo@taxxo.pl'
ANCHOR_TAG_TEXT = 'Kliknij tutaj, aby pobrać fakturę'
EXPECTED_SUBJECT_TEXT = 'Firma Kamil Kozik wystawiła'


def find_ksbr_message(messages: List[O365.message.Message]) -> Optional[O365.message.Message]:
    for message in messages:
        if (
            message.sender.address.lower() == KSBR_EMAIL.lower()
            and EXPECTED_SUBJECT_TEXT.lower() in message.subject.lower()
        ):
            return message


def get_download_invoice_link(message: O365.message.Message) -> str:
    soup: bs4.BeautifulSoup = message.get_body_soup()
    anchor = soup.find('a', text=ANCHOR_TAG_TEXT)
    return anchor.attrs['href']


def download_page(url: str) -> str:
    response = requests.get(url)
    return response.text


def save_invoice(body: str, path: pathlib.Path, date: datetime.datetime):
    url = parse_invoice_download_url(body)
    response = requests.get(url)
    file_prefix = date.strftime('%Y%m')
    with open(path / f'{file_prefix}_kozik.pdf', 'wb') as f:
        f.write(response.content)


def parse_invoice_download_url(body: str):
    soup = bs4.BeautifulSoup(body, 'lxml')
    src = soup.find('iframe').attrs['src']
    src = src.replace('HTML', 'PDF').replace('&amp;', '&')
    return src


def download_ksbr_invoice(messages: List[O365.message.Message], path: pathlib.Path, date: datetime.datetime):
    message = find_ksbr_message(messages)
    if message:
        url = get_download_invoice_link(message)
        text = download_page(url)
        save_invoice(text, path, date)
