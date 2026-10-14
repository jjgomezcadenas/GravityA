#!/usr/bin/env python3
"""Extract chapter 3 and its notes from the pinned DOCX; existing files are protected."""
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

HEADINGS = {192: ('chapter', 'Spacetime, Curvature and Gravity', 'ch:03'),
 206: ('section', 'Spacetime: Everything That Has Happened and Will Happen', 'sec:03-spacetime'),
 214: ('section', 'Curvature', 'sec:03-curvature'),
 250: ('section', 'Curvature and The Einstein Equations', 'sec:03-equations'),
 282: ('section', 'Spacetime is an Elastic Fabric', 'sec:03-fabric'),
 297: ('section', 'Curvature and Gravity', 'sec:03-gravity'),
 311: ('section', 'Nothing Moves on a Straight Line', 'sec:03-geodesics')}
FIGURES = {221:(1,222),228:(2,229),235:(3,237),243:(4,244),286:(5,287),
           291:(6,291),306:(7,306),318:(8,320),334:(9,335),358:(10,358)}
CALLOUTS = {211:1,256:2,266:3,289:4,322:5}
EQUATIONS = {200:1,254:2,264:3,270:4,276:5}
GROUPS = {'ch03':list(range(192,364)), 'notes/ch03':list(range(2023,2028))}


def extract():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    tokens, records, indices = {}, {}, []
    def token(s):
        key = f'CHTHREETOKEN{len(tokens):05d}END'
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
                marker=ET.Element(W+'p');marker.append(run(f'CHTHREEPARA{i}END'));blocks.append(marker)
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
                    assert len(candidates)==(2 if i==256 else 1),(i,candidates)
                    # Paragraph 256 has c-squared first, then note 2.
                    r=candidates[-1];pos=list(p).index(r);p.remove(r)
                    p.insert(pos,run(token(r'\textsuperscript{\hyperlink{note:03-'+f'{n:02d}'+'}{'+str(n)+'}}')))
                # Images are mapped explicitly below, including image+caption paragraphs.
                for parent in p.iter():
                    for child in list(parent):
                        if child.tag==W+'drawing':parent.remove(child)
                props=p.find('w:pPr',NS)
                if props is not None:p.remove(props)
                blocks.append(p)
        for child in list(body):body.remove(child)
        body.extend(blocks)
        with tempfile.TemporaryDirectory(prefix='gravity-ch03-') as tmp:
            path=Path(tmp)/'chapter.docx'
            with ZipFile(path,'w',ZIP_DEFLATED) as out:
                for name in archive.namelist():
                    out.writestr(name,ET.tostring(document) if name=='word/document.xml' else archive.read(name))
            ast=json.loads(subprocess.check_output(['pandoc',str(path),'-t','json'],text=True))
    assert not list(nodes(ast,'Image'))
    groups={}; current=None
    for b in ast['blocks']:
        strings=list(nodes(b,'Str'))
        if len(strings)==1 and re.fullmatch(r'CHTHREEPARA\d+END',strings[0]['c']):
            current=int(strings[0]['c'][11:-3]);groups[current]=[]
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
        if i==193: lines.append('% Title continued in paragraph 192.')
        elif i in (201,271,277):lines.append('% Equation number is generated with the preceding equation.')
        elif i in HEADINGS:
            cmd,title,label=HEADINGS[i];lines.append(f'\\{cmd}{{{title}}}\\label{{{label}}}')
        elif i in EQUATIONS:
            math=list(nodes(groups[i],'Math'));assert len(math)==1
            lines.append(r'\begin{equation}\label{eq:03-'+f'{EQUATIONS[i]:02d}'+'}\n'+math[0]['c'][1]+'\n'+r'\end{equation}')
        else:
            t=convert(i)
            if i in FIGURES:
                n,cap=FIGURES[i]
                lines.append('\\begin{figure}[htbp]\n\\centering\n'+f'\\includegraphics[width=0.88\\linewidth,height=0.48\\textheight,keepaspectratio]{{../figs/pdf/en/fig-03-{n:02d}.pdf}}')
                if i!=cap:t=''
            if i in captions:
                t=re.sub(r'^Fig\.\s*3\.\d+\s+','',t)
                # Italic captions may place the prefix inside \emph{}.
                t=re.sub(r'(\\emph\{)Fig\.\s*3\.\d+\s+',r'\1',t)
                t=r'\caption{'+t+'}'+r'\label{fig:03-'+f'{captions[i]:02d}'+'}\n'+r'\end{figure}'
            if i>=2023:
                t=re.sub(r'^\d+\s*','',t)
                t=f'\\item[{i-2022}.]\\hypertarget{{note:03-{i-2022:02d}}}{{}}'+t
            if t:lines.append(t)
        outputs[rec['group']].append('\n'.join(lines))
    result={}
    for group,parts in outputs.items():
        text='\n\n'.join(parts)+'\n'
        text=re.sub(r'(Figure\s+|Fig\.\s+)3\.(\d+)\b',lambda m:m[1]+r'\ref{fig:03-'+f'{int(m[2]):02d}'+'}',text)
        text=re.sub(r'\(3\.([1-5])\)',lambda m:r'\eqref{eq:03-0'+m[1]+'}',text)
        text=text.replace('E = mc^{2}',r'E = m\textcolor{gray}{c^{2}}')
        text=text.replace(r'\left( \frac{8\pi G}{c^{4}} \right)',r'\textcolor{gray}{\left( \frac{8\pi G}{c^{4}} \right)}')
        text=text.replace('\\emph{\\hfill\\break\n}','')
        text=text.replace(r'\section{Spacetime:',r'\section[Spacetime]{Spacetime:')
        text=text.replace('../figs/pdf/en/fig-03-08.pdf','../figs/source/en/fig-03-08.png')
        if group.startswith('notes/'):
            text='\\section*{Chapter 3: Spacetime, Curvature and Gravity}\n\\begin{description}[style=multiline,leftmargin=2em,labelwidth=1.5em]\n\n'+text+'\n\\end{description}\n'
        result[group]=text
    audit=ROOT/'tex/build/ch03-audit';audit.mkdir(parents=True,exist_ok=True)
    (audit/'source-map.json').write_text(json.dumps({'paragraphs':records,'index_entries':indices,'math':[m['c'][1] for m in nodes(ast,'Math')]},ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--audit-only',action='store_true');args=ap.parse_args()
    if not args.audit_only:
        assert all(not (ROOT/'tex/en'/f'{g}.tex').exists() for g in GROUPS),'Refusing to overwrite existing chapter files'
    outputs=extract()
    if not args.audit_only:
        for group,text in outputs.items():(ROOT/'tex/en'/f'{group}.tex').write_text(text)
    print('Chapter 3 extraction/audit complete.')
