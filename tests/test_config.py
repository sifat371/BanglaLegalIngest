import pytest
from pydantic import ValidationError

from legal_ingest.config import PipelineConfig


def test_pipeline_config_defaults_are_safe() -> None:
    config = PipelineConfig()

    assert config.extractor == "auto"
    assert config.convert_bijoy is True
    assert config.preserve_page_text is True
    assert config.min_extracted_characters == 100


def test_pipeline_config_rejects_unknown_extractor() -> None:
    with pytest.raises(ValidationError):
        PipelineConfig(extractor="unknown")
