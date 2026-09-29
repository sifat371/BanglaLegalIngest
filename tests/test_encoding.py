from legal_ingest.encoding.detector import (
    detect_encoding,
    is_bijoy_line,
    is_legacy_font_line,
)
from legal_ingest.encoding.normalizer import (
    BanglaEncodingNormalizer,
    process_extracted_content,
)
from legal_ingest.schemas import EncodingKind, ExtractedContent, PageContent


class FakeConverter:
    def convertBijoyToUnicode(self, line: str) -> str:
        return f"বাংলা::{line}"


class FailingConverter:
    def convertBijoyToUnicode(self, _line: str) -> str:
        raise ValueError("synthetic conversion failure")


def test_detects_plain_english_as_none() -> None:
    info = detect_encoding("Supreme Court of Bangladesh\nCriminal Appeal No. 12 of 2024")

    assert info.kind == EncodingKind.NONE
    assert info.has_bangla is False
    assert info.unicode_bangla_chars == 0
    assert info.bijoy_candidate_lines == 0


def test_detects_unicode_bangla_without_conversion_candidate() -> None:
    info = detect_encoding("বাংলাদেশ সুপ্রিম কোর্ট")

    assert info.kind == EncodingKind.UNICODE_BANGLA
    assert info.has_bangla is True
    assert info.unicode_bangla_chars > 0
    assert info.bijoy_candidate_lines == 0


def test_detects_bijoy_candidate_line_conservatively() -> None:
    text = "Avwg AvBb ‡K †"
    info = detect_encoding(text)

    assert is_bijoy_line(text) is True
    assert info.kind == EncodingKind.BIJOY
    assert info.convertible_bijoy_lines == 1
    assert info.legacy_font_candidate_lines == 0


def test_detects_legacy_pdf_font_without_marking_it_convertible() -> None:
    text = "A¡¢j A¡j¡l Ù»£ p¡mj¡­L ¢h­u Ll¡l"
    info = detect_encoding(text)

    assert is_legacy_font_line(text) is True
    assert is_bijoy_line(text) is False
    assert info.kind == EncodingKind.LEGACY_FONT
    assert info.convertible_bijoy_lines == 0
    assert info.legacy_font_candidate_lines == 1


def test_detects_mixed_unicode_and_bijoy() -> None:
    info = detect_encoding("বাংলাদেশ\nAvwg AvBb ‡K †")

    assert info.kind == EncodingKind.MIXED
    assert info.has_bangla is True


def test_single_ascii_pattern_does_not_trigger_conversion() -> None:
    assert is_bijoy_line("A legal note containing Avwg as an isolated token.") is False


def test_normalizer_converts_only_candidate_lines() -> None:
    text = "English line\nAvwg AvBb ‡K †\nAnother English line"
    normalizer = BanglaEncodingNormalizer(converter=FakeConverter())

    result = normalizer.normalize_text(text)

    assert result.converted_lines == 1
    assert result.failed_lines == 0
    assert result.text.splitlines()[0] == "English line"
    assert result.text.splitlines()[1].startswith("বাংলা::")
    assert result.text.splitlines()[2] == "Another English line"


def test_normalizer_preserves_failed_candidate_line() -> None:
    line = "Avwg AvBb ‡K †"
    normalizer = BanglaEncodingNormalizer(converter=FailingConverter())

    result = normalizer.normalize_text(line)

    assert result.text == line
    assert result.converted_lines == 0
    assert result.failed_lines == 1
    assert result.warnings


def test_process_extracted_content_preserves_page_provenance() -> None:
    content = ExtractedContent(
        pages=[
            PageContent(page_number=1, text="English"),
            PageContent(page_number=2, text="Avwg AvBb ‡K †"),
        ],
        text="English\n\nAvwg AvBb ‡K †",
    )

    normalized, info = process_extracted_content(
        content,
        convert_bijoy=True,
        normalizer=BanglaEncodingNormalizer(converter=FakeConverter()),
    )

    assert [page.page_number for page in normalized.pages] == [1, 2]
    assert normalized.pages[0].text == "English"
    assert normalized.pages[1].text.startswith("বাংলা::")
    assert info.kind == EncodingKind.BIJOY
    assert info.normalization_applied is True
    assert info.converted_lines == 1


def test_process_preserves_unsafe_legacy_font_text() -> None:
    original = "A¡¢j A¡j¡l Ù»£ p¡mj¡­L ¢h­u Ll¡l"
    content = ExtractedContent(
        pages=[PageContent(page_number=1, text=original)],
        text=original,
    )

    normalized, info = process_extracted_content(content, convert_bijoy=True)

    assert normalized.text == original
    assert normalized.pages[0].text == original
    assert info.kind == EncodingKind.LEGACY_FONT
    assert info.normalization_applied is False
    assert info.converted_lines == 0
    assert any("Legacy font-encoded" in warning for warning in normalized.warnings)


def test_process_extracted_content_can_detect_without_converting() -> None:
    original = "Avwg AvBb ‡K †"
    content = ExtractedContent(
        pages=[PageContent(page_number=1, text=original)],
        text=original,
    )

    normalized, info = process_extracted_content(content, convert_bijoy=False)

    assert normalized.text == original
    assert info.kind == EncodingKind.BIJOY
    assert info.normalization_applied is False
