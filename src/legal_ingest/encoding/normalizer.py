"""Conservative line-level Bijoy-to-Unicode normalization."""

from dataclasses import dataclass
from typing import Any

from legal_ingest.encoding.detector import detect_encoding, is_bijoy_line
from legal_ingest.schemas import EncodingInfo, ExtractedContent, PageContent


@dataclass(slots=True)
class TextNormalizationResult:
    """Result of normalizing one text payload."""

    text: str
    converted_lines: int = 0
    failed_lines: int = 0
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


def _load_bijoy_converter() -> Any:
    """Load the optional converter only when a candidate line actually needs it."""

    try:
        from bijoy2unicode.converter import Unicode
    except ImportError:
        return None
    return Unicode()


class BanglaEncodingNormalizer:
    """Normalize only lines that are safe standard-Bijoy candidates."""

    def __init__(self, converter: Any | None = None) -> None:
        self._converter = converter
        self._converter_loaded = converter is not None

    def _get_converter(self) -> Any:
        if not self._converter_loaded:
            self._converter = _load_bijoy_converter()
            self._converter_loaded = True
        return self._converter

    def normalize_text(self, text: str, *, enabled: bool = True) -> TextNormalizationResult:
        """Convert standard-Bijoy candidate lines and preserve every other line."""

        if not enabled or not text:
            return TextNormalizationResult(text=text)

        candidate_lines = [line for line in text.splitlines() if is_bijoy_line(line)]
        if not candidate_lines:
            return TextNormalizationResult(text=text)

        converter = self._get_converter()
        if converter is None:
            return TextNormalizationResult(
                text=text,
                warnings=[
                    "Standard Bijoy-like text was detected but bijoy2unicode is not installed; "
                    "text was preserved unchanged."
                ],
            )

        converted_lines = 0
        failed_lines = 0
        output_lines: list[str] = []

        for line in text.split("\n"):
            if not is_bijoy_line(line):
                output_lines.append(line)
                continue

            try:
                converted = converter.convertBijoyToUnicode(line)
            except Exception:
                output_lines.append(line)
                failed_lines += 1
                continue

            output_lines.append(converted)
            converted_lines += 1

        warnings: list[str] = []
        if failed_lines:
            warnings.append(
                f"Bijoy conversion failed for {failed_lines} candidate line(s); "
                "their original text was preserved."
            )

        return TextNormalizationResult(
            text="\n".join(output_lines),
            converted_lines=converted_lines,
            failed_lines=failed_lines,
            warnings=warnings,
        )


def _combine_pages(pages: list[PageContent]) -> str:
    return "\n\n".join(page.text.strip() for page in pages if page.text.strip())


def _deduplicate(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def process_extracted_content(
    content: ExtractedContent,
    *,
    convert_bijoy: bool,
    normalizer: BanglaEncodingNormalizer | None = None,
) -> tuple[ExtractedContent, EncodingInfo]:
    """Detect source encoding and safely normalize standard Bijoy candidates."""

    encoding = detect_encoding(content.text)
    warnings = list(content.warnings)

    if convert_bijoy and encoding.legacy_font_candidate_lines:
        warnings.append(
            "Legacy font-encoded Bangla glyph text was detected in "
            f"{encoding.legacy_font_candidate_lines} line(s). Automatic conversion was skipped "
            "for those lines because bijoy2unicode is not reliable for this PDF-font encoding."
        )

    if not convert_bijoy or encoding.convertible_bijoy_lines == 0:
        if warnings == content.warnings:
            return content, encoding
        return (
            ExtractedContent(
                pages=content.pages,
                text=content.text,
                warnings=_deduplicate(warnings),
            ),
            encoding,
        )

    normalizer = normalizer or BanglaEncodingNormalizer()
    converted_lines = 0
    failed_lines = 0

    if content.pages:
        normalized_pages: list[PageContent] = []
        for page in content.pages:
            report = normalizer.normalize_text(page.text)
            normalized_pages.append(PageContent(page_number=page.page_number, text=report.text))
            converted_lines += report.converted_lines
            failed_lines += report.failed_lines
            warnings.extend(report.warnings or [])

        normalized_text = _combine_pages(normalized_pages)
    else:
        report = normalizer.normalize_text(content.text)
        normalized_pages = []
        normalized_text = report.text
        converted_lines = report.converted_lines
        failed_lines = report.failed_lines
        warnings.extend(report.warnings or [])

    updated_encoding = encoding.model_copy(
        update={
            "normalization_applied": converted_lines > 0,
            "converted_lines": converted_lines,
            "conversion_failures": failed_lines,
        }
    )

    return (
        ExtractedContent(
            pages=normalized_pages,
            text=normalized_text,
            warnings=_deduplicate(warnings),
        ),
        updated_encoding,
    )
