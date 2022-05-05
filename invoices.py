import pathlib
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

from classifiers import FileClassifier, PDF


class InvoiceDetector:
    NIP = '7151889251'

    def is_invoice(self, file_path: pathlib.Path, classifier: FileClassifier) -> bool:
        if not classifier.is_of_type(file_path, PDF):
            return False

        content = self._get_text_from_pdf(file_path)
        cleaned = self._clean_content(content)
        return self.NIP in cleaned

    @staticmethod
    def _clean_content(content: str) -> str:
        characters = [(" ", ""), ("-", "")]
        for old, new in characters:
            content = content.replace(old, new)
        return content

    # Following static method is stolen from:
    # https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
    @staticmethod
    def _get_text_from_pdf(file_path: pathlib.Path) -> str:
        resource_manager = PDFResourceManager()
        string_io = StringIO()
        la_params = LAParams()
        device = TextConverter(resource_manager, string_io, laparams=la_params)
        fp = open(file_path, 'rb')
        interpreter = PDFPageInterpreter(resource_manager, device)
        password = ""
        max_pages = 0
        caching = True
        page_numbers = set()
        pages = PDFPage.get_pages(
            fp, page_numbers, maxpages=max_pages, password=password, caching=caching, check_extractable=True
        )
        for page in pages:
            interpreter.process_page(page)

        text = string_io.getvalue()
        fp.close()
        device.close()
        string_io.close()

        return text
