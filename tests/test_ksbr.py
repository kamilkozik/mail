import ksbr


def test_parse_invoice_page(body):
    expected = "https://platforma2.taxxo.pl/InvoicesPreview/File.pdf?IDCustomer=21359&GUID=93a34bd8-9840-4085-9b17-" \
               "13213bfd04d9&Format=PDF&DuplicateDate=&refresh=False&ServerDistributionKey=240"
    url = ksbr.parse_invoice_download_url(body)
    assert url == expected
