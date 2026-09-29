from legal_ingest.quality import assess_extraction_quality
from legal_ingest.schemas import ExtractedContent, PageContent


def test_quality_rewards_non_empty_clean_pages() -> None:
    good = ExtractedContent(
        pages=[
            PageContent(page_number=1, text="A" * 700),
            PageContent(page_number=2, text="B" * 700),
        ],
        text=("A" * 700) + "\n\n" + ("B" * 700),
    )
    poor = ExtractedContent(
        pages=[
            PageContent(page_number=1, text=""),
            PageContent(page_number=2, text="x\ufffd\x00"),
        ],
        text="x\ufffd\x00",
    )

    good_report = assess_extraction_quality(good)
    poor_report = assess_extraction_quality(poor)

    assert good_report.usability_score > poor_report.usability_score
    assert good_report.non_empty_page_ratio == 1.0
    assert poor_report.replacement_char_ratio > 0
    assert poor_report.control_char_ratio > 0


def test_quality_handles_empty_content() -> None:
    report = assess_extraction_quality(ExtractedContent())

    assert report.page_count == 0
    assert report.usability_score == 0.0
