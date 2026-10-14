#!/usr/bin/env python3
"""Extract the reviewed two-chapter boundary map. Never modify GA/.

Uses only the Python standard library and Pandoc. The paragraph numbers
are zero-based top-level w:body/w:p positions in the pinned source DOCX.
Regeneration is explicit because the resulting TeX is intended for editing.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "GA/english_version/attraction_wfigs.docx"
SOURCE_SHA256 = "cf359448c92b1c0cccea917d473469e77005ed3d0a48a6d906f458b0737b8010"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
}
W = "{" + NS["w"] + "}"
GROUPS = {
    "frontmatter": list(range(0, 40)),
    "introduction": list(range(40, 55)),
    "ch01": list(range(55, 110)),
    "ch02": list(range(110, 192)),
    "notes/ch01": [2012],
    "notes/ch02": [2017, 2018],
}
HEADINGS = {
    40: ("chapter*", "The Beginning of the Journey", "introduction"),
    55: ("chapter", "Gravity … Attracts!", "ch:01"),
    64: ("section", "Instinctive Knowledge", "sec:01-instinctive"),
    77: ("section", "Rational Knowledge", "sec:01-rational"),
    84: ("section", "Imaginative Knowledge", "sec:01-imaginative"),
    90: ("section", "One of Four, but Definitely Different from the Others", "sec:01-interactions"),
    101: ("section", "But What is Gravity, and How Does It Work?", "sec:01-gravity"),
    110: ("chapter", "The Fathers of Gravity", "ch:02"),
    116: ("section", "Galileo Galilei: The Importance of the Method", "sec:02-galileo"),
    131: ("section", "Isaac Newton: A Complete Mathematical Picture", "sec:02-newton"),
    181: ("section", "Albert Einstein: A Revolutionary Vision", "sec:02-einstein"),
}
FIGURES = {
    70: ("01-01", 71, "source/en/fig-01-01.jpg", "Fig_1.01.jpg", "V. Tverdokhlib/depositphotos.com"),
    170: ("02-01", 173, "pdf/en/fig-02-01.pdf", "Fig_2.01.svg", "No credit specified in source caption"),
}
# Deliberately explicit: other superscripts in chapter 2 are exponents.
CALLOUTS = {97: (1, 1), 159: (2, 1), 175: (2, 2)}
NOTE_PARAS = {2012: (1, 1), 2017: (2, 1), 2018: (2, 2)}


def text_of(p):
    return "".join(t.text or "" for t in p.iter(W + "t"))


def tex_escape(s):
    escapes = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
               "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
               "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(escapes.get(c, c) for c in s)


def run(s):
    r = ET.Element(W + "r")
    t = ET.SubElement(r, W + "t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = s
    return r


def paragraph(s):
    p = ET.Element(W + "p")
    p.append(run(s))
    return p


def strip_prefix(p, pattern):
    """Remove a literal prefix across Word runs without touching formatting."""
    match = re.match(pattern, text_of(p))
    if not match:
        raise ValueError(f"Missing expected prefix {pattern}: {text_of(p)[:80]}")
    remaining = match.end()
    for t in p.iter(W + "t"):
        s = t.text or ""
        take = min(remaining, len(s))
        t.text = s[take:]
        remaining -= take
        if not remaining:
            break


def nodes(o, kind):
    if isinstance(o, dict):
        if o.get("t") == kind:
            yield o
        for v in o.values():
            yield from nodes(v, kind)
    elif isinstance(o, list):
        for v in o:
            yield from nodes(v, kind)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="explicitly replace generated English pilot files")
    ap.add_argument("--audit-only", action="store_true", help="refresh source audit without changing editable TeX or artwork")
    args = ap.parse_args()
    outputs = [ROOT / "tex/en" / (g + ".tex") for g in GROUPS]
    if not args.force and not args.audit_only and any(p.exists() for p in outputs):
        ap.error("English pilot files already exist; review edits before using --force")
    original_bytes = SOURCE.read_bytes()
    source_hash = hashlib.sha256(original_bytes).hexdigest()
    assert source_hash == SOURCE_SHA256, "Source DOCX changed: review the extraction map before regeneration"
    # Register all original prefixes so mc:Ignorable keeps meaningful names.
    with ZipFile(io.BytesIO(original_bytes)) as archive:
        xml = archive.read("word/document.xml")
        for _, pair in ET.iterparse(io.BytesIO(xml), events=["start-ns"]):
            prefix, uri = pair
            if not re.fullmatch(r"ns\d+", prefix):
                ET.register_namespace(prefix, uri)
        document = ET.fromstring(xml)
        body = document.find("w:body", NS)
        source_paragraphs = body.findall("w:p", NS)
        assert len(source_paragraphs) == 2104, "Source structure changed: review boundary map"
        assert text_of(source_paragraphs[55]).strip() == "1 Gravity … Attracts!"
        assert text_of(source_paragraphs[110]).strip() == "2 The Fathers of Gravity"

        replacements = {}
        audit = {"source": str(SOURCE.relative_to(ROOT)), "sha256": source_hash,
                 "pandoc": subprocess.check_output(["pandoc", "--version"], text=True).splitlines()[0],
                 "scope": "front matter, introduction, chapters 1–2, corresponding notes",
                 "groups": {}, "index_entries": [], "note_callouts": [], "figures": []}

        def token(latex):
            key = f"GATOKEN{len(replacements):06d}END"
            replacements[key] = latex
            return key

        def indices(p, position):
            children = list(p)
            start = None
            buf = ""
            ranges = []
            for j, child in enumerate(children):
                for e in child.iter():
                    if e.tag == W + "fldChar":
                        t = e.get(W + "fldCharType")
                        if t == "begin":
                            assert start is None, "Nested fields require explicit handling"
                            start, buf = j, ""
                        elif t == "end":
                            assert start is not None
                            ranges.append((start, j, buf))
                            start = None
                    elif e.tag == W + "instrText":
                        buf += e.text or ""
            assert start is None, "Unclosed Word field"
            for a, b, instruction in reversed(ranges):
                match = re.fullmatch(r'\s*XE\s+"((?:\\.|[^"\\])*)"\s*(?:\\t\s+"([^"]*)"\s*)?', instruction)
                if not match:
                    raise ValueError(f"Unreviewed field at {position}: {instruction}")
                entry = match[1].replace(r'\"', '"')
                # MakeIndex uses ! for hierarchy and double quote as its escape.
                parts = []
                for part in entry.split(":"):
                    escaped = tex_escape(part)
                    escaped = re.sub(r'(["!@|])', r'"\1', escaped)
                    parts.append(escaped)
                see = ""
                if match[2]:
                    assert match[2].startswith("See "), instruction
                    see = "|see{" + tex_escape(match[2][4:]) + "}"
                latex = r"\index{" + "!".join(parts) + see + "}"
                audit["index_entries"].append({"paragraph": position, "entry": entry})
                for child in children[a:b + 1]:
                    p.remove(child)
                p.insert(a, run(token(latex)))

        all_blocks = []
        for group, positions in GROUPS.items():
            all_blocks.append(paragraph(f"GAGROUP{group.replace('/', 'ZZ')}END"))
            records = []
            for i in positions:
                original = source_paragraphs[i]
                p = copy.deepcopy(original)
                source_text = text_of(original)
                math_count = len(original.findall(".//m:oMath", NS))
                drawing_count = len(original.findall(".//w:drawing", NS))
                rec = {"paragraph": i, "source_text": source_text, "math_objects": math_count,
                       "drawings": drawing_count, "kind": "paragraph"}
                # The literal source title/credits are deliberately typeset below.
                if group == "frontmatter":
                    rec["kind"] = "frontmatter" if source_text.strip() else "blank"
                    records.append(rec)
                    continue
                if not source_text.strip() and not math_count and not drawing_count:
                    rec["kind"] = "blank"
                    records.append(rec)
                    continue
                indices(p, i)
                if i in HEADINGS:
                    command, title, label = HEADINGS[i]
                    latex = f"\\{command}{{{tex_escape(title)}}}\\label{{{label}}}\n"
                    if command.endswith("*"):
                        latex += f"\\addcontentsline{{toc}}{{chapter}}{{{tex_escape(title)}}}\n"
                    p = paragraph(token(latex))
                    rec["kind"] = "heading"
                elif i in FIGURES:
                    fid, cap, output, source, credit = FIGURES[i]
                    # Check the independent caption map before touching the artwork.
                    assert text_of(source_paragraphs[cap]).startswith("Fig. " + fid.replace("-", ".").replace("01.", "1.").replace("02.", "2.").replace(".01", ".1"))
                    width = "0.65" if fid == "01-01" else "0.82"
                    graphic = f"\\includegraphics[width={width}\\linewidth]{{../figs/{output}}}"
                    if fid == "01-01":
                        # The supplied colour JPEG is mirrored relative to the Word preview.
                        graphic = r"\reflectbox{" + graphic + "}"
                    p = paragraph(token("\\begin{figure}[htbp]\n\\centering\n"
                                        + graphic + "\n"))
                    rec["kind"] = "figure"
                    audit["figures"].append({"id": fid, "drawing_paragraph": i, "caption_paragraph": cap,
                                              "original": source, "output": output, "credit": credit})
                elif i in [v[1] for v in FIGURES.values()]:
                    fid = next(v[0] for v in FIGURES.values() if v[1] == i)
                    strip_prefix(p, r"Fig\.\s*\d+\.\d+\s+")
                    p.insert(1 if p.find("w:pPr", NS) is not None else 0, run(token(r"\caption{")))
                    p.append(run(token("}\\label{fig:" + fid + "}\n\\end{figure}\n")))
                    rec["kind"] = "caption"
                elif i == 157:
                    # Identified explicitly in the AST, retaining Pandoc's OMML conversion.
                    rec["kind"] = "equation"
                elif i in NOTE_PARAS:
                    chapter, number = NOTE_PARAS[i]
                    props = p.find("w:pPr", NS)
                    numbering = props.find("w:numPr", NS) if props is not None else None
                    if numbering is not None:
                        props.remove(numbering)
                    if i == 2012:
                        strip_prefix(p, r"1\s+")
                    p.insert(1 if props is not None else 0, run(token(
                        f"\\item[{number}.]\\hypertarget{{note:{chapter:02d}-{number:02d}}}{{}}")))
                    rec["kind"] = "note"
                if i in CALLOUTS:
                    chapter, number = CALLOUTS[i]
                    candidates = []
                    for child in p.findall("w:r", NS):
                        align = child.find("w:rPr/w:vertAlign", NS)
                        if align is not None and align.get(W + "val") == "superscript" and text_of(child) == str(number):
                            candidates.append(child)
                    assert len(candidates) == 1, (i, "ambiguous note callout")
                    old = candidates[0]
                    offset = list(p).index(old)
                    p.remove(old)
                    p.insert(offset, run(token(
                        r"\textsuperscript{\hyperlink{note:" + f"{chapter:02d}-{number:02d}"
                        + "}{" + str(number) + "}}")))
                    audit["note_callouts"].append({"paragraph": i, "chapter": chapter, "note": number})
                # Remove accidental heading/outline styles; reviewed headings are above.
                props = p.find("w:pPr", NS)
                if props is not None:
                    for tag in ["w:pStyle", "w:outlineLvl", "w:sectPr", "w:ind", "w:tabs"]:
                        e = props.find(tag, NS)
                        if e is not None:
                            props.remove(e)
                marker = f"GAPARA{i:06d}END"
                p.insert(1 if props is not None else 0, run(marker + " "))
                all_blocks.append(p)
                records.append(rec)
            audit["groups"][group] = records

        for child in list(body):
            body.remove(child)
        body.extend(all_blocks)
        with tempfile.TemporaryDirectory(prefix="gravitya-pilot-") as tmp:
            normalized = Path(tmp) / "normalized.docx"
            with ZipFile(normalized, "w", ZIP_DEFLATED) as out:
                for name in archive.namelist():
                    out.writestr(name, ET.tostring(document, encoding="utf-8", xml_declaration=True)
                                 if name == "word/document.xml" else archive.read(name))
            result = subprocess.run(["pandoc", str(normalized), "-f", "docx", "-t", "json"],
                                    check=True, text=True, capture_output=True)
            if result.stderr.strip():
                raise RuntimeError(result.stderr)
            ast = json.loads(result.stdout)

    expected_math = sum(r["math_objects"] for rows in audit["groups"].values() for r in rows)
    assert len(list(nodes(ast, "Math"))) == expected_math
    assert not list(nodes(ast, "Image")), "Drawing escaped the explicit figure map"
    # Keep an intermediate AST to make text/maths conversion inspectable.
    build = ROOT / "tex/build/audit"
    build.mkdir(parents=True, exist_ok=True)
    (build / "pilot-before-latex.json").write_text(json.dumps(ast, ensure_ascii=False, indent=2) + "\n")
    audit["math_objects"] = expected_math
    audit["index_entries"].sort(key=lambda e: e["paragraph"])
    audit["counts"] = {"figures": len(FIGURES), "notes": len(NOTE_PARAS),
                       "index_entries": len(audit["index_entries"]), "math_objects": expected_math}
    (build / "pilot-source-map.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    if args.audit_only:
        print("Refreshed source audit; editable TeX and artwork unchanged.")
        return

    selected = {}
    current = None
    for block in ast["blocks"]:
        strings = [x["c"] for x in nodes(block, "Str")]
        if len(strings) == 1 and re.fullmatch(r"GAGROUP.*END", strings[0]):
            current = strings[0][7:-3].replace("ZZ", "/")
            selected[current] = []
        else:
            assert current is not None
            selected[current].append(block)

    token_pattern = re.compile(r"(GATOKEN\d+END|GAPARA\d+END)")

    def convert(o):
        if isinstance(o, dict):
            if o.get("t") == "Str" and token_pattern.search(o["c"]):
                parts = []
                for part in token_pattern.split(o["c"]):
                    if part in replacements:
                        parts.append({"t": "RawInline", "c": ["latex", replacements[part]]})
                    elif re.fullmatch(r"GAPARA\d+END", part):
                        # Comments keep the editable TeX traceable to DOCX paragraphs.
                        parts.append({"t": "RawInline", "c": ["latex", f"\n% DOCX paragraph {int(part[6:-3])}\n"]})
                    elif part:
                        parts.append({"t": "Str", "c": part})
                return parts
            return {k: convert(v) for k, v in o.items()}
        if isinstance(o, list):
            result = []
            for child in o:
                value = convert(child)
                if isinstance(child, dict) and child.get("t") == "Str" and isinstance(value, list):
                    result.extend(value)
                else:
                    result.append(value)
            return result
        return o

    for group, blocks in selected.items():
        if group == "frontmatter":
            continue
        for k, block in enumerate(blocks):
            if any(s["c"] == "GAPARA000157END" for s in nodes(block, "Str")):
                math = list(nodes(block, "Math"))
                assert len(math) == 1
                blocks[k] = {"t": "RawBlock", "c": ["latex", "% DOCX paragraph 157\n"
                    + "\\begin{equation}\\label{eq:02-01}\n" + math[0]["c"][1] + "\n\\end{equation}"]}
        doc = {**ast, "blocks": convert(blocks)}
        result = subprocess.run(["pandoc", "-f", "json", "-t", "latex", "--wrap=auto", "--columns=88"],
                                input=json.dumps(doc), check=True, text=True, capture_output=True)
        if result.stderr.strip():
            raise RuntimeError(result.stderr)
        content = result.stdout
        assert not re.search(r"GA(?:TOKEN|PARA|GROUP)\d*", content)
        if group.startswith("notes/"):
            chapter = int(group[-2:])
            title = HEADINGS[55 if chapter == 1 else 110][1]
            content = (f"\\section*{{Chapter {chapter}: {tex_escape(title)}}}\n"
                       + "\\begin{description}[style=multiline,leftmargin=2em,labelwidth=1.5em]\n"
                       + content + "\n\\end{description}\n")
        # Source cross-references within the pilot can be linked safely.
        content = re.sub(r"(?i)(fig(?:ure)?\.?\s+)([12])\.1\b",
                         lambda m: m[1] + r"\ref{fig:0" + m[2] + "-01}", content)
        if group == "ch02":
            content = content.replace("(2.1)", r"\eqref{eq:02-01}")
        output = ROOT / "tex/en" / (group + ".tex")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("% Extracted from attraction_wfigs.docx; see PLAN.md and tools/extract_pilot.py.\n"
                          + content)

    # Reuse the source wording verbatim; typography is new.
    ps = source_paragraphs
    front = ("\\begin{titlepage}\n\\centering\n\\vspace*{1.5cm}\n"
             + "{\\Huge\\bfseries " + tex_escape(text_of(ps[2])) + "\\par}\n\\vspace{1cm}\n"
             + "{\\Large " + tex_escape(text_of(ps[5])) + "\\par}\n\\vspace{1.5cm}\n"
             + "{\\LARGE " + tex_escape(text_of(ps[8])) + "\\par}\n\\vfill\n"
             + tex_escape(text_of(ps[10])) + "\\par\n" + tex_escape(text_of(ps[12]))
             + "\\par\n\\end{titlepage}\n\\clearpage\n\\thispagestyle{empty}\n"
             + "\\vspace*{3cm}\n\\begin{center}\\itshape\n"
             + tex_escape(text_of(ps[20])) + "\\par\n" + tex_escape(text_of(ps[21]))
             + "\\par\n\\end{center}\n\\clearpage\n\\thispagestyle{empty}\n"
             + "\\vspace*{3cm}\n\\begin{center}\\itshape\n"
             + tex_escape(text_of(ps[31])) + "\\par\n" + tex_escape(text_of(ps[32]))
             + "\\par\n\\end{center}\n\\clearpage\n")
    (ROOT / "tex/en/frontmatter.tex").write_text("% Source DOCX paragraphs 2–32.\n" + front)
    for _, (fid, _, output, original, credit) in FIGURES.items():
        dest = ROOT / "figs/source/en" / ("fig-" + fid + Path(original).suffix)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "GA/english_version/figs" / original, dest)
    manifest = "id\tsource\tprepared_asset\tcaption_paragraph\tcredit\ttransform\tstatus\n"
    for _, (fid, cap, output, original, credit) in FIGURES.items():
        transform = "horizontal reflection in LaTeX to match DOCX; retain source colour" if fid == "01-01" else "export drawing bounds; text to paths; retain source colour"
        manifest += f"{fid}\tGA/english_version/figs/{original}\tfigs/{output}\t{cap}\t{credit}\t{transform}\tmatched to embedded DOCX image; original artwork colour retained\n"
    (ROOT / "figs/manifest.tsv").write_text(manifest)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
    print(json.dumps(audit["counts"], indent=2))


if __name__ == "__main__":
    main()
