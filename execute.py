from textwrap import dedent

from outlook.auth import init_o365
from storage.gdrive import fetch_files, flush
from outlook.mail import send_mail
from misc.utils import get_month_year


def main():
    flush()
    fetch_files()
    account = init_o365()
    month, year = get_month_year()
    subject = f"Dokumenty za {month}/{year}"
    body = dedent(
        f"""
            Panie Pawle,<br><br>
            przesyłam dokumenty za okers {month}/{year}<br><br>
            Pozdrawiam<br>
            Kamil Kozik
        """
    )
    send_mail(account, subject, body)


if __name__ == '__main__':
    main()
