#!/usr/bin/env python3
"""Check the introduction, conclusion and acknowledgements against the DOCX."""
import hashlib,json,re,subprocess
from extract_pilot import ROOT,nodes
from extract_supporting import extract,GROUPS
from validate_pilot import normalize,prose
from validate_spanish import parse,paragraphs
from supporting_scope import before_supporting

def main():
    extract()
    directory=ROOT/'tex/build/supporting-audit'
    source=json.loads((directory/'source-map.json').read_text())
    counts={};texts={'en':{},'spanish':{}}
    for name in GROUPS:
        expected={pos:r['source_text'] for pos,r in source.items() if r['group']==name}
        for lang in texts:
            text=(ROOT/f'tex/{lang}/{name}.tex').read_text();texts[lang][name]=text
            actual=paragraphs(text)
            assert list(actual)==list(expected),(lang,name,'paragraph coverage')
            assert not list(nodes(parse(text),'Math')) and not list(nodes(parse(text),'Image'))
            assert r'\index{' not in text and r'\hyperlink{' not in text
            if lang=='en':
                for pos,body in actual.items():
                    assert normalize(expected[pos])==normalize(prose(parse(body)['blocks'])),('English/source',name,pos)
        en,es=paragraphs(texts['en'][name]),paragraphs(texts['spanish'][name])
        for pos in en:
            a=prose(parse(en[pos])['blocks']);b=prose(parse(es[pos])['blocks'])
            assert re.findall(r'\d+',a)==re.findall(r'\d+',b),('numbers',name,pos)
        for command in ['label','ref','eqref']:
            assert re.findall(r'\\'+command+r'\{([^}]+)\}',texts['en'][name])==re.findall(r'\\'+command+r'\{([^}]+)\}',texts['spanish'][name])
        plain=ROOT/f'tex/build/prose/spanish/{name}.txt'
        assert plain.stat().st_mtime >= (ROOT/f'tex/spanish/{name}.tex').stat().st_mtime
        assert normalize(plain.read_text())==normalize(prose(parse(texts['spanish'][name])['blocks'])),('prose',name)
        counts[name]=len(expected)
    # Preserve every named acknowledgement and the source edition attribution.
    for person in ['Luca Bonatti','Marina Forlizzi','Manuela Galbiati','Rizzoli','Donato Bini','Carlo Rovelli','Olindo Zanotti','Carolin','Anna','Emilia','Dominik','Victoria Hislop']:
        assert person in texts['spanish']['acknowledgements'],person
    assert 'edición en inglés' in texts['spanish']['acknowledgements']
    logs={}
    for build,lang,stem in [('supporting','en','supporting'),('spanish-supporting','spanish','supporting'),('en','en','main'),('spanish','spanish','main')]:
        base=ROOT/f'tex/build/{build}/{stem}'
        log=base.with_suffix('.log').read_text()
        issues=re.findall(r'.*(?:Warning|Overfull|Underfull|Missing character|undefined|duplicate destination).*',log)
        assert not issues,'\n'.join(issues)
        for name in GROUPS:
            assert (ROOT/f'tex/{lang}/{name}.tex').stat().st_mtime<=base.with_suffix('.pdf').stat().st_mtime
        info=subprocess.check_output(['pdfinfo',str(base.with_suffix('.pdf'))],text=True)
        logs[build]={'status':'clean','pages':int(re.search(r'Pages:\s*(\d+)',info)[1])}
    snapshot=json.loads((directory/'protected-before.json').read_text())
    for name,digest in snapshot.items():
        data=before_supporting(name,(ROOT/name).read_bytes())
        assert hashlib.sha256(data).hexdigest()==digest,f'Protected file changed: {name}'
    result={'english_matches_docx':True,'paragraphs':counts,'figures':0,'math_objects':0,'notes':0,'index_entries':0,'builds':logs,'protected_files_checked':len(snapshot),'scope':'Mechanical checks complement manual translation and rendered-page review.'}
    (directory/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
