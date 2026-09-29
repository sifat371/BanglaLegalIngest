"""Configuration models for the ingestion pipeline."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ExtractorName = Literal["auto", "pdfplumber", "pypdf", "docling"]


class PipelineConfig(BaseModel):
    """Runtime configuration shared by the ingestion stages."""

    model_config = ConfigDict(extra="forbid")

    extractor: ExtractorName = "auto"
    convert_bijoy: bool = True
    parse_metadata: bool = True
    preserve_page_text: bool = True
    min_extracted_characters: int = Field(default=100, ge=0)
    min_quality_score: float = Field(default=0.65, ge=0.0, le=1.0)
    auto_docling_fallback: bool = False
    output_encoding: Literal["utf-8"] = "utf-8"
