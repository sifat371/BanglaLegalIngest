# Bangla Encoding Detection and Normalization

The encoding layer distinguishes Unicode Bangla, standard Bijoy-like text that can be offered to
bijoy2unicode, and legacy PDF-font glyph text that should not be converted automatically.

## Why the distinction matters

Real Bangladesh court PDFs can expose old font-encoded Bangla as strings containing Latin-1 and
extended glyph codes. That representation is not the same thing as ordinary Bijoy keyboard text.
A public Supreme Court smoke test showed that feeding such a line directly to bijoy2unicode can
produce plausible-looking but incorrect Unicode Bangla.

The module therefore treats these cases separately:

- unicode_bangla: already Unicode Bangla;
- bijoy: conservative standard-Bijoy conversion candidates;
- legacy_font_bangla: old PDF-font glyph text that is preserved with a warning;
- mixed: more than one Bangla representation is present;
- none: no supported Bangla representation was detected.

## Conversion policy

Standard Bijoy candidates may be converted line by line when conversion is enabled. Legacy
font-encoded lines are detected but preserved unchanged. This favors source fidelity over silently
producing corrupted Unicode.

The EncodingInfo diagnostics expose:

- unicode_bangla_chars;
- bijoy_candidate_lines;
- convertible_bijoy_lines;
- legacy_font_candidate_lines;
- normalization_applied;
- converted_lines;
- conversion_failures.

## Public API

~~~python
from legal_ingest import detect_encoding

info = detect_encoding(text)
print(info.kind)
print(info.convertible_bijoy_lines)
print(info.legacy_font_candidate_lines)
~~~

The ingestion pipeline applies the same detection automatically.

## Limitations

Detection remains heuristic. The module does not yet include a font-specific decoder for all
legacy Bangladesh PDF fonts. When legacy-font text is detected, the safe behavior is to preserve
the source glyph string and surface a diagnostic warning. A future benchmarked decoder can be
added behind an explicit strategy without changing this safety rule.
