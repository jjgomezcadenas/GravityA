#!/usr/bin/env python3
"""Give MakeIndex consistent Spanish sort keys without changing printed terms.

The generated .idx is kept intact; MakeIndex reads a normalized sibling file.
Accents do not affect ordering, while ñ sorts after n and before o.
"""
import argparse
from pathlib import Path
import re
import subprocess
import unicodedata


def normalize_entry(entry):
    term, separator, formatting = entry.partition('|')
    levels = []
    for level in term.split('!'):
        printed = level.rsplit('@', 1)[-1]
        # Preserve ñ as a distinct letter during accent removal.
        key = printed.replace('ñ', 'n~').replace('Ñ', 'N~')
        key = ''.join(c for c in unicodedata.normalize('NFD', key)
                      if not unicodedata.combining(c))
        levels.append(key + '@' + printed if key != printed else printed)
    return '!'.join(levels) + separator + formatting


def normalize(text):
    result = []
    for line in text.splitlines(keepends=True):
        match = re.match(r'\\indexentry\{', line)
        if not match:
            result.append(line)
            continue
        start = match.end()
        depth = 1
        end = start
        while depth:
            if line[end] == '{':
                depth += 1
            elif line[end] == '}':
                depth -= 1
            end += 1
        result.append(line[:start] + normalize_entry(line[start:end-1]) + line[end-1:])
    return ''.join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', required=True)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    normalized = args.source.with_suffix('.sorted.idx')
    normalized.write_text(normalize(args.source.read_text()))
    subprocess.run(['makeindex', '-t', str(args.source.with_suffix('.ilg')),
                    '-o', args.o, str(normalized)], check=True)


if __name__ == '__main__':
    main()
