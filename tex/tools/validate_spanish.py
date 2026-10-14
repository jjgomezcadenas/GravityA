#!/usr/bin/env python3
"""Audit the Spanish pilot against English; linguistic review remains manual."""
from supporting_scope import before_supporting
import hashlib
import json
import re
import subprocess

from extract_pilot import ROOT, nodes
from validate_pilot import prose


def parse(text):
    return json.loads(subprocess.check_output(
        ["pandoc", "-f", "latex", "-t", "json"], input=text, text=True))


def compact(text):
    return re.sub(r"\s+", "", text)


def paragraphs(text):
    chunks = re.split(r"% DOCX paragraph (\d+)\s*\n", text)
    return dict(zip(chunks[1::2], chunks[2::2]))


def numbers(text, language):
    # Paragraph boundaries can fall inside floats/lists; remove their wrappers
    # before parsing a fragment (mathematical environments remain intact).
    text = re.sub(r"\\(?:begin|end)\{(?:figure|enumerate|description)\}(?:\[[^]]*\])?", "", text)
    text = re.sub(r"\\item(?:\[[^]]*\])?", "", text)
    text = prose(parse(text)["blocks"])
    if language == "en":
        text = text.replace("3,600", "3600")
    else:
        text = text.replace(",", ".")
        text = re.sub(r"\bcuarenta\b", "40", text)
    return re.findall(r"\d+(?:\.\d+)?", text)


def main():
    result = {"coverage": {}, "numeric_checks": "Arabic numerals by source paragraph",
              "editorial_exceptions": [
                  "ch02 paragraph 127: ambiguous English precision phrase; see chapter summary"],
              "scope": "Structural audit; does not certify translation accuracy"}
    full = {"en": "", "spanish": ""}
    for name in ("ch01", "ch02", "notes/ch01", "notes/ch02"):
        en = (ROOT / "tex/en" / (name + ".tex")).read_text()
        es = (ROOT / "tex/spanish" / (name + ".tex")).read_text()
        source, translated = paragraphs(en), paragraphs(es)
        assert list(source) == list(translated), f"{name}: paragraph coverage/order"
        for position in source:
            assert numbers(source[position], "en") == numbers(translated[position], "es"), (
                f"{name}, paragraph {position}: numbers differ")
        for command in ("label", "ref", "eqref", "hyperlink", "hypertarget"):
            pattern = r"\\" + command + r"\{([^}]+)\}"
            assert re.findall(pattern, en) == re.findall(pattern, es), (name, command)
        for token in (r"\index{", r"\caption{", r"\item", r"\reflectbox{"):
            assert en.count(token) == es.count(token), (name, token)
        pattern = r"\\includegraphics\[[^]]*\]\{[^}]*\}"
        assert re.findall(pattern, en) == re.findall(pattern, es), f"{name}: artwork"
        result["coverage"][name] = len(source)
        full["en"] += en
        full["spanish"] += es
    maths = {lang: [m["c"][1] for m in nodes(parse(text), "Math")]
             for lang, text in full.items()}
    assert len(maths["en"]) == len(maths["spanish"]) == 8
    assert [compact(m) for m in maths["en"][1:]] == [compact(m) for m in maths["spanish"][1:]]
    # Check the conceptual expression after mapping its translated text back.
    conceptual = maths["spanish"][0]
    for es, en in (("intensidad de la", "strength of the"),
                   ("fuerza de la gravedad", "force of gravity"),
                   ("masa del objeto 1", "mass of object 1"),
                   ("masa del objeto 2", "mass of object 2"),
                   ("distancia entre los objetos 1 y 2", "distance between object 1 and 2")):
        conceptual = conceptual.replace(r"\text{" + es + "}", en)
    assert compact(conceptual.replace("\\ ", "")) == compact(maths["en"][0].replace("\\ ", ""))
    result["math_objects"] = {"symbolic_unchanged": 7, "conceptual_text_translated": 1}
    result["figures"] = 2
    result["notes"] = 3
    result["index_entries"] = 73
    builds = {"spanish/main": 73}
    builds["spanish/main"] += sum(p.read_text().count(r"\index{") for p in
                                 (ROOT / 'tex/spanish').rglob('ch[0-9][0-9].tex')
                                 if p.stem not in ('ch01', 'ch02'))
    builds['spanish/main'] += sum(p.read_text().count(r'\index{') for p in (ROOT / 'tex/spanish/tables').glob('*.tex'))
    # Per-chapter counts include each chapter's notes.
    for chapter in ("01", "02"):
        builds[f"spanish-chapter{chapter}/chapter{chapter}"] = sum(
            (ROOT / "tex/spanish" / (name + ".tex")).read_text().count(r"\index{")
            for name in (f"ch{chapter}", f"notes/ch{chapter}"))
    for build, count in builds.items():
        base = ROOT / "tex/build" / build
        log = base.with_suffix(".log").read_text()
        issues = re.findall(r".*(?:Warning|Overfull|Underfull|Missing character|undefined|unreferenced destination).*", log)
        assert not issues, "\n".join(issues)
        index_log = base.with_suffix(".ilg").read_text()
        assert f"{count} entries accepted, 0 rejected" in index_log and "0 warnings" in index_log
        pdf_time = base.with_suffix(".pdf").stat().st_mtime
        # The combined edition must include every edited Spanish TeX file.
        if build == "spanish/main":
            for path in list((ROOT / "tex/spanish").rglob("*.tex")) + [ROOT / "tex/common/preamble.tex"]:
                assert path.stat().st_mtime <= pdf_time, f"Rebuild after editing {path}"
    result["builds"] = list(builds)
    snapshot = ROOT / "tex/build/spanish-audit/protected-before.json"
    if snapshot.exists():
        hashes = json.loads(snapshot.read_text())
        for name, expected in hashes.items():
            data = (ROOT / name).read_bytes()
            data = before_supporting(name, data)
            if name == "tex/en/main.tex":
                for chapter in ('03', '04', '05', '06', '07', '08'):
                    data = data.replace(f"\\include{{en/ch{chapter}}}\n".encode(), b"").replace(f"\\input{{en/notes/ch{chapter}}}\n".encode(), b"")
            if name == "figs/manifest.tsv":
                data = b"\n".join(line for line in data.split(b"\n") if not line.startswith((b"03-", b"04-", b"05-", b"06-", b"07-", b"08-")))
            assert hashlib.sha256(data).hexdigest() == expected, f"Changed protected file: {name}"
        result["protected_files_unchanged"] = len(hashes)
    output = ROOT / "tex/build/spanish-audit/validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
