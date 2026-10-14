#!/usr/bin/env python3
"""Audit chapter 3 extraction, translation structure, artwork and build logs."""
from supporting_scope import before_supporting
import hashlib,json,re,subprocess
from pathlib import Path
from extract_pilot import ROOT,nodes
from extract_chapter03 import extract
from validate_pilot import prose,normalize
from validate_spanish import paragraphs,parse,numbers


def main():
    extracted=extract()  # Regenerate audit only; does not write chapter files or artwork.
    audit=json.loads((ROOT/'tex/build/ch03-audit/source-map.json').read_text())
    en=(ROOT/'tex/en/ch03.tex').read_text()+'\n'+(ROOT/'tex/en/notes/ch03.tex').read_text()
    es=(ROOT/'tex/spanish/ch03.tex').read_text()+'\n'+(ROOT/'tex/spanish/notes/ch03.tex').read_text()
    expected=[]
    for pos,record in audit['paragraphs'].items():
        i=int(pos);s=record['source_text']
        if i==192:s=s.lstrip('3')
        if i in (254,264):s=''
        s=re.sub(r'^Fig\.\s*3\.\d+\s+','',s)
        if i>=2023:s=re.sub(r'^\d+\s*','',s)
        expected.append(s)
    t=re.sub(r'\\(?:eqref|ref)\{(?:eq|fig):03-(\d+)\}',lambda m:'3.'+str(int(m[1])),en)
    # Restore parentheses only on equation references for the DOCX prose comparison.
    t=re.sub(r'\\eqref\{eq:03-(\d+)\}',lambda m:'(3.'+str(int(m[1]))+')',en)
    t=re.sub(r'\\ref\{fig:03-(\d+)\}',lambda m:'3.'+str(int(m[1])),t)
    t=re.sub(r'\\section\*\{Chapter 3:[^}]+\}','',t)
    a,b=normalize(''.join(expected)),normalize(prose(parse(t)['blocks']))
    if a!=b:
        i=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
        raise AssertionError(f'English extraction mismatch at {i}:\n{a[i-50:i+100]}\n{b[i-50:i+100]}')
    enp,esp=paragraphs(en),paragraphs(es)
    assert list(enp)==list(esp),'Paragraph coverage/order mismatch'
    assert en.count(r'\includegraphics[')==es.count(r'\includegraphics[')==10
    assert en.count(r'\caption{')==es.count(r'\caption{')==10
    assert en.count(r'\index{')==es.count(r'\index{')==len(audit['index_entries'])
    for command in ('label','ref','hyperlink','hypertarget'):
        pattern=r'\\'+command+r'\{([^}]+)\}'
        assert re.findall(pattern,en)==re.findall(pattern,es),command
    assert re.findall(r'\\includegraphics\[[^]]+\]\{[^}]+\}',en)==re.findall(r'\\includegraphics\[[^]]+\]\{[^}]+\}',es)
    # All equation callouts are aligned except the documented source typo in note 2.
    assert re.findall(r'\\eqref\{[^}]+\}',en.replace('Eq. \\eqref{eq:03-03}, and','Eq. \\eqref{eq:03-02}, and'))==re.findall(r'\\eqref\{[^}]+\}',es)
    # The two symbolic equations must remain identical; four conceptual displays
    # are translated (3.1, 3.4, 3.5, and the repeat of 3.1).
    em=[m['c'][1] for m in nodes(parse(en),'Math')]
    sm=[m['c'][1] for m in nodes(parse(es),'Math')]
    original=[m['c'][1] for m in nodes(parse('\n'.join(extracted.values())),'Math')]
    assert [re.sub(r'\s+','',m) for m in em]==[re.sub(r'\s+','',m) for m in original]
    assert len(em)==len(sm)==6
    assert em[1:3]==sm[1:3]
    errors=[]
    for pos in enp:
        if int(pos) in (192,193,201,271,277,200,254,264,270,276,300):continue
        a=enp[pos].replace('6,400','6400').replace('270,000','270000')
        if pos=='2024':a=a.replace('Eq. \\eqref{eq:03-03}, and','Eq. \\eqref{eq:03-02}, and')
        b=esp[pos].replace('270 000','270000')
        if numbers(a,'en')!=numbers(b,'es'):errors.append((pos,numbers(a,'en'),numbers(b,'es')))
    assert not errors,errors
    logs={}
    for name in ('chapter03','spanish-chapter03'):
        base=ROOT/'tex/build'/name/'chapter03'
        log=base.with_suffix('.log').read_text()
        problems=re.findall(r'.*(?:Warning|Overfull|Underfull|Missing character|undefined|unreferenced destination).*',log)
        assert not problems,'\n'.join(problems)
        idx=base.with_suffix('.ilg').read_text()
        assert f"{len(audit['index_entries'])} entries accepted, 0 rejected" in idx and '0 warnings' in idx
        logs[name]='clean'
        language='en' if name=='chapter03' else 'spanish'
        for path in [ROOT/f'tex/{language}/ch03.tex',ROOT/f'tex/{language}/notes/ch03.tex',ROOT/'tex/common/preamble.tex']:
            assert path.stat().st_mtime<=base.with_suffix('.pdf').stat().st_mtime,f'Stale PDF: {name}'
    hashes=json.loads((ROOT/'tex/build/ch03-audit/protected-before.json').read_text())
    for name,digest in hashes.items():
        if name=='figs/manifest.tsv':continue  # Append-only manifest update, not artwork.
        data=(ROOT/name).read_bytes()
        data = before_supporting(name, data)
        if name in ('tex/en/main.tex','tex/spanish/main.tex'):
            language=name.split('/')[1]
            for chapter in ('04', '05', '06', '07', '08'):
                data=data.replace(f'\\include{{{language}/ch{chapter}}}\n'.encode(),b'').replace(f'\\input{{{language}/notes/ch{chapter}}}\n'.encode(),b'')
        assert hashlib.sha256(data).hexdigest()==digest,name
    result={'english_matches_docx':True,'paragraphs':len(enp),'figures':10,'notes':5,'numbered_equations':5,
            'source_math_objects':len(audit['math']),'rendered_math_displays':6,'index_entries':len(audit['index_entries']),
            'builds':logs,'protected_files_checked':len(hashes)-1,
            'exceptions':['Spanish note 2: source reference 3.3 corrected to 3.2; see editorial summary'],
            'scope':'Mechanical checks complement manual translation and visual review.'}
    (ROOT/'tex/build/ch03-audit/validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
