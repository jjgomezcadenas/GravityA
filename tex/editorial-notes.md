# Editorial and conversion notes

## Source policy

The DOCX supplies the wording. The accompanying PDF is a different
editorial/layout state. No scientific updates or prose corrections have
been made during extraction. Paragraph numbers below are zero-based
top-level DOCX paragraph positions.

## Open source issues

| Location | Observation | Current treatment |
| --- | --- | --- |
| Chapter 2, paragraph 140 | “universal law of gravitation)” has an unmatched closing parenthesis. | Preserved; editorial correction pending. |
| Chapter 2, paragraph 153 | The deliberately conceptual gravity expression has no proportionality constant; the following numbered equation includes G. | Preserved as written; no scientific intervention. |
| Chapter 2, paragraph 159 | The numerical value of G and text notation `x 10` are the manuscript's wording/notation. | Preserved; any update or notation change should be explicit. |

## Resolved conversion issues

- Recovered unstyled chapter/section titles and removed physical Word
  paragraph indents that Pandoc interpreted as block quotations.
- Reconstructed three note callouts by explicit source location, retaining
  mathematical exponents as superscripts.
- Preserved 73 XE index fields, including the source index cross-reference
  from “relativity:general” to “general relativity”. Rebuilt page numbers.
- Preserved eight Word math objects, including the conceptual expression,
  equation (2.1), inline vectors, and the chapter 2 note mathematics.
- Matched figure 1.1 to the high-resolution original; used a horizontal
  reflection at inclusion time because the supplied JPEG has the opposite
  orientation to the DOCX image. The original file is unchanged.
- Matched figure 2.1 to its SVG master. Exported only its drawing bounds
  to avoid reproducing the SVG's large empty A4 canvas.
- Used the original artwork's colour. Both DOCX previews are grayscale.
- Linked in-pilot figure/equation references and note callouts. References
  to future chapters remain literal until those chapters are included.

## Later-chapter checks

The two-chapter pilot does not validate the omitted figure 4.2, alternate
figure 7.1 assets, later EMF replacements, the chapter 8 table, or the
remaining notes and index entries. Each needs explicit reconciliation
during full extraction. The Spanish edition uses unchanged artwork,
including its existing English labels, with translated captions.

## Spanish pilot

The English extraction remains unchanged. Translation decisions and source
ambiguities are recorded in `spanish/notes/ch01-summary.md` and
`spanish/notes/ch02-summary.md`; these summaries are not part of the book.

## Chapter 3

English wording is preserved, including source scientific issues listed in
`spanish/notes/ch03-summary.md`. In particular, the convex/concave sign
association changes between paragraphs 242 and 293; the vacuum/flatness
statements, the curvature claim about sin(r)/r, and the asserted Einstein–Riemann
proportionality need author review. Equation 3.3 has υ in Word math but ν in
surrounding prose; that discrepancy remains visible in both editions.
Spanish note 2 corrects the evident equation-reference typo (3.3) to (3.2).

The nine native Word math objects consist of six mathematical displays and
three separately encoded equation numbers. LaTeX generates five numbered
equations and one unnumbered repeat; no mathematical content is lost.
Grey factors in 3.2 and 3.3 are retained, as the text expressly discusses them.
Figure 3.8 uses the embedded PNG to retain its dashed A–B line; the other
figures use the separate artwork. All source files remain unchanged.
