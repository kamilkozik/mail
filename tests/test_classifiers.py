import pathlib

import pytest

from classifiers import MagicClassifier, PDF


@pytest.mark.parametrize(
    "file_path,is_pdf",
    [
        (pathlib.Path('./tests/data/test_files/types/invoice.pdf'), True),
        (pathlib.Path('./tests/data/test_files/types/its_pdf_but_changed_extension.xlsx'), True),
        (pathlib.Path('./tests/data/test_files/types/viking.png'), False),
        (pathlib.Path('./tests/data/test_files/types/eagle_ai_deployments.txt'), False),
    ]
)
def test_pdf_classifier(file_path: pathlib.Path, is_pdf: bool):
    classifier = MagicClassifier()
    assert is_pdf == classifier.is_of_type(file_path, PDF)
