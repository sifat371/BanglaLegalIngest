"""Configuration models for the ingestion pipeline."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ExtractorName = Literal["auto", "pdfplumber", "pypdf", "docling"]


class PipelineConfig(BaseModel):
    """Runtime configuration shared by future extractor implementations."""

    model_config = ConfigDict(extra="forbid")

    extractor: ExtractorName = "auto"
    convert_bijoy: bool = True
    preserve_page_text: bool = True
    min_extracted_characters: int = Field(default=100, ge=0)
    output_encoding: Literal["utf-8"] = "utf-8"
