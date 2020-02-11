from datetime import datetime
from unittest import mock

import pytest

from misc.utils import get_month_year

test_data = [
    (datetime(year=2012, month=12, day=31), datetime(year=2012, month=11, day=2)),
    (datetime(year=2012, month=12, day=2), datetime(year=2012, month=11, day=2)),
    (datetime(year=2012, month=1, day=1), datetime(year=2011, month=12, day=1)),
    (datetime(year=2012, month=1, day=31), datetime(year=2011, month=12, day=31)),
]


@mock.patch("misc.utils.datetime")
@pytest.mark.parametrize("date, expected_date", test_data)
def test_get_month_year(mock_datetime, date, expected_date):
    mock_datetime.today.return_value = date
    month, year = get_month_year()
    assert month == expected_date.month
    assert year == expected_date.year
