# Working instructions for GravityA

## Purpose and source hierarchy

Build an accurate English LaTeX edition, then a Spanish translation chapter
by chapter. Generate Word only after the Spanish translation is approved.
The implementation plan is in `PLAN.md`; these instructions record the
user's editorial decisions and take precedence over older plan details.

1. `GA/english_version/attraction_wfigs.docx` is the authoritative original.
2. The validated chapter files in `tex/en/` are the working English source
   for translation. Check the DOCX if an extraction appears doubtful.
3. `anahi/` contains incomplete, sometimes inaccurate Spanish drafts. They
   supply the basis for translation style and reusable prose, not a competing
   source of facts, content, chapter boundaries, or numbering.
4. The accompanying English PDF is a secondary visual reference. It contains
   edition differences; do not import its additions or wording into the
   translation when they differ from the authoritative DOCX/English LaTeX.

Preserve `GA/` and `anahi/` unchanged. The English original must not be
edited: this is a translation, not a scientific revision. Keep validated
English LaTeX faithful to the DOCX; correcting an extraction defect is not
permission to revise the author's prose or claims. Do not update the science
to a newer edition.

## Popular-science editorial scope

Read the original as a physics professor's explanation for a broad public.
Respect its pedagogical intent, analogies, accessible language, and deliberate
simplifications. Do not treat omitted technical qualifications or a lack of
textbook precision as errors when the intended explanation is clear. Avoid
pedantic objections and do not add technical caveats to the translation.

Distinguish errors in Anahi's translation, which should be corrected against
the English source, from claims made by the author, which should be translated
faithfully. Only flag clear, consequential source errors in the concise
editorial notes; do not turn those notes into a scientific referee report.
Flagging a source issue does not authorize changing either the original or
its meaning in Spanish. Any substantive correction to an author's claim in
the translation requires the user's explicit instruction.

## Spanish translation method

For each chapter:

- Read the complete corresponding English LaTeX chapter, its notes and
  captions, and Anahi's corresponding draft before drafting the translation.
- Reuse Anahi's prose whenever it expresses the original accurately and
  reads well. Preserve her narrative voice as far as possible. Do not
  replace sound passages merely to impose a different style.
- Exercise editorial judgment autonomously. Correct errors, questionable
  translations, awkward wording, transcription mistakes, and inconsistent
  terminology. Scientific meaning takes priority; for example, `non-zero
  curvature` must not become `curvatura nula`.
- Follow the English LaTeX whenever the draft differs in content or
  structure. Restore omissions, reconcile misplaced or duplicated passages,
  and discard additions belonging to another edition or another work.
- Translate missing, confused, or garbled passages independently. Remove
  draft comments and placeholders from book prose; preserve material
  editorial questions in the chapter summary if they remain unresolved.
- Preserve the original claims, numerical values, qualifications, examples,
  names, and references. Correct evident typographic defects without
  changing meaning; record substantive interventions concisely.
- Translate the entire chapter, including headings, captions, lists, tables,
  chapter notes, and index terms. Keep equations, symbols, stable labels,
  numbering, and cross-references aligned with the English version.
- Maintain a shared terminology glossary in `tex/glossary.tsv`. Use fluent,
  consistent Spanish suitable for this popular-science narrative.

Known draft hazards include chapter 3 material appended to the chapter 2
file, the conclusion appended to chapter 8, editorial remarks in ordinary
paragraphs, missing equations, and the separate `Capítulo 4-ampl.docx`.
Determine chapter boundaries from the English source, not Spanish filenames.

## Artwork and mathematics

Use the same prepared figure assets and inclusion transforms as the English
edition. Include every source figure and formula in the Spanish edition.
Translate captions, but **do not modify the figures or translate labels
inside them**, even when those labels remain in English. Do not create
Spanish artwork variants. Preserve credits and original artwork provenance.
Earlier plan provisions for translating figure labels are superseded.

Retain mathematical meaning and equation numbering. Translate words inside
textual/conceptual equations when appropriate, while retaining their
structure. Restore equations omitted or damaged in Anahi's drafts directly
from the validated English LaTeX. Use consistent Spanish numeric typography
without changing values.

## Directories and deliverables

- `tex/en/`: English chapters and drivers.
- `tex/spanish/`: Spanish chapters and drivers. Keep this directory name;
  do not introduce `tex/es/` or a root `/es/` directory.
- `tex/spanish/notes/ch01.tex`: the book's translated chapter 1 notes.
- `tex/spanish/notes/ch01-summary.md`: our concise editorial account for
  that chapter. Apply the same naming scheme to subsequent chapters.
- `figs/`: shared artwork; no translation-specific image edits.
- `docx/`: final Word exports, deferred until translation approval.
- `tex/build/`: generated PDFs, logs, and audit artifacts.

At the end of each chapter, write a short summary of substantive changes:
material corrections, restored text/formulas, removed draft intrusions, and
source-edition discrepancies. Do not catalogue routine punctuation or every
wording choice. Keep these summaries outside the book's compiled text.

## Verification and work sequence

Chapters 1–8 form the completed baseline, including all figures, formulas,
captions, notes and index terms. The introduction, conclusion and
acknowledgements are also authorized for extraction and translation. Apply the
same method and validate each chapter before extending to subsequent ones.
Preserve the accepted earlier prose.

Check paragraph/section coverage against English, mathematical expressions
and numbers, figure paths and transforms, captions/credits, note callouts,
and cross-references. Compile both combined and chapter review PDFs and
inspect representative rendered pages. Address missing glyphs, unresolved
references, missing figures, and material layout defects. Build instructions
belong in `tex/README.md`; expose normal targets through `tex/Makefile`.

From the repository root, use `make -C tex spanish` for the combined
Spanish PDF, `make -C tex spanish-chapter01 spanish-chapter02` for chapter
PDFs, and `make -C tex check-spanish` for the translation structure/build
audit. Run `make -C tex check` when shared build files change to verify
the English edition still matches the DOCX. Mechanical audits complement
linguistic and visual review; they do not establish translation accuracy.

Chapter 3 has standalone targets `chapter03`, `spanish-chapter03`, and
`check-chapter03`. Chapter 4 follows the same naming pattern: `chapter04`,
`spanish-chapter04`, and `check-chapter04`. Chapter 5 uses `chapter05`,
`spanish-chapter05`, and `check-chapter05`. Chapter 6 uses `chapter06`,
`spanish-chapter06`, and `check-chapter06`. Chapter 7 uses `chapter07`,
`spanish-chapter07`, and `check-chapter07`. Chapter 8 uses `chapter08`,
`spanish-chapter08`, and `check-chapter08`. Both main drivers include chapters
1–8. Use
`make -C tex prose-spanish` for local plain-text exports in
`tex/build/prose/spanish/`, including `ch03.txt`, `ch04.txt`, `ch05.txt`, `ch06.txt`, `ch07.txt`, `ch08.txt`, and `all-chapters.txt`.
Use clean prose, without LaTeX comments or commands, for external prose
checks. Do not rewrite sound passages merely because a detector flags
them; the user confirmed a false positive caused by a source comment.

Extraction scripts must not overwrite edited chapter files automatically.
Keep regeneration explicit and reviewable. Preserve source-position comments
where useful for comparing English and Spanish.

Make routine translation and implementation decisions without repeatedly
asking for confirmation. Use the existing approved build command forms
where possible. Actual sandbox restrictions still apply. Do not publish,
send files to other people, or change original archives as part of this work.

Chapter 8 includes a comparison table in `en/tables/ch08-waves.tex` and
`spanish/tables/ch08-waves.tex`. Include it in coverage, index counts and clean
prose exports. Preserve the DOCX equation 8.1, including its printed v/v factors,
its repeated number and subsequent reference to 8.2; the discrepancy is recorded
in `spanish/notes/ch08-summary.md` and has not been authorized for correction.
The conclusion appended to Anahi’s chapter 8 draft is outside that chapter
and is translated separately in `spanish/conclusion.tex`.

The supporting sections use `introduction.tex`, `conclusion.tex` and
`acknowledgements.tex` in each language. The validated English introduction
is preserved. Anahi has a conclusion and acknowledgements draft but no
introduction draft was found. Keep the conclusion's source date and the
English-edition acknowledgement to Victoria Hislop; do not invent Spanish
credits. Spanish front matter is now authorized; DOCX export remains deferred.

Use `make -C tex supporting spanish-supporting check-supporting` for the
supporting-section review PDFs and audit. `prose-spanish` also produces
`introduction.txt`, `conclusion.txt`, `acknowledgements.txt` and `supporting.txt`.
`all-chapters.txt` continues to contain only chapters 1–8 and their notes.
Concise editorial records are `spanish/notes/<section>-summary.md`.

## Spanish edition credits

The user specified the translator's name as **Anahí Seri Murciano**.
Use **Traducción de Anahí Seri Murciano** in the Spanish front matter.
The user approved **La irresistible atracción de la gravedad** with the
subtitle **Un viaje para descubrir los agujeros negros**. The title page,
translation credit, dedication and epigraph are in `tex/spanish/frontmatter.tex`.
The dedication preserves the source names Emilia and Domenico. Do not invent
publisher, ISBN, copyright or Spanish copy-editing details.

## Final book review

The user authorized a complete textual review and mechanical checks, with clear
translation and production errors corrected directly. Preserve sound prose and
the original scientific claims. Record exact corrections in
`tex/tools/book_review_edits.json` and summarize substantive results concisely in
`tex/spanish/notes/book-review-summary.md`. Historical snapshot checks may undo
only those recorded edits when comparing with the earlier accepted versions.
For this review the user will inspect the rendered pages; do not spend time or
tokens on visual inspection. Rebuild the revised PDF and refresh clean prose.
Word export remains deferred.

Spanish builds normalize index sort keys through `tools/make_spanish_index.py`
before running MakeIndex; do not mix manual and implicit accent sorting.
`make -C tex check-book` runs the complete audit, including the final review
snapshot and index checks. The exact review-edit manifest permits only the
recorded wording replacements, with explicit occurrence counts where needed.
