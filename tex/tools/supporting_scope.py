"""Remove only the newly authorized supporting-material driver inclusions.

Used when checking snapshots taken before these sections were added.
"""
import json
from pathlib import Path


def before_book_review(name, data):
    """Undo only recorded Spanish review edits for historical snapshot checks."""
    edits = json.loads(Path(__file__).with_name('book_review_edits.json').read_text())
    for edit in reversed(edits):
        if edit['file'] == name:
            old, new = edit['before'].encode(), edit['after'].encode()
            count = edit.get('count', 1)
            assert data.count(new) == count, f'Reviewed wording changed: {name}'
            data = data.replace(new, old, count)
    return data


def before_supporting(name, data):
    data = before_book_review(name, data)
    if name not in ('tex/en/main.tex', 'tex/spanish/main.tex'):
        return data
    data = before_frontmatter(name, data)
    language = name.split('/')[1]
    sections = ['conclusion', 'acknowledgements']
    if language == 'spanish':
        sections.insert(0, 'introduction')
    for section in sections:
        data = data.replace(f'\\include{{{language}/{section}}}\n'.encode(), b'')
    return data


def before_frontmatter(name, data):
    """Restore only the former title block for historical snapshot checks."""
    if name == "tex/spanish/main.tex":
        data = data.replace(b"\\input{spanish/frontmatter}\n", b'\\begin{titlepage}\n\\centering\n\\vspace*{2cm}\n{\\Huge La irresistible atracci\xc3\xb3n\\par de la gravedad\\par}\n\\vspace{1cm}\n{\\Large Un viaje para descubrir los agujeros negros\\par}\n\\vspace{2cm}\n{\\Large Luciano Rezzolla\\par}\n\\end{titlepage}\n')
    return data
