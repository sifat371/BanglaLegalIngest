from types import SimpleNamespace

from pypdf import PdfWriter

from legal_ingest.extractors.docling import DoclingExtractor
from legal_ingest.extractors.pdfplumber import PdfPlumberExtractor
from legal_ingest.extractors.pypdf import PyPDFExtractor


def make_blank_pdf(path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with path.open("wb") as handle:
        writer.write(handle)


def test_pypdf_preserves_page_identity(tmp_path) -> None:
    path = tmp_path / "blank.pdf"
    make_blank_pdf(path)

    result = PyPDFExtractor().extract(path)

    assert len(result.pages) == 1
    assert result.pages[0].page_number == 1
    assert result.pages[0].text == ""
    assert result.text == ""


def test_pdfplumber_preserves_page_identity(tmp_path) -> None:
    path = tmp_path / "blank.pdf"
    make_blank_pdf(path)

    result = PdfPlumberExtractor().extract(path)

    assert len(result.pages) == 1
    assert result.pages[0].page_number == 1
    assert result.pages[0].text == ""
    assert result.text == ""


def test_docling_uses_page_aware_export(tmp_path) -> None:
    path = tmp_path / "fake.pdf"
    path.write_bytes(b"not-used-by-injected-converter")

    class FakeDocument:
        pages = {1: object(), 2: object()}

        def export_to_markdown(self, *, page_no):
            return {1: "# Page one", 2: "Page two"}[page_no]

    class FakeConverter:
        def convert(self, _path):
            return SimpleNamespace(document=FakeDocument())

    result = DoclingExtractor(converter_factory=FakeConverter).extract(path)

    assert [page.page_number for page in result.pages] == [1, 2]
    assert result.pages[0].text == "# Page one"
    assert result.text == "# Page one\n\nPage two"
