#!/usr/bin/env python3
"""Final review checks supplement the existing chapter/source audits."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

from make_spanish_index import normalize
from supporting_scope import before_book_review

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'tex/build/book-review'


def main():
    snapshot = json.loads((AUDIT / 'protected-before.json').read_text())
    for name, digest in snapshot.items():
        data = before_book_review(name, (ROOT / name).read_bytes())
        assert hashlib.sha256(data).hexdigest() == digest, name

    base = ROOT / 'tex/build/spanish/main'
    raw = base.with_suffix('.idx').read_text()
    assert normalize(raw) == base.with_suffix('.sorted.idx').read_text()
    assert normalize(normalize(raw)) == normalize(raw)
    entries = re.findall(r'^\\indexentry\{(.*)\}\{([^{}]+)\}$', raw, re.M)
    assert len(entries) == 1218
    paths = set()
    references = []
    for entry, page in entries:
        levels = tuple(x.rsplit('@', 1)[-1] for x in entry.split('|', 1)[0].split('!'))
        paths.update(levels[:i] for i in range(1, len(levels) + 1))
        references.extend(re.findall(r'\\see\{([^}]+)\}', entry))
    for target in references:
        assert tuple(target.split(', ')) in paths, ('Index reference', target)

    # Read generated index text, not page images. No split duplicate headings.
    headings = []
    parent = None
    for kind, text in re.findall(r'\\(item|subitem) ([^\n]+)', base.with_suffix('.ind').read_text()):
        heading = re.split(r',\s*\\', text)[0].rstrip(', ')
        if kind == 'item':
            parent = heading
            headings.append((heading,))
        else:
            headings.append((parent, heading))
    duplicates = [key for key, n in Counter(headings).items() if n > 1]
    assert not duplicates, duplicates

    for chapter in range(1, 9):
        stem = ROOT / f'tex/build/spanish-chapter{chapter:02d}/chapter{chapter:02d}'
        assert normalize(stem.with_suffix('.idx').read_text()) == stem.with_suffix('.sorted.idx').read_text(), stem
        issues = re.findall(r'.*(?:Warning|Overfull|Underfull|Missing character|undefined|unreferenced destination).*', stem.with_suffix('.log').read_text())
        assert not issues, (stem, issues)

    builds = {}
    for language in ('en', 'spanish'):
        stem = ROOT / f'tex/build/{language}/main'
        log = stem.with_suffix('.log').read_text()
        issues = re.findall(r'.*(?:Warning|Overfull|Underfull|Missing character|undefined|unreferenced destination).*', log)
        assert not issues, issues
        info = subprocess.check_output(['pdfinfo', str(stem.with_suffix('.pdf'))], text=True)
        builds[language] = {'pages': int(re.search(r'Pages:\s*(\d+)', info)[1]), 'log': 'clean'}
    result = {
        'protected_files_verified': len(snapshot),
        'review_edit_records': len(json.loads((ROOT / 'tex/tools/book_review_edits.json').read_text())),
        'index_entries': len(entries),
        'index_see_references_checked': len(references),
        'duplicate_index_headings': duplicates,
        'standalone_spanish_indexes_checked': 8,
        'builds': builds,
        'visual_inspection': 'Deferred to the user, as requested.',
    }
    (AUDIT / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
