#!/usr/bin/env python3
"""Audit chapter 6 extraction, translated coverage, inline notation and builds."""
from supporting_scope import before_supporting
import hashlib
import json
import re
from extract_pilot import ROOT, nodes
from extract_chapter06 import extract
from validate_pilot import prose, normalize
from validate_spanish import paragraphs, parse

INDEX = r'\\index\{((?:[^{}]|\{[^{}]*\})*)\}'
GRAPHIC = r'\\includegraphics\[[^]]+\]\{([^}]+)\}'


def math_content(text):
    """Ignore reviewed typesetting differences, but retain math tokens and values."""
    for es, en in [('Sol', 'Sun'), ('estrella ultracompacta', 'ultra-compact star'), ('agujero negro', 'black hole')]:
        text = text.replace(es, en)
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = text.replace(r'\begin{array}{@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}}', '')
    text = re.sub(r'\\begin\{array\}\{c@\{[^}]+\}c@\{[^}]+\}c\}', '', text)
    text = re.sub(r'\\(?:begin|end)\{(?:equation|gathered|array)\}', '', text)
    text = text.replace(r'\textcolor{gray}', '')
    text = re.sub(r'\\(?:text|mathrm)\{([^}]+)\}', r'\1', text)
    text = text.replace('{,}', '.')
    text = text.replace(r'\\', '').replace(r'\,', '').replace(r'\ ', '').replace('&', '')
    return re.sub(r'[\s{}]', '', text)


def prose_numbers(text, language):
    text = re.sub(r'\\(?:begin|end)\{(?:figure|description|enumerate|itemize)\}(?:\[[^]]*\])?', '', text)
    text = re.sub(r'\\item(?:\[[^]]*\])?', '', text).replace(r'\,', '')
    text = re.sub(r'\\textsuperscript\{\\hyperlink\{[^}]+\}\{\d+\}\}', ' ', text)
    s = prose(parse(text)['blocks'])
    if language == 'en':
        s = re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))', '', s)
    else:
        s = s.replace(',', '.')
    return re.findall(r'\d+(?:\.\d+)?', s)


def main():
    extract()  # Refresh only the audit; never overwrite the English chapter.
    directory = ROOT / 'tex/build/ch06-audit'
    source = json.loads((directory / 'source-map.json').read_text())
    en = '\n'.join((ROOT / 'tex/en' / f'{name}.tex').read_text() for name in ('ch06', 'notes/ch06'))
    es = '\n'.join((ROOT / 'tex/spanish' / f'{name}.tex').read_text() for name in ('ch06', 'notes/ch06'))
    expected = []
    for pos, record in source['paragraphs'].items():
        s = record['source_text']
        if pos == '626':
            s = s.removeprefix('6')
        if pos in ('652', '721'):
            s = ''
        if int(pos) >= 2057:
            s = re.sub(r'^\d+\.?\s*', '', s)
        s = re.sub(r'^Fig\.\s*6\.\d+\s+', '', s)
        expected.append(s)
    t = re.sub(r'\\ref\{fig:06-(\d+)\}', lambda m: f'6.{int(m[1])}', en)
    t = re.sub(r'\\eqref\{eq:06-(\d+)\}', lambda m: f'(6.{int(m[1])})', t)
    t = t.replace(r'\textsubscript{\(\star\)}', r'\textsubscript{★}')
    t = re.sub(r'\\section\*\{Chapter 6:[^}]+\}', '', t)
    a, b = normalize(''.join(expected)), normalize(prose(parse(t)['blocks']))
    if a != b:
        i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        raise AssertionError(f'English differs from DOCX at {i}:\n{a[max(0,i-50):i+100]}\n{b[max(0,i-50):i+100]}')
    enp, esp = paragraphs(en), paragraphs(es)
    assert list(enp) == list(esp) == list(source['paragraphs']), 'Paragraph coverage/order'
    assert len(enp) == 152
    for command in ('label', 'ref', 'eqref', 'hyperlink', 'hypertarget'):
        pattern = r'\\' + command + r'\{([^}]+)\}'
        assert re.findall(pattern, en) == re.findall(pattern, es), command
    assert en.count(r'\index{') == es.count(r'\index{') == len(source['index_entries']) == 223
    assert en.count(r'\caption{') == es.count(r'\caption{') == 3
    assert en.count(r'\begin{equation}') == es.count(r'\begin{equation}') == 3
    assert en.count(r'\hypertarget{note:') == es.count(r'\hypertarget{note:') == 10
    assert en.count(r'\hyperlink{note:') == es.count(r'\hyperlink{note:') == 11
    assert re.findall(GRAPHIC.replace('([^}]+)', '[^}]+'), en) == re.findall(GRAPHIC.replace('([^}]+)', '[^}]+'), es)
    for path in re.findall(GRAPHIC, en):
        assert (ROOT / 'tex' / path).is_file(), path
    em = [m['c'][1] for m in nodes(parse(en), 'Math')]
    sm = [m['c'][1] for m in nodes(parse(es), 'Math')]
    original = [m for m in source['math'] if m != '(6.2)']
    substantive = [m for m in em if m != r'\star']
    assert len(em) == len(sm) == 13
    assert len(substantive) == len(original) == 6
    for i, (a, b) in enumerate(zip(original, substantive)):
        assert math_content(a) == math_content(b), ('source math', i, math_content(a), math_content(b))
    for i, (a, b) in enumerate(zip(em, sm)):
        assert math_content(a) == math_content(b), ('translated math', i, math_content(a), math_content(b))
    errors = []
    for pos in enp:
        a, b = enp[pos], esp[pos]
        if pos == '762':
            a = a.replace('1970s', 'años setenta')
        assert len(re.findall(INDEX, a)) == len(re.findall(INDEX, b)), ('index coverage', pos)
        # Word uses ordinary styled text for this chapter's formulas/powers.
        power = r'\\textsuperscript\{(-?\d+)\}'
        assert re.findall(power, a) == re.findall(power, b), ('exponents', pos)
        an, bn = prose_numbers(a, 'en'), prose_numbers(b, 'es')
        if an != bn:
            errors.append((pos, an, bn))
    assert not errors, errors
    logs = {}
    for build, lang in [('chapter06', 'en'), ('spanish-chapter06', 'spanish')]:
        base = ROOT / 'tex/build' / build / 'chapter06'
        log = base.with_suffix('.log').read_text()
        issues = re.findall(r'.*(?:Warning|Overfull|Underfull|Missing character|undefined|unreferenced destination).*', log)
        assert not issues, '\n'.join(issues)
        idx = base.with_suffix('.ilg').read_text()
        assert '223 entries accepted, 0 rejected' in idx and '0 warnings' in idx
        inputs = [ROOT / f'tex/{lang}/{f}.tex' for f in ('ch06', 'notes/ch06', 'chapter06')]
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
            for chapter in ('06', '07', '08'):
                data = data.replace(f'\\include{{{lang}/ch{chapter}}}\n'.encode(), b'').replace(f'\\input{{{lang}/notes/ch{chapter}}}\n'.encode(), b'')
        if name == 'figs/manifest.tsv':
            data = b'\n'.join(line for line in data.split(b'\n') if not line.startswith((b'06-', b'07-', b'08-')))
        assert hashlib.sha256(data).hexdigest() == digest, f'Protected file changed: {name}'
    result = {'english_matches_docx': True, 'paragraphs': len(enp), 'figures': 3,
              'numbered_equations': 3, 'notes': 10, 'note_callouts': 11,
              'source_math_objects': 7, 'inline_notation': 'Exponents, formulas and values preserved',
              'index_entries': 223, 'builds': logs, 'protected_files_checked': len(snapshot),
              'exceptions': ['Three equation numbers generated by LaTeX; Word star subscripts rendered in math',
                             '1970s rendered as años setenta; decimal commas and thin thousands spacing',
                             'Spanish typographic repairs documented in chapter summary'],
              'scope': 'Mechanical checks complement manual translation and visual review.'}
    (directory / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
