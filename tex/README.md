# English and Spanish LaTeX editions

The current English edition contains the source front matter, introduction,
chapters 1–8, their figures, table and notes, the conclusion and acknowledgements,
and a regenerated index. See
`../PLAN.md` for the complete workflow.

The Spanish edition contains chapters 1–8, their unchanged figures, translated
captions, equations, the comparison table, sixty-two notes, and an index. Translation follows
`../AGENTS.md`, reusing Anahi's prose where accurate against the English.
It also includes the introduction, conclusion and acknowledgements.
The approved Spanish title, subtitle and translation credit, plus the translated
dedication and epigraph, are in `spanish/frontmatter.tex`. Word export remains deferred.

## Spanish build

```sh
make -C tex spanish
make -C tex spanish-chapter01 spanish-chapter02
make -C tex spanish-chapter03
make -C tex check-spanish
make -C tex check-chapter03
make -C tex spanish-chapter04
make -C tex check-chapter04
make -C tex spanish-chapter05
make -C tex check-chapter05
make -C tex spanish-chapter06
make -C tex check-chapter06
make -C tex spanish-chapter07
make -C tex check-chapter07
make -C tex spanish-chapter08
make -C tex check-chapter08
make -C tex spanish-supporting
make -C tex check-supporting
```

The combined PDF is `tex/build/spanish/main.pdf`. Individual PDFs are
`tex/build/spanish-chapter01/chapter01.pdf` and
`tex/build/spanish-chapter02/chapter02.pdf`. As below, run from the repository
root. Spanish uses the shared preamble with Spanish hyphenation and headings.

Concise editorial summaries are `spanish/notes/ch01-summary.md` and
`spanish/notes/ch02-summary.md`; they are separate from the book's `.tex`
notes and are not compiled. The second summary records an interpretation
of an ambiguous precision phrase in the original. Terms used in this pilot
are recorded in `glossary.tsv` for review.

`check-spanish` builds the combined PDF and the two pilot chapter PDFs and checks paragraph coverage/order,
Arabic numerals, mathematical expressions (allowing translated conceptual
text), figure paths/transforms, labels, references, notes, index entries,
and build warnings. Its report is `build/spanish-audit/validation.json`.
It also checks the original sources and artwork against the pre-translation
snapshot when that local artifact is present. These mechanical checks
complement manual translation and visual review; they cannot certify prose.

Chapter 3 is independently audited with `check-chapter03`: English prose
against DOCX, 107 source paragraph positions, ten figures, five numbered
equations (plus the unnumbered repeat of 3.1), five notes, 105 index entries,
Spanish structure and numbers, and both standalone build logs. See
`spanish/notes/ch03-summary.md` for the chapter 3 editorial record; the later scope clarification in
`AGENTS.md` governs future chapters. The standalone PDFs are `build/chapter03/chapter03.pdf`
and `build/spanish-chapter03/chapter03.pdf`.

Chapter 4 has standalone targets `chapter04` and `spanish-chapter04`, producing
`build/chapter04/chapter04.pdf` and `build/spanish-chapter04/chapter04.pdf`.
`check-chapter04` audits English prose against DOCX, 65 paragraph positions,
three numbered equations, the two formula rows around figure 4.2, two figures,
three notes, 49 index entries, Spanish numbers/structure, and both build logs.
It verifies that the archived original, drafts, and accepted chapters remain
unchanged. See `spanish/notes/ch04-summary.md` for the concise editorial record.
The extraction script `tools/extract_chapter04.py` refuses to overwrite existing
English files; `--audit-only` refreshes its source map. The chapter's mathematical
line breaks and figure-label alignment are reviewed LaTeX typesetting.

Chapter 5 has standalone targets `chapter05` and `spanish-chapter05`, producing
`build/chapter05/chapter05.pdf` and `build/spanish-chapter05/chapter05.pdf`.
`check-chapter05` compares the English with the DOCX and checks 138 source
paragraph positions, six figures, fourteen notes (fifteen callouts, including
the original repeated note 4), and 235 index entries. It also checks Spanish
structure, numbers, inline powers and formulas, artwork inclusion, both build
logs, and protected earlier files. This chapter has no numbered display equations;
its formulas are inline styled text in Word. `tools/extract_chapter05.py` refuses
to overwrite existing English files; `--audit-only` refreshes the source map.
See `spanish/notes/ch05-summary.md` for the concise editorial record.

Chapter 6 uses `chapter06`, `spanish-chapter06`, and `check-chapter06`.
Its standalone PDFs are `build/chapter06/chapter06.pdf` (38 pages) and
`build/spanish-chapter06/chapter06.pdf` (39 pages). The audit checks the
English against DOCX, all 152 source paragraph positions, three figures,
three numbered equations, the external labels around figure 6.1, ten notes
with eleven callouts, and 223 index entries. It also checks values, powers,
references, build logs, PDF freshness, and the preserved originals and earlier
chapters. `tools/extract_chapter06.py --audit-only` refreshes the source map
without replacing editable text. See `spanish/notes/ch06-summary.md`.

## Plain text for prose review

Run `make -C tex prose-spanish` from the repository root. This exports
`tex/build/prose/spanish/ch01.txt` through `ch08.txt`, and `all-chapters.txt`,
plus `introduction.txt`, `conclusion.txt`, `acknowledgements.txt` and `supporting.txt`
directly from the Spanish LaTeX using local Pandoc and Python. No PDF build,
OCR, network access, or upload is needed.

The UTF-8 text preserves paragraphs, headings, captions/credits, numbered
references, and chapter notes. Comments, LaTeX commands, index markup,
images, page headers, and page numbers are excluded. The display
equations in chapters 2–4, 6 and 7 have explicit plain-text equivalents; inline math uses Pandoc's
Unicode rendering. These files serve prose review, while the PDFs remain
the reference for mathematical typography and layout. The original TeX
files are not modified. Re-run the target after editing the translation.
The earlier `chapters01-02.txt` remains restricted to the accepted pilot.
`all-chapters.txt` contains chapters 1–8 and their notes; `supporting.txt`
contains the three newly translated supporting sections.
`frontmatter.txt` contains the title, subtitle, author, translation credit,
dedication and epigraph.

## English build

From the repository root:

```sh
make -C tex en
make -C tex check
```

The review PDF is `tex/build/en/main.pdf`. The build uses LuaLaTeX,
latexmk, and MakeIndex. Pandoc and Python 3 are needed for the content
audit and extraction. Inkscape is needed when rebuilding an SVG-derived
PDF; a prepared PDF is supplied in `figs/pdf/en/`.

The individual chapter review builds preserve chapter, figure, equation,
and note numbering; their page numbers start afresh:

```sh
make -C tex chapter01
make -C tex chapter02
make -C tex chapter03
```

Outputs are `tex/build/chapter01/chapter01.pdf` and
`tex/build/chapter02/chapter02.pdf`; chapter 3 follows the same naming pattern.
`make -C tex pilot` retains the original two-chapter checkpoint in
`tex/build/pilot/pilot.pdf`; `en` includes all eight chapters and supporting sections.

LuaLaTeX needs a writable font cache. In this managed Codex environment,
the first font-cache initialization and Inkscape execution required the
normal sandbox approval mechanism. Normal book compilation does not
require LaTeX shell escape.

## Editing and regeneration

Edit the chapter `.tex` files directly. `% DOCX paragraph N` comments refer
to zero-based top-level paragraphs in `word/document.xml`. Notes are in
`en/notes/` and `spanish/notes/`. Both editions share the preamble and stable identifiers.
References to later, unextracted chapters remain readable literal text.

`tools/extract_chapter03.py` separately records the chapter 3 mapping and
refuses to overwrite existing English files. Its `--audit-only` option
refreshes the chapter audit without editing source files or artwork.

`tools/extract_pilot.py` pins the DOCX SHA-256 and records the reviewed
heading, figure, equation, and note mapping. It refuses to replace existing
chapter files unless explicitly invoked with `--force`:

```sh
python3 tex/tools/extract_pilot.py --force
```

That command replaces the pilot chapter sources, figure manifest, and
selected artwork copies. Use it only when deliberately regenerating the
English extraction, after preserving any editorial changes. It does not
change `GA/`, the shared preamble, drivers, Spanish files, or Word output.

`make -C tex check` refreshes its source audit without overwriting editable
files. It compares the resulting TeX prose against the DOCX, normalizing
whitespace and typographic quotes/dashes, and separately checks the eight
converted math objects, figure and note counts, 73 index entries, build
warnings, and hashes of all 50 archived source files. It intentionally
fails after unrecorded prose changes: any accepted editorial corrections
will need a corresponding explicit audit exception.

Generated audit files are in `tex/build/audit/`:

- `pilot-source-map.json`: source paragraphs, source hash, and index/figure/note mappings.
- `pilot-before-latex.json`: the normalized Pandoc document, including math expressions.
- `pilot-validation.json`: results of the most recent successful content audit.

These are generated artifacts and can be recreated. The validation is a
content check, not a substitute for visual review or a scientific edit.

## Typography and artwork

The review layout uses 170 × 240 mm pages, 11-point TeX Gyre Pagella, and
Pagella Math. This is a working book layout rather than a reconstruction
of the publisher's pagination. Sections are unnumbered; chapters, figures,
and the numbered equation retain their source numbers.

Original colour artwork is retained even though the DOCX previews are
grayscale. Figure 1.1 uses the high-resolution JPEG with a horizontal
reflection in LaTeX to match the manuscript's orientation. Figure 2.1 is
exported from SVG at the drawing bounds, with text converted to paths for
portable rendering; the editable SVG is preserved. See `../figs/manifest.tsv`.

Chapter 3 uses eight SVG-derived PDFs, the original PDF for figure 3.7,
and the unchanged DOCX PNG for figure 3.8. The latter preserves the dashed
A–B line that was not visible in the SVG PDF export. All ten figures were
compared with the embedded DOCX previews. Both languages share these assets.

Chapter 4 uses the original SVG-derived PDFs for both figures. Figure 4.1
retains the original colour artwork and has its blank outer margins trimmed
only at inclusion time. Figure 4.2 retains the Word formula labels above and
below its unchanged artwork; these are typeset identically in both editions.

Chapter 5 uses one unchanged original JPEG, two original PDFs, and three
SVG-derived PDFs. All six were compared with the DOCX previews. Figure 5.4's
blank outer margins are trimmed at inclusion time; both languages use the
same transform. Artwork colours and English labels are retained.

Chapter 6 uses three PDFs exported from the original SVGs. Figure 6.1's
external headings and compactness formulas are typeset in LaTeX, as in Word;
only these external text labels are translated. Artwork labels remain in
English. The colour in the original SVGs is retained; DOCX previews are grey.

Notes are grouped by chapter at the end and linked from superscript
callouts. Index pagination is regenerated for the included material. The
driver places notes before the index, as a working editorial layout;
the DOCX has these two blocks in the opposite order.


## Chapter 7

Build with `make -C tex chapter07 spanish-chapter07`; review PDFs are
`build/chapter07/chapter07.pdf` (55 pages) and
`build/spanish-chapter07/chapter07.pdf` (53 pages).
`make -C tex check-chapter07` compares the English with the DOCX and checks
213 paragraph positions, fifteen figures, one numbered equation, four rendered
math objects, eleven notes/callouts, and 253 index entries. It also checks
numbers, references, figure inclusion, protected sources and build logs.
The report is `build/ch07-audit/validation.json`.

`tools/extract_chapter07.py --audit-only` refreshes the source map without
overwriting the chapter. `make -C tex prose-spanish` exports `ch07.txt`, including
captions, notes and reviewed text equivalents for equation 7.1 and square roots.
See `spanish/notes/ch07-summary.md` for the editorial record.

Figures 7.1–3, 7.6 and 7.15 use original PDFs; 7.9, 7.10 and 7.12 use SVGs
exported to PDF; 7.13 uses the original JPEG. Figures 7.4, 7.5 and 7.11 use
unchanged images embedded in the DOCX. Figures 7.7, 7.8 and 7.14 use embedded
DOCX EMFs converted to PDF. These fallbacks preserve the DOCX artwork where
SVG variants are unsuitable or export with clipped/overlapping labels. The external
Word label above 7.3 is typeset separately and translated. The two editions
share every image and inclusion transform; no in-art labels were edited.
PDF annotations in 7.3, 7.6 and 7.15 are flattened with Ghostscript so that
LuaLaTeX retains the source labels. Figure 7.2 has a larger inclusion to make
its many small labels readable.


## Chapter 8

Build with `make -C tex chapter08 spanish-chapter08`. Review files are
`build/chapter08/chapter08.pdf` (51 pages),
`build/spanish-chapter08/chapter08.pdf` (53 pages), and
`build/prose/spanish/ch08.txt` (clean prose, including captions, table and notes).
The combined PDFs include chapters 1–8 and the supporting sections: 243 pages in English and 249 in
Spanish, with 1218 index entries each.

`make -C tex check-chapter08` checks DOCX fidelity, 171 paragraph positions,
18 comparison-table cells, seven figures, two numbered equations (8.1 is
repeated), sixteen notes/callouts and 280 index entries. It also checks all
nine source math objects, the restored box glyph, numerical values,
references, credits, shared artwork, build logs and protected files.
`tools/extract_chapter08.py --audit-only` refreshes the audit without
replacing editable chapter files. The table is extracted through
`tools/extract_chapter08_table.py` into `en/tables/ch08-waves.tex`.

Figures 8.1, 8.2 and 8.6 use the original PDFs, with annotations flattened;
8.7 uses the original SVG exported to PDF. Figures 8.3 and 8.4 use the
unchanged JPEGs embedded in the DOCX, and 8.5 its embedded EMF converted to
PDF, to preserve labels lost or overlapped by SVG font substitution.
Both languages share the same artwork and inclusion transforms.

The printed v/v factors in equation 8.1, its repeated number and the source's
subsequent reference to 8.2 are intentionally retained. See
`spanish/notes/ch08-summary.md` for the concise editorial record.
The conclusion appended to Anahi's draft is outside chapter 8.

## Introduction, conclusion and acknowledgements

`make -C tex supporting spanish-supporting` produces five-page review PDFs
at `build/supporting/supporting.pdf` and
`build/spanish-supporting/supporting.pdf`. Both combined books include these
sections in their proper front/back-matter positions.

`make -C tex check-supporting` checks all 24 source paragraph positions,
English fidelity to the DOCX, Spanish structure and numbers, names, clean
prose exports, build logs and preservation of earlier files. These sections
contain no figures, formulas, notes or index entries. The report is
`build/supporting-audit/validation.json`.

The existing English introduction is unchanged. Anahi's conclusion (appended
to chapter 8) and acknowledgements supplied the Spanish prose where sound;
no introduction draft was found. The source date and the acknowledgement
for the English edition are retained. Concise editorial records are in
`spanish/notes/introduction-summary.md`, `conclusion-summary.md` and
`acknowledgements-summary.md`.

`tools/extract_supporting.py --audit-only` refreshes the source map without
overwriting English files. The clean Spanish exports contain 640, 518 and
304 words respectively.

## Whole-book review

The complete bilingual textual review is recorded in
`spanish/notes/book-review-summary.md`; exact language and index-label edits
are in `tools/book_review_edits.json`. English, original drafts and artwork
are unchanged. Visual inspection is reserved for the user.

Build the review PDF with `make -C tex spanish`:
`build/spanish/main.pdf`. Refresh the clean text with
`make -C tex prose-spanish`; `build/prose/spanish/all-chapters.txt` contains
the eight chapters and notes, while `supporting.txt` and `frontmatter.txt`
contain the remaining prose.

`make -C tex check-book` runs all chapter/supporting audits and checks the
review snapshot, index references and combined build logs. Its final report
is `build/book-review/validation.json`.

Spanish builds run `tools/make_spanish_index.py` before MakeIndex, using a
generated `.sorted.idx` with consistent accent-insensitive sort keys and
separate ordering for ñ. Printed terms, page references and the raw `.idx`
are retained. After changing this build helper, force index regeneration
with `make -C tex spanish LATEXMK='latexmk -g -lualatex -interaction=nonstopmode -halt-on-error -file-line-error'`.
