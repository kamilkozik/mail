from datetime import datetime, timedelta


def get_month_year():
    date_today = datetime.today()
    month = (date_today - timedelta(days=27)).strftime("%m")
    year = date_today.strftime("%Y")
    return month, year
