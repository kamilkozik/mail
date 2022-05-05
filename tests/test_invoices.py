import pathlib

import pytest

from classifiers import PDF, MagicClassifier
from invoices import InvoiceDetector


@pytest.mark.parametrize(
    "file_path,company_invoice",
    [
        (pathlib.Path('./tests/data/test_files/invoices/1.pdf'), True),
        (pathlib.Path('./tests/data/test_files/invoices/2.pdf'), True),
        (pathlib.Path('./tests/data/test_files/invoices/3.PDF'), True),
        (pathlib.Path('./tests/data/test_files/invoices/4.pdf'), True),
        (pathlib.Path('./tests/data/test_files/invoices/not_a_company_invoice.pdf'), False),
    ]
)
def test_is_invoice(file_path: pathlib.Path, company_invoice: bool):
    detector = InvoiceDetector()
    assert company_invoice == detector.is_invoice(file_path, classifier=MagicClassifier())
