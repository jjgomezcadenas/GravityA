# English LaTeX edition and Spanish translation plan

## Objective and source policy

Create a faithful, editable English LaTeX edition of *The Irresistible
Attraction of Gravity: A Journey to Discover Black Holes*, by Luciano
Rezzolla. Translate it into Spanish chapter by chapter, review the complete
translation, and only then produce the Word edition.

`GA/` is the untouched source archive. The authoritative text is
`GA/english_version/attraction_wfigs.docx`. The accompanying
`Attraction_en.pdf` is a secondary reference for visual interpretation; it
is not an interchangeable text source. Its chapter 4 title and ordering of
notes/index differ from the manuscript. Do not silently import PDF wording
or update the science. Preserve wording and credits; record suspected
errors separately for editorial decisions.

## Inventory established during assessment

| Chapter | DOCX title | Approximate words | Figures |
| --- | --- | ---: | ---: |
| 1 | Gravity … Attracts! | 2,700 | 1 |
| 2 | The Fathers of Gravity | 3,700 | 1 |
| 3 | Spacetime, Curvature and Gravity | 7,300 | 10 |
| 4 | Curving Spacetime | 5,200 | 2 |
| 5 | Neutron Stars: Wonders of Physics | 13,500 | 6 |
| 6 | Black Holes: Champions of Curvature | 14,300 | 3 |
| 7 | The First Image of a Black Hole | 19,300 | 15 |
| 8 | Gravitational Waves: Curvature in Motion | 17,800 | 7 |

The eight chapters total about 84,000 words. Supporting material comprises
the title/credits, dedication, epigraph, The Beginning of the Journey,
The End of the Journey, acknowledgements, chapter notes, and index.

The DOCX contains 45 drawings and matching figure captions, 47 Word math
objects (not necessarily 47 distinct equations), one comparison table,
and approximately 1,219 index-entry fields. The external artwork folder
contains 31 SVGs, 12 PDFs, and four JPEGs, including alternate versions.

## Directory layout

All directories below are relative to the repository root.

```text
GA/                              untouched source archive
PLAN.md                          this plan and milestone status
AGENTS.md                        current editorial and working instructions
tex/
  common/preamble.tex            shared typography and packages
  en/
    main.tex                     English book driver
    pilot.tex                    introduction and chapters 1–2
    frontmatter.tex
    introduction.tex
    ch01.tex ... ch08.tex         separate editable chapter files
    conclusion.tex
    acknowledgements.tex
    notes/ch01.tex ... ch08.tex   notes grouped by source chapter
  spanish/                       matching structure as translated
  tools/                         reproducible extraction and validation
  glossary.tsv                   shared English–Spanish terminology
  editorial-notes.md             source issues and editorial decisions
  Makefile                       documented build entry points
  build/                         generated PDFs, logs, conversion audit
figs/
  manifest.tsv                   figure ID, source, variant, credit
  source/en/                     copies of selected original artwork
  pdf/en/                        prepared diagrams shared by both editions
  png/en/                        raster derivatives as needed
docx/                            reserved for approved final exports
```

Create content only when that stage is reached. Empty Spanish and Word
destinations are not translated/exported editions. Keep build products
separate from editable chapter sources. Use stable chapter filenames,
figure IDs, equation labels, and note identifiers across languages.

## Figure policy

| Format | Advantages | Limitations | Role |
| --- | --- | --- | --- |
| PDF | Sharp vectors/text and direct LaTeX inclusion | Labels may be difficult to edit | Default diagrams and plots |
| PNG | Predictable rendering and Word compatibility | Resolution-dependent, larger at high resolution | Word derivatives and raster artwork |
| SVG | Editable vector artwork and labels | Conversion required for the proposed LaTeX build | Editable master |
| JPEG | Appropriate for existing photographs | Lossy recompression | Retain original photographs |

Preserve SVG masters and explicitly export PDFs before compiling LaTeX.
The LaTeX `svg` package is possible, but it normally invokes Inkscape and
requires shell escape for automatic conversion. Pre-exporting keeps normal
book builds independent of that step. Existing PDFs need no rasterization.
Raster images embedded in SVG/PDF retain their original resolution.

For Word, generate PNGs at a resolution appropriate to the final printed
size (normally 300 dpi, higher for fine line art where needed). Do not
convert original photographs through unnecessary lossy formats. Prefer
the separate artwork over lower-quality embedded DOCX previews after
confirming that it is the correct version. Compare alternatives visually,
especially figure 7.1. Preserve figure credits and record provenance.

Translate captions only. Use the same figures and inclusion transforms in
both editions; retain English labels inside the artwork. Do not modify
figures or create Spanish variants. This editorial decision supersedes the
earlier proposal to translate figure labels.

References: [SVG package documentation](https://tug.ctan.org/graphics/svg/doc/svg.pdf),
[Pandoc manual](https://pandoc.org/MANUAL.html).

## Extraction design and known hazards

- Recover chapter/section structure from explicit manuscript boundaries
  and formatting. Several titles are unstyled or split over paragraphs;
  a stock conversion does not recover them correctly.
- Use Pandoc for text formatting and Word math conversion, supplemented
  by an auditable DOCX XML preprocessing step. Fail on unaccounted content
  rather than silently omit it. Keep a source paragraph/asset mapping.
- Reconcile each drawing and caption against the artwork manifest. The
  initial stock conversion emitted only 44 images, omitting the drawing
  beside figure 4.2, and retained seven EMF images.
- Preserve all math objects and inspect their rendering, vector notation,
  subscripts, superscripts, signs, units, and equation numbers. Math-like
  ordinary text also requires attention.
- Recover chapter notes and callouts from ordinary manuscript paragraphs.
  They are not native Word footnotes/endnotes. Distinguish note callouts
  from numerical exponents; never map every superscript to a note.
- Preserve Word XE index fields at their source positions, translate
  index terms later, and rebuild page numbers in each edition. The old
  printed index is a reconciliation reference, not reusable pagination.
- Preserve the chapter 8 comparison table with readable column widths.
- Replace unambiguous textual chapter/figure/equation references with
  semantic LaTeX references where possible, without changing wording.
  A partial pilot must not show broken references to unextracted chapters.
- Use LuaLaTeX with consistent Unicode fonts, standard LaTeX structures,
  and few custom macros. Both language drivers should build complete
  editions and allow chapter-focused reviews with consistent numbering.
- Keep extraction repeatable, but do not overwrite edited/approved source
  files automatically. Regeneration must be explicit and reviewable.

## Milestones and acceptance checks

### 1. Two-chapter English pilot — current implementation scope

Build the title/credits, dedication, epigraph, introduction, chapters 1–2,
their two figures, their three chapter notes, the numbered gravitational
force equation, and a regenerated index for the included material.
Provide the driver, shared preamble, figure manifest, build instructions,
source mapping, and an audit of the conversion.

Validate before extending extraction:

1. Compare extracted prose with source paragraphs, accounting explicitly
   for recovered structure, index fields, note callouts, and captions.
2. Confirm all pilot math, images, captions, credits, lists, and notes are
   present; distinguish mathematical superscripts from note markers.
3. Compile successfully with no missing images, undefined references,
   missing glyphs, or unresolved index processing.
4. Inspect rendered title, contents, chapter openings, both figures,
   the force equation, notes, and index. Address material overflow.
5. Rebuild from the documented entry point and verify `GA/` hashes remain
   unchanged. Record remaining editorial issues without silently fixing
   the author's prose or scientific claims.

The pilot is a reviewable checkpoint before the full extraction. It does
not establish that later chapter tables, alternate images, complex math,
or all index cross-references have been validated.

### 2. Complete English LaTeX edition

Extend the validated method to chapters 3–8 and the remaining supporting
material. Reconcile all 45 figures, all 47 math objects, the comparison
table, all notes, and the source index fields. Finish semantic references
and independently compile each chapter as well as the complete book.
Review the full PDF and document any unresolved source ambiguities.

### 3. Spanish translation pilot

Translate the two existing chapters (1–2), including captions, equations,
notes, and index terms. Read Anahi's corresponding drafts and reuse her
prose wherever accurate; repair omissions, errors, and garbled passages
against the authoritative English. Preserve scientific meaning and the
author's voice. Keep artwork unchanged. Maintain a shared glossary and
concise chapter summaries in `tex/spanish/notes/`. See `AGENTS.md` for the
complete translation instructions. This pilot precedes full extraction.

### 4. Chapter-by-chapter Spanish translation

For each chapter, deliver the `.tex` text, translated notes and captions,
shared original artwork, and a compiled review PDF. Record substantive
decisions in a concise chapter summary, update the glossary, and mark review
status. Chapters 5–8 may be processed internally in sections, but the
review unit remains a complete chapter.

### 5. Whole-book editorial review

Check scientific meaning, consistent terminology and voice, chapter and
equation numbering, figure/table references, credits, bibliography within
notes, translated index terms, and front/back matter. Rebuild pagination
and the index. Obtain approval of the complete translation before final
Word production.

### 6. Word production

Export approved content with Pandoc, a reference DOCX style template, and
explicit handling for notes, references, index entries, and figure paths.
Prefer native Word equations and editable text. Use PNG derivatives where
required by Word. Validate structure and content against the approved
LaTeX edition, then inspect Word layout separately: pagination need not
match the PDF. Do not promise a lossless round trip for arbitrary LaTeX.

## Status

- [x] Inspect archive and identify authoritative source and hazards.
- [x] Record the complete agreed plan.
- [x] Build and validate the two-chapter English pilot.
- [ ] Extend to the complete English edition after pilot review.
- [x] Translate, compile, and validate the Spanish chapters 1–2 pilot.
- [x] Author acceptance of the Spanish chapters 1–2 pilot.
- [x] Extract, translate, and validate chapter 3 with figures and notes.
- [x] Author acceptance of chapter 3; preserve the original's popular-science explanations without scientific revision.
- [x] Extract, translate, and validate chapter 4 with figures and notes.
- [x] Author acceptance of chapter 4; proceed with chapter 5.
- [x] Extract and translate chapter 5 with figures and notes.
- [x] Validate chapter 5 and deliver review PDF/prose.
- [x] Proceed to chapter 6 at the user’s request; preserve chapter 5.
- [x] Extract, translate, and validate chapter 6 with figures, formulas and notes.
- [ ] Author review of chapter 6.
- [ ] Translate the remaining chapters and supporting material.
- [ ] Review and approve the complete translation.
- [ ] Produce and validate the Word edition.

### Pilot checkpoint — 2026-10-14

Delivered `tex/build/en/main.pdf` (26 pages), separate chapter sources,
and standalone chapter PDFs (9 and 12 pages). `make -C tex check` passes:
all six content groups match the DOCX after documented typography/spacing
normalization; eight converted math objects, two figures, three notes,
and 73 index entries are preserved. All final build logs are free of
warnings, overfull/underfull boxes, missing glyphs, and undefined references.
All 50 files under `GA/` match the recorded initial hashes. Title, contents,
chapter openings, both figures, equations, notes, and index were visually
reviewed. The high-resolution photograph is reflected at inclusion time
to match the DOCX, and the SVG export is cropped to its drawing bounds.

The checkpoint intentionally contains only chapters 1–2 and their supporting
material. Full extraction remains milestone 2. Build instructions and
validation limitations are in `tex/README.md`; source issues are recorded
in `tex/editorial-notes.md`.

### Spanish pilot checkpoint — 2026-10-14

Delivered `tex/build/spanish/main.pdf` (24 pages) and standalone chapter
PDFs (10 and 12 pages). All 87 source paragraph positions are represented;
the pilot includes two unchanged figures, eight mathematical expressions,
three translated notes, and 73 translated index entries. The conceptual
equation uses Spanish words; the other seven math objects are unchanged.

`make -C tex check-spanish` passes for all three builds, without warnings,
overfull/underfull boxes, missing glyphs, or undefined references. The
English regression check also passes. The 75 protected files under `GA/`,
`anahi/`, `figs/`, and `tex/en/` match the pre-translation snapshot.
Representative chapter, figure, equation, note, and index pages were
visually reviewed. The Arabic-numeral check allows Spanish decimal commas
and «cuarenta» for the source's «40»; prose accuracy still needs author review.

`AGENTS.md` records the agreed workflow. Chapter summaries in
`tex/spanish/notes/` record substantive repairs and the source questions:
Cuarón's nationality as stated in the original and the interpretation of
the ambiguous precision phrase in chapter 2. Final Word export is deferred.

### Chapter 3 checkpoint — 2026-10-14

English chapter 3 has been extracted from the authoritative DOCX; its
prose matches the source under the same typography normalization as the
pilot. The Spanish version reuses Anahi's valid prose and restores the
missing geodesic passage, equations, captions, and notes. It corrects the
draft's reversals of non-zero curvature and other transcription errors.
The chapter contains 107 source paragraph positions, ten figures, five
numbered equations plus one repeated conceptual display, five notes, and
105 index entries. The nine original Word math objects include three
separately encoded equation numbers, now generated by LaTeX.

Standalone PDFs are `tex/build/chapter03/chapter03.pdf` (26 pages) and
`tex/build/spanish-chapter03/chapter03.pdf` (28 pages). Both main drivers
now include chapters 1–3; their PDFs have 50 pages each. Plain text is in
`tex/build/prose/spanish/ch03.txt` (about 8000 words), with the current
Spanish chapters combined in `all-chapters.txt`.

All ten figures were compared against their DOCX previews. Figure 3.8 uses
the unchanged embedded PNG to preserve the dashed A–B line missing from
the SVG-derived PDF rendering. The other nine use the original separate
artwork, including the source PDF for figure 3.7. No artwork labels were
translated. Representative chapter openings, equations, figures, notes,
and index pages were visually reviewed.

Chapter checks and earlier-chapter regression checks pass. Original
archives, drafts, and accepted chapter 1–2 text remain unchanged. Scientific
questions inherited from the original are recorded concisely in
`tex/spanish/notes/ch03-summary.md`; the translation does not silently
rewrite those claims. Word production remains deferred.

### Chapter 4 checkpoint — 2026-10-14

Extracted the complete DOCX chapter and its three notes, and translated them
using the valid prose in Anahi's main draft. The unrelated cosmology supplement
was excluded. The original's explanations and numerical claims were preserved;
translation errors and missing material were repaired without scientific revision.

The chapter has 65 source paragraph positions, two unchanged figures, three
numbered equations, two rows of formula labels around figure 4.2, three notes,
and 49 index entries. Its nine Word math objects include one empty object;
the eight nonempty expressions are preserved, with the solar-symbol typo repaired
only in the Spanish note. Both SVG exports were compared with the DOCX previews.

Review files: `tex/build/chapter04/chapter04.pdf` (15 pages),
`tex/build/spanish-chapter04/chapter04.pdf` (16 pages), and
`tex/build/prose/spanish/ch04.txt` (about 5800 words). The combined English and
Spanish PDFs now include chapters 1–4 and have 65 pages each. The editorial
summary is `tex/spanish/notes/ch04-summary.md`.

Chapter 4 content, math, structure, numerical and build checks pass, as do the
checks for the preceding chapters. Archived originals, Anahi's drafts, and
accepted chapters 1–3 remain unchanged. Equations, figures, notes and representative
rendered pages have been visually reviewed. Author review of chapter 4 is pending.

### Chapter 5 checkpoint — 2026-10-14

Extracted the complete English chapter and its fourteen notes from the DOCX,
and translated them using Anahi's valid prose. Restored omitted passages,
corrected transcription and translation errors, and preserved the original's
scientific claims and popular-science explanations. The concise account is
`tex/spanish/notes/ch05-summary.md`.

The chapter contains 138 source paragraph positions, six figures, fourteen
notes with fifteen callouts, and 235 index entries. It has no numbered display
equations or native Word math objects; inline formulas, powers, symbols and
numerical values are preserved. The repeated note 4 and its appearance before
note 3 follow the original. All six figures were compared with DOCX previews.
The original JPEG, two original PDFs and three SVG-derived PDFs are shared
between languages; figure 5.4 has blank margins trimmed only at inclusion time.
The artwork and its English labels remain unchanged.

Review files: `tex/build/chapter05/chapter05.pdf` (39 pages),
`tex/build/spanish-chapter05/chapter05.pdf` (40 pages), and
`tex/build/prose/spanish/ch05.txt` (14,813 words, including captions and notes).
The combined English and Spanish PDFs include chapters 1–5 and have 102 and
105 pages respectively. Both contain 462 index entries and twenty-five notes.

Chapter 5 source-fidelity, coverage, numerical, notation and build checks pass,
as do all earlier chapter checks. Final logs are free of warnings, missing
glyphs, unresolved references and overfull/underfull boxes. The 124 protected
files match the pre-chapter snapshot, allowing only the driver inclusions and
manifest additions. Representative English and Spanish pages, all translated
figures, inline notation, notes and index were visually reviewed. Clean prose
was exported locally; no external detector was used. Author review of chapter 5
is pending. Word production remains deferred.


### Chapter 6 checkpoint — 2026-10-14

Extracted the complete English chapter and ten notes from the authoritative
DOCX, then translated them using Anahi’s draft where sound. Missing and
garbled passages, equations and notes were restored against the original;
draft comments and duplicated material were removed. The concise editorial
record is `tex/spanish/notes/ch06-summary.md`.

The chapter contains 152 source paragraph positions, three figures, three
numbered equations, two external figure-label rows, ten notes with eleven
callouts, and 223 index entries. Seven Word math objects represent the three
equations, a separate equation number, two figure-label rows and an inline
inequality. Ordinary Word star subscripts are rendered with the matching
math symbol. English prose and source claims remain unchanged.

All three assets use the original SVG artwork exported to PDF. Their content
was compared visually with the embedded DOCX previews; original colour and
in-art English labels are retained. The labels outside figure 6.1 are typeset
in LaTeX and translated in Spanish, without modifying the artwork.

Review files: `tex/build/chapter06/chapter06.pdf` (38 pages),
`tex/build/spanish-chapter06/chapter06.pdf` (39 pages), and
`tex/build/prose/spanish/ch06.txt` (14,465 words, including captions and notes). Both combined books now include chapters
1–6: 138 pages in English and 142 in Spanish, with 685 index entries and
thirty-five notes each.

Source-fidelity, coverage, mathematics, numerical, reference and build checks
pass, including all earlier chapter checks. Logs are free of warnings,
missing glyphs and unresolved references. The 140 protected files match the
pre-chapter snapshot, allowing only the new driver inclusions and figure
manifest entries. Representative equations, figures, notes and index pages
were inspected in both editions. Clean prose was exported locally; no
external detector was used. Chapter 6 is ready for author review.

### Chapter 7 checkpoint — 2026-10-14

Extracted and translated the complete chapter and eleven notes, using the
DOCX/English LaTeX as the reference and retaining Anahi’s sound prose. Later
edition material about the 2022 Sagittarius A* image was omitted; the original
prospective timeline and scientific claims were preserved. Draft errors and
omissions are recorded in `tex/spanish/notes/ch07-summary.md`.

The chapter has 213 source paragraph positions, fifteen figures, one numbered
equation, four rendered math objects, eleven notes/callouts and 253 index
entries. The fifth Word math object is the separately stored equation number.
The square-root conversion and an index entry in a section title were restored
without changing source meaning. Captions, references, numerical values,
notation and index terms were checked in both languages.

Shared artwork comes from original PDF/SVG/JPEG files and, for six figures,
the unchanged DOCX-embedded images. Embedded artwork avoids SVG label export
problems and preserves the authoritative figure. Existing annotations in
PDF figures 7.3, 7.6 and 7.15 were flattened so LaTeX retains the source labels.
Figure 7.2 has a larger inclusion for readability. No artwork was redrawn or
translated. Provenance and conversion choices are in `figs/manifest.tsv`.

Standalone review PDFs: `tex/build/chapter07/chapter07.pdf` (55 pages) and
`tex/build/spanish-chapter07/chapter07.pdf` (53 pages). Clean Spanish prose:
`tex/build/prose/spanish/ch07.txt` (17,826 words, including captions and notes).
Both combined editions now contain chapters 1–7 and have 191 pages, 938 index
entries and forty-six notes. The English combined edition also retains the
previously extracted front matter and introduction.

All chapter and regression checks pass. The English text matches the DOCX;
153 protected files match the pre-chapter snapshot, allowing only new driver
inclusions and manifest rows. Build logs contain no warnings, unresolved
references, missing glyphs or overfull boxes. All chapter 7 figures and
representative equation, prose, note and index pages were visually reviewed.
The audit artifacts are under `tex/build/ch07-audit/`. No external detector
was used; chapter 7 is ready for author review. Word export remains deferred.

### Chapter 8 checkpoint — 2026-10-14

Extracted and translated chapter 8 through the DOCX chapter boundary, with
its comparison table, seven figures, formulas, sixteen notes and 280 index
entries. Anahi's usable prose was retained; missing or garbled passages,
notations and draft figures were restored against the English. The conclusion
appended to her file remains outside this chapter. The concise editorial
record is `tex/spanish/notes/ch08-summary.md`.

The audit covers 171 source paragraph positions and 18 table cells. Nine Word
math objects and the damaged box glyph are rendered; equations 8.1 and 8.2
retain their numbering, including the repeated 8.1. The source's v/v factors
and the adjacent reference discrepancy are preserved and documented, without
revising the author's claims. Spanish repairs the obvious identifier typo
GW17817 to GW170817; English remains literal.

The two editions share all artwork and transforms. Original PDF/SVG colour
is retained for 8.1, 8.2, 8.6 and 8.7; 8.3 and 8.4 use unchanged DOCX JPEGs
and 8.5 the DOCX EMF converted to PDF, avoiding clipped/overlapping SVG labels.
All seven were compared with their DOCX versions. Representative prose,
table, formula, note and index pages were inspected in both editions.

Review files are `tex/build/chapter08/chapter08.pdf` (51 pages),
`tex/build/spanish-chapter08/chapter08.pdf` (53 pages), and
`tex/build/prose/spanish/ch08.txt` (19,199 words, including captions, table and
notes). Both combined editions contain chapters 1–8, with 241 English pages,
243 Spanish pages, 1218 index entries and sixty-two notes. The conclusion,
acknowledgements and Spanish front matter remain outside this checkpoint.
Word export remains deferred until approval of the translation.

All chapter and regression audits passed, including the unchanged earlier
chapters. The 192 protected files match the pre-chapter snapshot, allowing
only new driver inclusions and appended figure-manifest rows. Both chapter
logs are clean. Clean prose was generated locally; no external detector was
used. Chapter 8 is ready for author review.

### Introduction, conclusion and acknowledgements checkpoint — 2026-10-14

Completed the three authorized supporting sections. The existing English
introduction was preserved; the conclusion and acknowledgements were
extracted from the authoritative DOCX. All three were translated into Spanish.
Anahi's conclusion and acknowledgements supplied reusable prose; no
corresponding introduction draft was found among her files. The conclusion's
garbled ending and missing date were restored, and the acknowledgements
retain the original English-edition credit. Concise editorial records are
`tex/spanish/notes/introduction-summary.md`, `conclusion-summary.md` and
`acknowledgements-summary.md`.

The source audit covers 24 paragraph positions (9, 10 and 5 respectively).
These sections contain no figures, formulas, notes or index entries.
English prose matches the DOCX. Coverage, numbers, names, references,
clean-prose freshness and build checks pass. All earlier chapter audits pass;
218 protected files are unchanged apart from the exact new driver inclusions.
The original archives, drafts, accepted chapter prose and artwork remain intact.

Review PDFs are `tex/build/supporting/supporting.pdf` and
`tex/build/spanish-supporting/supporting.pdf`, five pages each. All five
Spanish pages and representative English pages were visually inspected.
The combined English and Spanish books now have 243 and 247 pages respectively,
including all eight chapters, sixty-two notes and 1218 index entries each.
Final build logs are clean.

Clean Spanish prose is in `tex/build/prose/spanish/introduction.txt` (640 words),
`conclusion.txt` (518 words), `acknowledgements.txt` (304 words) and their combined
`supporting.txt`. `all-chapters.txt` remains restricted to chapters 1–8 and notes.
No external detector was used. These three sections are ready for author review;
Spanish credits, dedication, epigraph, final whole-book editorial review and
Word export remain outside this checkpoint.

### Spanish front matter checkpoint — 2026-10-14

Added the approved title «La irresistible atracción de la gravedad», subtitle
«Un viaje para descubrir los agujeros negros» and credit «Traducción de Anahí
Seri Murciano». Translated the dedication and epigraph from the source, preserving
Emilia and Domenico. No publisher or copyright details were invented.
The source is `tex/spanish/frontmatter.tex`; the editorial record is
`tex/spanish/notes/frontmatter-summary.md`, and clean prose is exported to
`tex/build/prose/spanish/frontmatter.txt`.

The combined Spanish PDF now has 249 pages. Its title, dedication, epigraph
and first contents page were visually checked. `check-spanish` and
`check-supporting` pass with clean build logs. All 228 files in the pre-change
snapshot are preserved, allowing only the Spanish driver's replacement of
its old title block with the new front-matter inclusion. English and accepted
chapter prose remain unchanged. Final whole-book review and DOCX production
remain pending.

### Whole-book textual review checkpoint — 2026-10-14

Completed a full bilingual reading of chapters 1–8, all captions, formulas,
the comparison table and 62 notes, plus introduction, conclusion,
acknowledgements and front matter. Applied eight local language corrections
and seven groups of index-label corrections; the exact 15 records are in
`tex/tools/book_review_edits.json`. Sound prose and the original scientific
claims and dates were preserved.

Fixed Spanish index sorting: accented spellings and explicit sort keys now
merge consistently, without losing any of the 1218 input entries or their
page references. All 14 formal index cross-references resolve, and the
generated index has no duplicate headings. All eight standalone Spanish
indexes were regenerated and checked.

All existing chapter and supporting-section audits passed. Combined PDFs
remain 243 pages in English and 249 in Spanish, with clean build logs.
All 230 files in the review snapshot match their previous versions after
undoing only the exact recorded Spanish edits; GA, Anahi's drafts, English
and artwork are unchanged. Clean Spanish prose has been refreshed.

The concise review and pending source questions are in
`tex/spanish/notes/book-review-summary.md`; mechanical results are in
`tex/build/book-review/validation.json`. Use `make -C tex check-book` for
the complete audit. Per the user's instruction, no page images were
inspected during this review: visual inspection is the user's next step.
DOCX export remains deferred until translation approval.
