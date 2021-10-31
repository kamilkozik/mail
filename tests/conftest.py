import pytest


@pytest.fixture
def body() -> str:
    with open('./tests/data/download_invoice_page.html', 'r') as f:
        return f.read()
