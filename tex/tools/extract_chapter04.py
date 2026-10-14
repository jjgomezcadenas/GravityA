#!/usr/bin/env python3
"""Extract chapter 4 and its notes from the pinned DOCX; existing files are protected."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from extract_pilot import ROOT, SOURCE, SOURCE_SHA256, NS, W, text_of, tex_escape, run, nodes

HEADINGS = {364: ('chapter', 'Curving Spacetime', 'ch:04'),
 389: ('section', 'Curving Time?', 'sec:04-time'),
 406: ('section', 'In Search Of Strong Curvature', 'sec:04-search'),
 421: ('section', 'A Theory Nobody Liked ...', 'sec:04-history'),
 435: ('section', 'A Gedanken Experiment', 'sec:04-experiment')}
FIGURES = {398:(1,400),444:(2,447)}
CALLOUTS = {376:1,382:2,415:3}
EQUATIONS = {373:1,380:2,411:3}
GROUPS = {'ch04':list(range(364,455)), 'notes/ch04':list(range(2032,2035))}


def extract():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    tokens, records, indices = {}, {}, []
    def token(s):
        key = f'CHFOURTOKEN{len(tokens):05d}END'
        tokens[key] = s
        return key
    with ZipFile(SOURCE) as archive:
        xml=archive.read('word/document.xml')
        for _,(prefix,uri) in ET.iterparse(io.BytesIO(xml),events=['start-ns']):
            if not re.fullmatch(r'ns\d+',prefix):ET.register_namespace(prefix,uri)
        document = ET.fromstring(xml)
        body = document.find('w:body',NS)
        ps = body.findall('w:p',NS)
        blocks=[]
        for group,positions in GROUPS.items():
            for i in positions:
                p=copy.deepcopy(ps[i]); s=text_of(p)
                maths=len(p.findall('.//m:oMath',NS))
                if not s.strip() and not maths and i not in FIGURES: continue
                records[i]={'group':group,'source_text':s,'math_objects':maths}
                # Keep paragraph boundaries as distinct Pandoc blocks.
                marker=ET.Element(W+'p');marker.append(run(f'CHFOURPARA{i}END'));blocks.append(marker)
                # Preserve XE fields at their source positions.
                children=list(p); start=None; instruction=''; ranges=[]
                for j,c in enumerate(children):
                    for e in c.iter():
                        if e.tag==W+'fldChar':
                            if e.get(W+'fldCharType')=='begin': start=j;instruction=''
                            elif e.get(W+'fldCharType')=='end': ranges.append((start,j,instruction));start=None
                        elif e.tag==W+'instrText':instruction+=e.text or ''
                for a,b,instruction in reversed(ranges):
                    match=re.fullmatch(r'\s*XE\s+"((?:\\.|[^"\\])*)"\s*(?:\\t\s+"([^"]*)"\s*)?',instruction)
                    assert match,(i,instruction)
                    entry=match[1].replace(r'\"','"')
                    latex='!'.join(re.sub(r'(["!@|])',r'"\1',tex_escape(part)) for part in entry.split(':'))
                    if match[2]:
                        assert match[2].startswith('See ')
                        latex+='|see{'+tex_escape(match[2][4:])+'}'
                    indices.append({'paragraph':i,'entry':entry})
                    for c in children[a:b+1]:p.remove(c)
                    p.insert(a,run(token(r'\index{'+latex+'}')))
                if i in CALLOUTS:
                    n=CALLOUTS[i]
                    candidates=[r for r in p.findall('w:r',NS) if text_of(r)==str(n)
                                and r.find('w:rPr/w:vertAlign',NS) is not None]
                    assert len(candidates)==1,(i,candidates)
                    r=candidates[-1];pos=list(p).index(r);p.remove(r)
                    p.insert(pos,run(token(r'\textsuperscript{\hyperlink{note:04-'+f'{n:02d}'+'}{'+str(n)+'}}')))
                # Images are mapped explicitly below, including image+caption paragraphs.
                for parent in p.iter():
                    for child in list(parent):
                        if child.tag==W+'drawing':parent.remove(child)
                props=p.find('w:pPr',NS)
                if props is not None:p.remove(props)
                blocks.append(p)
        for child in list(body):body.remove(child)
        body.extend(blocks)
        with tempfile.TemporaryDirectory(prefix='gravity-ch04-') as tmp:
            path=Path(tmp)/'chapter.docx'
            with ZipFile(path,'w',ZIP_DEFLATED) as out:
                for name in archive.namelist():
                    out.writestr(name,ET.tostring(document) if name=='word/document.xml' else archive.read(name))
            ast=json.loads(subprocess.check_output(['pandoc',str(path),'-t','json'],text=True))
    assert not list(nodes(ast,'Image'))
    groups={}; current=None
    for b in ast['blocks']:
        strings=list(nodes(b,'Str'))
        if len(strings)==1 and re.fullmatch(r'CHFOURPARA\d+END',strings[0]['c']):
            current=int(strings[0]['c'][10:-3]);groups[current]=[]
        else: groups[current].append(b)
    def convert(p):
        doc={**ast,'blocks':groups[p]}
        t=subprocess.check_output(['pandoc','-f','json','-t','latex','--columns=88'],input=json.dumps(doc),text=True)
        for key,value in tokens.items():t=t.replace(key,value)
        return t.strip()
    outputs={k:[] for k in GROUPS}
    captions={cap:n for n,cap in FIGURES.values()}
    for i,rec in records.items():
        lines=[f'% DOCX paragraph {i}']
        if i in (374,381,412):lines.append('% Equation number is generated with the preceding equation.')
        elif i in HEADINGS:
            cmd,title,label=HEADINGS[i];lines.append(f'\\{cmd}{{{title}}}\\label{{{label}}}')
        elif i in EQUATIONS:
            math=list(nodes(groups[i],'Math'));assert len(math)==1
            lines.append(r'\begin{equation}\label{eq:04-'+f'{EQUATIONS[i]:02d}'+'}\n'+math[0]['c'][1]+'\n'+r'\end{equation}')
        else:
            t=convert(i)
            if i==442:
                lines.append('\\begin{figure}[htbp]\n\\centering')
            if i in FIGURES:
                n,cap=FIGURES[i]
                lines.append(('\\begin{figure}[htbp]\n\\centering\n' if i==398 else '')+f'\\includegraphics[width=0.88\\linewidth,height=0.48\\textheight,keepaspectratio]{{../figs/pdf/en/fig-04-{n:02d}.pdf}}')
                if i!=cap:t=''
            if i in captions:
                t=re.sub(r'^Fig\.\s*4\.\d+\s+','',t)
                # Italic captions may place the prefix inside \emph{}.
                t=re.sub(r'(\\emph\{)Fig\.\s*4\.\d+\s+',r'\1',t)
                t=r'\caption{'+t+'}'+r'\label{fig:04-'+f'{captions[i]:02d}'+'}\n'+r'\end{figure}'
            if i>=2032:
                t=re.sub(r'^\d+\s*','',t)
                t=f'\\item[{i-2031}.]\\hypertarget{{note:04-{i-2031:02d}}}{{}}'+t
            if t:lines.append(t)
        outputs[rec['group']].append('\n'.join(lines))
    result={}
    for group,parts in outputs.items():
        text='\n\n'.join(parts)+'\n'
        text=re.sub(r'(Figure\s+|Fig\.\s+)4\.(\d+)\b',lambda m:m[1]+r'\ref{fig:04-'+f'{int(m[2]):02d}'+'}',text)
        text=re.sub(r'\(4\.([1-3])\)',lambda m:r'\eqref{eq:04-0'+m[1]+'}',text)
        text=text.replace(r'\frac{G}{c^{2}}',r'\textcolor{gray}{\frac{G}{c^{2}}}')
        text=text.replace(r'\bigodot',r'\odot')
        text=text.replace('\\emph{\\hfill\\break\n}','')
        if group.startswith('notes/'):
            text='\\section*{Chapter 4: Curving Spacetime}\n\\begin{description}[style=multiline,leftmargin=2em,labelwidth=1.5em]\n\n'+text+'\n\\end{description}\n'
        result[group]=text
    audit=ROOT/'tex/build/ch04-audit';audit.mkdir(parents=True,exist_ok=True)
    (audit/'source-map.json').write_text(json.dumps({'paragraphs':records,'index_entries':indices,'math':[m['c'][1] for m in nodes(ast,'Math')]},ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--audit-only',action='store_true');args=ap.parse_args()
    if not args.audit_only:
        assert all(not (ROOT/'tex/en'/f'{g}.tex').exists() for g in GROUPS),'Refusing to overwrite existing chapter files'
    outputs=extract()
    if not args.audit_only:
        for group,text in outputs.items():(ROOT/'tex/en'/f'{group}.tex').write_text(text)
    print('Chapter 4 extraction/audit complete.')
