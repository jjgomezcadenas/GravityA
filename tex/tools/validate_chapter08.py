#!/usr/bin/env python3
"""Audit chapter 8 against the DOCX, including its comparison table."""
from supporting_scope import before_supporting
import hashlib,json,re
from pathlib import Path
from extract_pilot import ROOT,nodes
from extract_chapter08 import extract
from validate_pilot import prose,normalize
from validate_spanish import paragraphs,parse
from validate_chapter07 import prose_numbers,INDEX,GRAPHIC

def math_content(s):
    s=s.replace(r'\textcolor{gray}', '').replace(r'\mathrm{vatios}','Watt').replace('{,}', '.')
    s=re.sub(r'\\label\{[^}]+\}|\\tag\{[^}]+\}|\\(?:begin|end)\{equation\}', '',s)
    return re.sub(r'[\s{}]', '',s.replace(r'\ ',''))

def table_cells(s):
    parts=re.split(r'% DOCX table after paragraph 1168, row (\d), column (\d)\n',s)
    result={}
    for i in range(1,len(parts),3):
        row,col,body=parts[i:i+3]
        body=re.split(r'\n&|\n\\\\\[6pt\]',body)[0]
        result[row,col]=body
    return result

def main():
    extract()
    audit=ROOT/'tex/build/ch08-audit';source=json.loads((audit/'source-map.json').read_text())
    en='\n'.join((ROOT/f'tex/en/{f}.tex').read_text() for f in ['ch08','notes/ch08'])
    es='\n'.join((ROOT/f'tex/spanish/{f}.tex').read_text() for f in ['ch08','notes/ch08'])
    tables={lang:(ROOT/f'tex/{lang}/tables/ch08-waves.tex').read_text() for lang in ['en','spanish']}
    expected=[]
    for pos,r in source['paragraphs'].items():
        s=r['source_text']
        if pos=='1125':s=s.removeprefix('8 ')
        if int(pos)>=2086:s=re.sub(r'^\d+\.?\s*','',s)
        if pos in ['1197','1283','1287']:s=''
        s=re.sub(r'^Fig\.\s*8\.\d+\s+','',s)
        s=s.replace('\x7f','')
        expected.append(s)
    t=en.replace(r'\input{en/tables/ch08-waves}','')
    t=re.sub(r'\\ref\{fig:08-(\d+)\}',lambda m:f'8.{int(m[1])}',t)
    t=re.sub(r'\\eqref\{eq:08-(\d+)\}',lambda m:f'(8.{int(m[1])})',t)
    t=re.sub(r'\\section\*\{Chapter 8:[^}]+\}', '',t)
    a,b=normalize(''.join(expected)),normalize(prose(parse(t)['blocks']))
    if a!=b:
        i=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
        raise AssertionError(f'English differs at {i}:\n{a[max(0,i-60):i+150]}\n{b[max(0,i-60):i+150]}')
    ec,sc=table_cells(tables['en']),table_cells(tables['spanish'])
    assert list(ec)==list(sc) and len(ec)==18
    for cell in source['table']['cells']:
        key=str(cell['row']),str(cell['column'])
        assert normalize(cell['source_text'])==normalize(prose(parse(ec[key])['blocks'])),key
        assert len(re.findall(INDEX,ec[key]))==len(re.findall(INDEX,sc[key])),key
    enp,esp=paragraphs(en),paragraphs(es)
    assert list(enp)==list(esp)==list(source['paragraphs']) and len(enp)==171
    for cmd in ['label','ref','eqref','hyperlink','hypertarget']:
        assert re.findall(r'\\'+cmd+r'\{([^}]+)\}',en)==re.findall(r'\\'+cmd+r'\{([^}]+)\}',es),cmd
    assert en.count(r'\index{')==es.count(r'\index{')==len(source['index_entries'])==272
    assert tables['en'].count(r'\index{')==tables['spanish'].count(r'\index{')==8
    for token,count in [(r'\caption{',7),(r'\begin{equation}',3),(r'\hyperlink{note:',16),(r'\hypertarget{note:',16)]:
        assert en.count(token)==es.count(token)==count,token
    assert re.findall(GRAPHIC.replace('([^}]+)','[^}]+'),en)==re.findall(GRAPHIC.replace('([^}]+)','[^}]+'),es)
    for path in re.findall(GRAPHIC,en):assert (ROOT/'tex'/path).is_file(),path
    em=[m['c'][1] for m in nodes(parse(en.replace(r'\input{en/tables/ch08-waves}','')),'Math')]
    sm=[m['c'][1] for m in nodes(parse(es.replace(r'\input{spanish/tables/ch08-waves}','')),'Math')]
    original=[r'\square']+source['math']
    assert len(em)==len(sm)==len(original)==10,(em,sm)
    for i,(a,b,c) in enumerate(zip(original,em,sm)):
        assert math_content(a)==math_content(b)==math_content(c),('math',i,math_content(a),math_content(b),math_content(c))
    errors=[]
    for pos in enp:
        a,b=enp[pos],esp[pos]
        a=re.sub(r'\\input\{[^}]+\}', '',a);b=re.sub(r'\\input\{[^}]+\}', '',b)
        assert len(re.findall(INDEX,a))==len(re.findall(INDEX,b)),('index',pos)
        power=r'\\textsuperscript\{(-?\d+)\}'
        assert re.findall(power,a)==re.findall(power,b),('powers',pos)
        an,bn=prose_numbers(a,'en'),prose_numbers(b,'es')
        if pos=='1325':an=['170817' if n=='17817' else n for n in an]
        # Decade names are naturally spelled out in Spanish.
        if pos in ['1232','1315','1316','1320','1343','1345']:
            an=[n for n in an if n not in {'1960','1970','1980','1990'}]
        if pos=='1271':an.remove('1990')
        if an!=bn:errors.append((pos,an,bn))
        if '©' in a:
            ac=prose(parse(r'\begin{figure}'+a)['blocks']).split('©')[1]
            bc=prose(parse(r'\begin{figure}'+b)['blocks']).split('©')[1].replace('datos de','data by').replace(' y ',' and ')
            assert normalize(ac)==normalize(bc),('credit',pos,ac,bc)
    assert not errors,errors
    logs={}
    for build,lang in [('chapter08','en'),('spanish-chapter08','spanish')]:
        base=ROOT/f'tex/build/{build}/chapter08';log=base.with_suffix('.log').read_text()
        issues=re.findall(r'.*(?:Warning|warning  \(pdf backend\)|Overfull|Underfull|Missing character|undefined|unreferenced destination).*',log)
        assert not issues,'\n'.join(issues)
        idx=base.with_suffix('.ilg').read_text();assert '280 entries accepted, 0 rejected' in idx and '0 warnings' in idx
        inputs=[ROOT/f'tex/{lang}/{f}.tex' for f in ['ch08','notes/ch08','tables/ch08-waves','chapter08']]+[ROOT/'tex/common/preamble.tex']+[ROOT/'tex'/p for p in re.findall(GRAPHIC,en)]
        assert all(p.stat().st_mtime<=base.with_suffix('.pdf').stat().st_mtime for p in inputs),'Stale PDF'
        logs[build]='clean'
    snapshot=json.loads((audit/'protected-before.json').read_text())
    for name,digest in snapshot.items():
        data=(ROOT/name).read_bytes()
        data = before_supporting(name, data)
        if name in ['tex/en/main.tex','tex/spanish/main.tex']:
            lang=name.split('/')[1]
            data=data.replace(f'\\include{{{lang}/ch08}}\n'.encode(),b'').replace(f'\\input{{{lang}/notes/ch08}}\n'.encode(),b'')
        if name=='figs/manifest.tsv':data=b'\n'.join(l for l in data.split(b'\n') if not l.startswith(b'08-'))
        assert hashlib.sha256(data).hexdigest()==digest,f'Protected file changed: {name}'
    result={'english_matches_docx':True,'paragraphs':171,'table_cells':18,'figures':7,'numbered_equations':2,'repeated_equations':1,'notes':16,'source_math_objects':9,'restored_box_glyph':1,'index_entries':280,'builds':logs,'protected_files_checked':len(snapshot),'exceptions':['Preserved source v/v factors, repeated (8.1) and source reference (8.2)','Restored damaged box glyph; translated decimal typography and decade names','Spanish repairs obvious identifier typo GW17817 to GW170817; English unchanged'],'scope':'Mechanical checks complement manual translation and visual review.'}
    (audit/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
