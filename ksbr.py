import datetime
import json
import pathlib
import re
from typing import List, Optional, Generator

import O365.message
import bs4
import requests

import logger

KSBR_EMAIL = 'wiadomosctaxxo@taxxo.pl'
ANCHOR_TAG_TEXT = 'Kliknij tutaj, aby pobrać fakturę'
EXPECTED_SUBJECT_TEXT = 'Firma Kamil Kozik wystawiła'
JMR_FILE_NAME = '{date}_kozik.pdf'
JMR_DATE_PREFIX = '%Y%m'


logger = logger.get_logger(__name__)


def find_ksbr_message(messages: List[O365.message.Message]) -> Generator[O365.message.Message, None, None]:
    for message in messages:
        if (
            message.sender.address.lower() == KSBR_EMAIL.lower()
            and EXPECTED_SUBJECT_TEXT.lower() in message.subject.lower()
        ):
            yield message


def get_download_invoice_link(message: O365.message.Message) -> str:
    soup: bs4.BeautifulSoup = message.get_body_soup()
    anchor = soup.find('a', text=ANCHOR_TAG_TEXT)
    return anchor.attrs['href']


def download_page(url: str) -> str:
    response = requests.get(url)
    return response.text


def save_invoice(body: str, path: pathlib.Path, date: datetime.datetime):
    soup = bs4.BeautifulSoup(body, 'lxml')
    customer = get_customer_name(soup)
    file_name = get_file_name_by_customer(customer, date)
    url = parse_invoice_download_url(soup)
    logger.info(f'Downloading KSBR')
    response = requests.get(url)
    with open(path / file_name, 'wb') as f:
        f.write(response.content)


def parse_invoice_download_url(soup: bs4.BeautifulSoup):
    src = soup.find('iframe').attrs['src']
    src = src.replace('HTML', 'PDF').replace('&amp;', '&')
    return src


def download_ksbr_invoice(messages: List[O365.message.Message], path: pathlib.Path, date: datetime.datetime):
    for message in find_ksbr_message(messages):
        url = get_download_invoice_link(message)
        text = download_page(url)
        save_invoice(text, path, date)


def get_customer_name(soup: bs4.BeautifulSoup) -> str:
    el = soup.find('div', attrs={'data-buyer-data': re.compile(".*")})
    return json.loads(el.attrs['data-buyer-data'])['CustomerName']


def get_file_name_by_customer(customer: str, date: datetime.datetime) -> str:
    if customer == 'JMR Technologies Sp. z o.o.':
        file_name = get_jmr_file_name(date)
    else:
        file_name = f'{customer}.pdf'

    return file_name


def get_jmr_file_name(date: datetime.datetime) -> str:
    return JMR_FILE_NAME.format(date=date.strftime(JMR_DATE_PREFIX))
