#!/usr/bin/env python3
"""Audit chapter 7 extraction, translated coverage, inline notation and builds."""
from supporting_scope import before_supporting
import hashlib
import json
import re
from extract_pilot import ROOT, nodes
from extract_chapter07 import extract
from validate_pilot import prose, normalize
from validate_spanish import paragraphs, parse

INDEX = r'\\index\{((?:[^{}]|\{[^{}]*\})*)\}'
GRAPHIC = r'\\includegraphics\[[^]]+\]\{([^}]+)\}'


def math_content(text):
    """Ignore reviewed typesetting differences, but retain math tokens and values."""
    for es, en in [('resolución angular de la', 'angular resolution of'), ('imagen astronómica', 'astronomical image'), ('longitud de onda de las observaciones', 'wavelength of observations'), ('tamaño del telescopio', 'telescope size')]:
        text = text.replace(es, en)
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = re.sub(r'\\(?:begin|end)\{(?:equation|pmatrix)\}', '', text)
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    text = text.replace(r'\binom', '').replace(r'\left', '').replace(r'\right', '')
    text = text.replace('{,}', '.').replace(r'\\', '').replace(r'\ ', '').replace(r'\,', '')
    return re.sub(r'[\s{}()]', '', text)


def prose_numbers(text, language):
    text = re.sub(r'\\(?:begin|end)\{(?:figure|description|enumerate|itemize)\}(?:\[[^]]*\])?', '', text)
    text = re.sub(r'\\item(?:\[[^]]*\])?', '', text).replace(r'\,', '')
    text = re.sub(r'\\textsuperscript\{\\hyperlink\{[^}]+\}\{\d+\}\}', ' ', text)
    if r'\caption{' in text:
        text = r'\begin{figure}' + text + r'\end{figure}'
    s = prose(parse(text)['blocks'])
    if language == 'en':
        s = re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))', '', s)
    else:
        s = s.replace(',', '.')
    return re.findall(r'\d+(?:\.\d+)?', s)


def main():
    extract()  # Refresh only the audit; never overwrite the English chapter.
    directory = ROOT / 'tex/build/ch07-audit'
    source = json.loads((directory / 'source-map.json').read_text())
    en = '\n'.join((ROOT / 'tex/en' / f'{name}.tex').read_text() for name in ('ch07', 'notes/ch07'))
    es = '\n'.join((ROOT / 'tex/spanish' / f'{name}.tex').read_text() for name in ('ch07', 'notes/ch07'))
    expected = []
    for pos, record in source['paragraphs'].items():
        s = record['source_text']
        if pos == '828':
            s = s.removeprefix('7')
        if pos in ('864', '905'):
            s = ''
        if int(pos) >= 2071:
            s = re.sub(r'^\d+\.?\s*', '', s)
        s = re.sub(r'^Fig\.\s*7\.\d+\s+', '', s)
        expected.append(s)
    t = re.sub(r'\\ref\{fig:07-(\d+)\}', lambda m: f'7.{int(m[1])}', en)
    t = re.sub(r'\\eqref\{eq:07-(\d+)\}', lambda m: f'(7.{int(m[1])})', t)
    t = t.replace(r'\textsubscript{\(\star\)}', r'\textsubscript{★}')
    t = re.sub(r'\\section\*\{Chapter 7:[^}]+\}', '', t)
    a, b = normalize(''.join(expected)), normalize(prose(parse(t)['blocks']))
    if a != b:
        i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        raise AssertionError(f'English differs from DOCX at {i}:\n{a[max(0,i-50):i+100]}\n{b[max(0,i-50):i+100]}')
    enp, esp = paragraphs(en), paragraphs(es)
    assert list(enp) == list(esp) == list(source['paragraphs']), 'Paragraph coverage/order'
    assert len(enp) == 213
    for command in ('label', 'ref', 'eqref', 'hyperlink', 'hypertarget'):
        pattern = r'\\' + command + r'\{([^}]+)\}'
        assert re.findall(pattern, en) == re.findall(pattern, es), command
    assert en.count(r'\index{') == es.count(r'\index{') == len(source['index_entries']) == 253
    assert en.count(r'\caption{') == es.count(r'\caption{') == 15
    assert en.count(r'\begin{equation}') == es.count(r'\begin{equation}') == 1
    assert en.count(r'\hypertarget{note:') == es.count(r'\hypertarget{note:') == 11
    assert en.count(r'\hyperlink{note:') == es.count(r'\hyperlink{note:') == 11
    assert re.findall(GRAPHIC.replace('([^}]+)', '[^}]+'), en) == re.findall(GRAPHIC.replace('([^}]+)', '[^}]+'), es)
    for path in re.findall(GRAPHIC, en):
        assert (ROOT / 'tex' / path).is_file(), path
    em = [m['c'][1] for m in nodes(parse(en), 'Math')]
    sm = [m['c'][1] for m in nodes(parse(es), 'Math')]
    original = [m for m in source['math'] if m != '(7.1)']
    assert len(em) == len(sm) == len(original) == 4
    for i, (a, b) in enumerate(zip(original, em)):
        assert math_content(a) == math_content(b), ('source math', i, math_content(a), math_content(b))
    for i, (a, b) in enumerate(zip(em, sm)):
        assert math_content(a) == math_content(b), ('translated math', i, math_content(a), math_content(b))
    errors = []
    for pos in enp:
        a, b = enp[pos], esp[pos]
        if pos == '930':
            a = a.replace('1970s', 'años setenta')
        if pos == '838':
            a = a.replace('4.5 billion', '4500 million')
        if pos == '1044':
            a = a.replace('6.5 billion', '6500 million')
        assert len(re.findall(INDEX, a)) == len(re.findall(INDEX, b)), ('index coverage', pos)
        if '©' in a:
            ac = prose(parse(r'\begin{figure}' + a)['blocks']).split('©', 1)[1]
            bc = prose(parse(r'\begin{figure}' + b)['blocks']).split('©', 1)[1]
            assert normalize(ac) == normalize(bc), ('figure credit', pos)
        # Word uses ordinary styled text for this chapter's formulas/powers.
        power = r'\\textsuperscript\{(-?\d+)\}'
        assert re.findall(power, a) == re.findall(power, b), ('exponents', pos)
        an, bn = prose_numbers(a, 'en'), prose_numbers(b, 'es')
        if pos == '835':
            # Spanish places M87* before the wavelength in this caption.
            assert an == ['1.3', '87'] and bn == ['87', '1.3']
            bn = list(reversed(bn))
        if an != bn:
            errors.append((pos, an, bn))
    assert not errors, errors
    logs = {}
    for build, lang in [('chapter07', 'en'), ('spanish-chapter07', 'spanish')]:
        base = ROOT / 'tex/build' / build / 'chapter07'
        log = base.with_suffix('.log').read_text()
        issues = re.findall(r'.*(?:Warning|Overfull|Underfull|Missing character|undefined|unreferenced destination).*', log)
        assert not issues, '\n'.join(issues)
        idx = base.with_suffix('.ilg').read_text()
        assert '253 entries accepted, 0 rejected' in idx and '0 warnings' in idx
        inputs = [ROOT / f'tex/{lang}/{f}.tex' for f in ('ch07', 'notes/ch07', 'chapter07')]
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
            for chapter in ('07', '08'):
                data = data.replace(f'\\include{{{lang}/ch{chapter}}}\n'.encode(), b'').replace(f'\\input{{{lang}/notes/ch{chapter}}}\n'.encode(), b'')
        if name == 'figs/manifest.tsv':
            data = b'\n'.join(line for line in data.split(b'\n') if not line.startswith((b'07-', b'08-')))
        assert hashlib.sha256(data).hexdigest() == digest, f'Protected file changed: {name}'
    assert re.search(r'\\centering\s+non-rotating\\par\\medskip', en)
    assert re.search(r'\\centering\s+sin rotación\\par\\medskip', es)
    result = {'english_matches_docx': True, 'paragraphs': len(enp), 'figures': 15,
              'numbered_equations': 1, 'notes': 11, 'note_callouts': 11,
              'source_math_objects': 5, 'rendered_math_objects': 4,
              'index_entries': 253, 'builds': logs, 'protected_files_checked': len(snapshot),
              'exceptions': ['Equation number generated by LaTeX; literal Word √27 rendered as a square root',
                             '1970s rendered as años setenta; decimal commas, thin thousands spacing and billion scale translated',
                             'External Word figure label translated separately from unchanged artwork'],
              'scope': 'Mechanical checks complement manual translation and visual review.'}
    (directory / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
