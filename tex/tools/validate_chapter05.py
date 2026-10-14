#!/usr/bin/env python3
"""Audit chapter 5 extraction, translated coverage, inline notation and builds."""
from supporting_scope import before_supporting
import hashlib
import json
import re
from extract_pilot import ROOT, nodes
from extract_chapter05 import extract
from validate_pilot import prose, normalize
from validate_spanish import paragraphs, parse

INDEX = r'\\index\{((?:[^{}]|\{[^{}]*\})*)\}'
GRAPHIC = r'\\includegraphics\[[^]]+\]\{([^}]+)\}'


def prose_numbers(text, language):
    text = re.sub(r'\\(?:begin|end)\{(?:figure|description)\}(?:\[[^]]*\])?', '', text)
    text = re.sub(r'\\item\[[^]]*\]', '', text).replace(r'\,', '')
    s = prose(parse(text)['blocks'])
    if language == 'en':
        s = re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))', '', s)
    else:
        s = s.replace(',', '.')
    return re.findall(r'\d+(?:\.\d+)?', s)


def main():
    extract()  # Refresh only the audit; never overwrite the English chapter.
    directory = ROOT / 'tex/build/ch05-audit'
    source = json.loads((directory / 'source-map.json').read_text())
    en = '\n'.join((ROOT / 'tex/en' / f'{name}.tex').read_text() for name in ('ch05', 'notes/ch05'))
    es = '\n'.join((ROOT / 'tex/spanish' / f'{name}.tex').read_text() for name in ('ch05', 'notes/ch05'))
    expected = []
    for pos, record in source['paragraphs'].items():
        s = record['source_text']
        if pos == '455':
            s = s.removeprefix('5 ')
        if int(pos) >= 2039:
            s = re.sub(r'^\d+\.?\s*', '', s)
        s = re.sub(r'^Fig\.\s*5\.\d+\s+', '', s)
        expected.append(s)
    t = re.sub(r'\\ref\{fig:05-(\d+)\}', lambda m: f'5.{int(m[1])}', en)
    t = re.sub(r'\\section\*\{Chapter 5:[^}]+\}', '', t)
    a, b = normalize(''.join(expected)), normalize(prose(parse(t)['blocks']))
    if a != b:
        i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        raise AssertionError(f'English differs from DOCX at {i}:\n{a[max(0,i-50):i+100]}\n{b[max(0,i-50):i+100]}')
    enp, esp = paragraphs(en), paragraphs(es)
    assert list(enp) == list(esp) == list(source['paragraphs']), 'Paragraph coverage/order'
    assert len(enp) == 138
    for command in ('label', 'ref', 'eqref', 'hyperlink', 'hypertarget'):
        pattern = r'\\' + command + r'\{([^}]+)\}'
        assert re.findall(pattern, en) == re.findall(pattern, es), command
    assert en.count(r'\index{') == es.count(r'\index{') == len(source['index_entries']) == 235
    assert en.count(r'\caption{') == es.count(r'\caption{') == 6
    assert en.count(r'\begin{equation}') == es.count(r'\begin{equation}') == 0
    assert en.count(r'\hypertarget{note:') == es.count(r'\hypertarget{note:') == 14
    assert en.count(r'\hyperlink{note:') == es.count(r'\hyperlink{note:') == 15
    assert re.findall(GRAPHIC.replace('([^}]+)', '[^}]+'), en) == re.findall(GRAPHIC.replace('([^}]+)', '[^}]+'), es)
    for path in re.findall(GRAPHIC, en):
        assert (ROOT / 'tex' / path).is_file(), path
    assert not source['math']
    assert not list(nodes(parse(en), 'Math')) and not list(nodes(parse(es), 'Math'))
    errors = []
    for pos in enp:
        a, b = enp[pos], esp[pos]
        if pos == '573':
            a = a.replace('30,000 billion', 'treinta billones')
        assert len(re.findall(INDEX, a)) == len(re.findall(INDEX, b)), ('index coverage', pos)
        # Word uses ordinary styled text for this chapter's formulas/powers.
        power = r'\\textsuperscript\{(-?\d+)\}'
        assert re.findall(power, a) == re.findall(power, b), ('exponents', pos)
        an, bn = prose_numbers(a, 'en'), prose_numbers(b, 'es')
        if pos == '487':
            # The caption reference and source name swap order in fluent Spanish.
            an, bn = sorted(an), sorted(bn)
        if an != bn:
            errors.append((pos, an, bn))
    assert not errors, errors
    for expression in (r'\emph{λ = c / f}', r'\emph{R \textless{} c ΔT}'):
        assert expression in en and expression in es, expression
    assert es.count(r'\emph{M/R}') == en.count(r'\emph{M/R}') == 2
    logs = {}
    for build, lang in [('chapter05', 'en'), ('spanish-chapter05', 'spanish')]:
        base = ROOT / 'tex/build' / build / 'chapter05'
        log = base.with_suffix('.log').read_text()
        issues = re.findall(r'.*(?:Warning|Overfull|Underfull|Missing character|undefined|unreferenced destination).*', log)
        assert not issues, '\n'.join(issues)
        idx = base.with_suffix('.ilg').read_text()
        assert '235 entries accepted, 0 rejected' in idx and '0 warnings' in idx
        inputs = [ROOT / f'tex/{lang}/{f}.tex' for f in ('ch05', 'notes/ch05', 'chapter05')]
        inputs += [ROOT / 'tex/common/preamble.tex']
        inputs += [ROOT / 'tex' / p for p in re.findall(GRAPHIC, en)]
        assert all(p.stat().st_mtime <= base.with_suffix('.pdf').stat().st_mtime for p in inputs), 'Stale PDF'
        logs[build] = 'clean'
    snapshot = json.loads((directory / 'protected-before.json').read_text())
    for name, digest in snapshot.items():
        data = (ROOT / name).read_bytes()
        data = before_supporting(name, data)
        if name in ('tex/en/main.tex', 'tex/spanish/main.tex'):
            lang = name.split('/')[1]
            for chapter in ('05', '06', '07', '08'):
                data = data.replace(f'\\include{{{lang}/ch{chapter}}}\n'.encode(), b'').replace(f'\\input{{{lang}/notes/ch{chapter}}}\n'.encode(), b'')
        if name == 'figs/manifest.tsv':
            data = b'\n'.join(line for line in data.split(b'\n') if not line.startswith((b'05-', b'06-', b'07-', b'08-')))
        assert hashlib.sha256(data).hexdigest() == digest, f'Protected file changed: {name}'
    result = {'english_matches_docx': True, 'paragraphs': len(enp), 'figures': 6,
              'numbered_equations': 0, 'notes': 14, 'note_callouts': 15,
              'source_math_objects': 0, 'inline_notation': 'Exponents, formulas and values preserved',
              'index_entries': 235, 'builds': logs, 'protected_files_checked': len(snapshot),
              'exceptions': ['English short-scale numbers translated into Spanish long scale'],
              'scope': 'Mechanical checks complement manual translation and visual review.'}
    (directory / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
