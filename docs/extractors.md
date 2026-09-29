# Extractor Backends

Stage 2 provides three interchangeable page-aware extractors.

## pdfplumber

`PdfPlumberExtractor` is the primary lightweight backend. It extracts every source page
independently and records blank-page warnings instead of silently dropping pages.

Install:

```bash
pip install -e ".[manual]"
```

## pypdf

`PyPDFExtractor` is the lightweight fallback. It uses the same `ExtractedContent` contract as
pdfplumber and preserves the same one-based page numbering.

## Docling

`DoclingExtractor` is optional and imported lazily:

```bash
pip install -e ".[docling]"
```

Stage 2 requires Docling to expose page metadata and page-aware Markdown export. If an installed
Docling version cannot do that, the extractor fails explicitly rather than flattening the document
and losing source provenance.

## Auto mode

`PipelineConfig(extractor="auto")` currently tries pdfplumber first and uses pypdf only when the
primary backend fails or produces fewer characters than `min_extracted_characters`.

Automatic Docling routing is intentionally deferred until the quality-routing stage.
