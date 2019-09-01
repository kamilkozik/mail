from gdrive import fetch_files, flush
from mail import send_mail, init_o365
from utils import get_month_year


def main():
    flush()
    fetch_files()
    account = init_o365()
    month, year = get_month_year()
    subject = f"Dokumenty za {month}/{year}"
    body = f"""
Panie Pawle,

przesyłam dokumenty za okres {month}/{year}

Pozdrawiam
Kamil Kozik
"""
    send_mail(account, subject, body)


if __name__ == '__main__':
    main()
