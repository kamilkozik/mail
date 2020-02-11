from datetime import datetime, timedelta


def get_month_year():
    date_today = datetime.today()
    date_today = date_today - timedelta(days=date_today.day)
    month = date_today.month
    year = date_today.year
    return month, year
