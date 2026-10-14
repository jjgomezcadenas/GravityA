#!/usr/bin/env python3
"""Compare the editable pilot TeX to the authoritative DOCX and build logs.

This is a content audit, not a pixel comparison: whitespace and typographic
quotes/dashes are normalized; mathematical notation is checked separately.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from extract_pilot import ROOT, SOURCE, SOURCE_SHA256, GROUPS, HEADINGS, FIGURES, NS, text_of, nodes


def prose(o):
    if isinstance(o, list):
        return "".join(prose(x) for x in o)
    if not isinstance(o, dict):
        return ""
    t, c = o.get("t"), o.get("c")
    if t == "Str":
        return c
    if t in ("Space", "SoftBreak", "LineBreak"):
        return " "
    if t in ("Math", "Image", "RawInline", "RawBlock"):
        return ""
    if t == "Header":
        return prose(c[2])
    if t in ("Link", "Span", "Cite"):
        return prose(c[1])
    if t == "Quoted":
        return '"' + prose(c[1]) + '"'
    if t == "OrderedList":
        return prose(c[1])
    if t == "Figure":
        return prose(c[1][1])
    if t == "DefinitionList":
        return "".join(prose(body) for _, body in c)
    return prose(c)


def normalize(s):
    s = unicodedata.normalize("NFC", s)
    # Pandoc normalizes prose typography, but the words and numbers must survive.
    s = s.replace("…", "...").replace("—", "-").replace("–", "-")
    s = re.sub(r'[\s\u00ad\'"‘’“”]', '', s)
    return s


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    archive_hashes = json.loads((ROOT / "tex/tools/source-hashes.json").read_text())
    actual_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (ROOT / "GA").rglob("*") if p.is_file()}
    assert actual_hashes == archive_hashes, "GA source archive has changed"
    subprocess.run([sys.executable, str(ROOT / "tex/tools/extract_pilot.py"), "--audit-only"], check=True)
    with ZipFile(SOURCE) as z:
        ps = ET.fromstring(z.read("word/document.xml")).findall("w:body/w:p", NS)
    audit = json.loads((ROOT / "tex/build/audit/pilot-source-map.json").read_text())
    result = {"source_sha256": SOURCE_SHA256, "prose_comparison": {}, "counts": audit["counts"]}
    result["archive_files_unchanged"] = len(archive_hashes)
    all_tex = ""
    for group, positions in GROUPS.items():
        content = (ROOT / "tex/en" / (group + ".tex")).read_text()
        all_tex += content
        # Resolve known references for text comparison independently of PDF layout.
        content = content.replace(r"\ref{fig:01-01}", "1.1").replace(r"\ref{fig:02-01}", "2.1")
        content = content.replace(r"\eqref{eq:02-01}", "(2.1)")
        a = json.loads(subprocess.check_output(["pandoc", "-f", "latex", "-t", "json"], input=content, text=True))
        blocks = a["blocks"]
        if group.startswith("notes/"):
            blocks = [b for b in blocks if b["t"] != "Header"]
        actual = normalize(prose(blocks))
        expected = []
        for i in positions:
            s = text_of(ps[i])
            if i in HEADINGS:
                s = re.sub(r"^[12]\s+", "", s)
            if i in [v[1] for v in FIGURES.values()]:
                s = re.sub(r"^Fig\.\s*\d+\.\d+\s+", "", s)
            if i == 2012:
                s = re.sub(r"^1\s+", "", s)
            if i == 157:
                s = ""  # Equation number is regenerated; math is checked below.
            expected.append(s)
        expected = normalize("".join(expected))
        if actual != expected:
            index = next((i for i, (x, y) in enumerate(zip(expected, actual)) if x != y), min(len(expected), len(actual)))
            raise AssertionError(f"{group}: prose differs at {index}\nSOURCE: {expected[max(0,index-40):index+100]}\nTEX:    {actual[max(0,index-40):index+100]}")
        result["prose_comparison"][group] = {"normalized_characters": len(actual), "status": "identical"}

    assert all_tex.count(r"\index{") == audit["counts"]["index_entries"] == 73
    assert all_tex.count(r"\includegraphics[") == 2
    assert all_tex.count(r"\caption{") == 2
    assert all_tex.count(r"\hyperlink{note:") == all_tex.count(r"\hypertarget{note:") == 3
    source_math = json.loads((ROOT / "tex/build/audit/pilot-before-latex.json").read_text())
    original_math = [m["c"][1] for m in nodes(source_math, "Math")]
    assert len(original_math) == 8
    # All converted mathematical expressions must be present literally, modulo wrapping.
    compact_tex = re.sub(r"\s+", "", all_tex)
    for expression in original_math:
        assert re.sub(r"\s+", "", expression) in compact_tex, expression
    log = (ROOT / "tex/build/en/main.log").read_text()
    pdf_mtime = (ROOT / "tex/build/en/main.pdf").stat().st_mtime
    for path in [ROOT / "tex/en" / (group + ".tex") for group in GROUPS] + [
            ROOT / "tex/en/main.tex", ROOT / "tex/common/preamble.tex", ROOT / "figs/pdf/en/fig-02-01.pdf"]:
        assert path.stat().st_mtime <= pdf_mtime, f"Rebuild the PDF after editing {path}"
    problems = re.findall(r".*(?:Warning|Overfull|Missing character|undefined|unreferenced destination).*", log)
    assert not problems, "\n".join(problems)
    idx = (ROOT / "tex/build/en/main.ilg").read_text()
    extra = sum(p.read_text().count(r"\index{") for p in
                (ROOT / 'tex/en').rglob('ch[0-9][0-9].tex') if p.stem not in ('ch01', 'ch02'))
    extra += sum(p.read_text().count(r'\index{') for p in (ROOT / 'tex/en/tables').glob('*.tex'))
    assert f"{73 + extra} entries accepted, 0 rejected" in idx and "0 warnings" in idx
    for f in audit["figures"]:
        assert (ROOT / "figs" / f["output"]).is_file()
    result["math_objects_preserved"] = len(original_math)
    result["latex_warnings"] = problems
    result["index"] = f"73 pilot entries; {73 + extra} in combined book; none rejected; no warnings"
    (ROOT / "tex/build/audit/pilot-validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
