#!/usr/bin/env python3
"""Extract chapter 6 and its notes from the pinned DOCX; existing files are protected."""
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

HEADINGS = {626: ('chapter', 'Black Holes: Champions Of Curvature', 'ch:06'),
 638: ('section', 'An Utterly Bizarre Solution', 'sec:06-solution'),
 664: ('section', 'Escape Velocity, Event Horizon And Singularities', 'sec:06-escape'),
 678: ('section', 'When The Escape Velocity Is As Large As Possible', 'sec:06-light'),
 700: ('section', 'When Time Makes Fun Of Us', 'sec:06-time'),
 715: ('section', 'How Do You Produce A Black Hole?', 'sec:06-formation'),
 747: ('section', 'Black Holes Have No Hair', 'sec:06-hair'),
 759: ('section', 'Cosmic Engines And Hawking Radiation', 'sec:06-hawking'),
 773: ('section', 'A Difficult-To-Digest Idea', 'sec:06-idea'),
 782: ('section', 'Giving Up A Cherished Method', 'sec:06-method'),
 793: ('section', 'Observations vs Experiments', 'sec:06-observations'),
 804: ('section', 'Black-Hole Mimickers', 'sec:06-mimickers')}
FIGURES = {731:(1,735),764:(2,765),813:(3,815)}
CALLOUTS = {642:1,681:2,685:2,696:3,755:4,756:5,767:6,785:7,806:8,807:9,810:10}
EQUATIONS = {
 652: (1, r'r_{S}=2M\textcolor{gray}{\frac{G}{c^{2}}}'),
 670: (2, r'v_{f}=\sqrt{2\frac{M}{R}\textcolor{gray}{G}}'),
 721: (3, r'\textcolor{gray}{\frac{G}{c^{2}}}\frac{M_{\star}}{R_{\star}}\leq\frac{4}{9}')}
FIGURE_ROWS = {
 729: r'\text{Sun} & \text{ultra-compact star} & \text{black hole}',
 733: r'M/R\cong0.000002 & M/R\cong0.444 & M/R=0.5'}
ROW_FORMAT = r'\begin{array}{@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}}'

GROUPS = {'ch06':list(range(626,827)), 'notes/ch06':list(range(2057,2067))}


def extract():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    tokens, records, indices = {}, {}, []
    def token(s):
        key = f'CHSIXTOKEN{len(tokens):05d}END'
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
                marker=ET.Element(W+'p');marker.append(run(f'CHSIXPARA{i}END'));blocks.append(marker)
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
                    p.insert(pos,run(token(r'\textsuperscript{\hyperlink{note:06-'+f'{n:02d}'+'}{'+str(n)+'}}')))
                # Images are mapped explicitly below, including image+caption paragraphs.
                for parent in p.iter():
                    for child in list(parent):
                        if child.tag==W+'drawing':parent.remove(child)
                props=p.find('w:pPr',NS)
                if props is not None:p.remove(props)
                blocks.append(p)
        for child in list(body):body.remove(child)
        body.extend(blocks)
        with tempfile.TemporaryDirectory(prefix='gravity-ch06-') as tmp:
            path=Path(tmp)/'chapter.docx'
            with ZipFile(path,'w',ZIP_DEFLATED) as out:
                for name in archive.namelist():
                    out.writestr(name,ET.tostring(document) if name=='word/document.xml' else archive.read(name))
            ast=json.loads(subprocess.check_output(['pandoc',str(path),'-t','json'],text=True))
    assert not list(nodes(ast,'Image'))
    groups={}; current=None
    for b in ast['blocks']:
        strings=list(nodes(b,'Str'))
        if len(strings)==1 and re.fullmatch(r'CHSIXPARA\d+END',strings[0]['c']):
            current=int(strings[0]['c'][9:-3]);groups[current]=[]
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
        if i in HEADINGS:
            cmd,title,label=HEADINGS[i];lines.append(f'\\{cmd}{{{title}}}\\label{{{label}}}')
        else:
            t=convert(i)
            if i == 627: t=''  # Continuation of the chapter title above.
            if i in EQUATIONS:
                n,expression=EQUATIONS[i]
                t=r'\begin{equation}\label{eq:06-'+f'{n:02d}'+'}\n'+expression+'\n'+r'\end{equation}'
            if i in FIGURE_ROWS:
                t=r'\['+ROW_FORMAT+FIGURE_ROWS[i]+r'\end{array}\]'
                if i==729:t='\\begin{figure}[htbp]\n\\centering\n'+t
            if i in range(644,647):
                t=r'\item '+t
                if i==644:t='\\begin{enumerate}\n'+t
                if i==646:t+='\n\\end{enumerate}'
            if i in range(690,696):
                t=r'\item '+t
                if i==690:t='\\begin{itemize}\n'+t
                if i==695:t+='\n\\end{itemize}'
            if i in FIGURES:
                n,cap=FIGURES[i]
                lines.append(('' if i==731 else '\\begin{figure}[htbp]\n\\centering\n')+f'\\includegraphics[width=0.88\\linewidth,height=0.48\\textheight,keepaspectratio]{{../figs/pdf/en/fig-06-{n:02d}.pdf}}')
                if i!=cap:t=''
            if i in captions:
                t=re.sub(r'^Fig\.\s*6\.\d+\s+','',t)
                # Italic captions may place the prefix inside \emph{}.
                t=re.sub(r'(\\emph\{)Fig\.\s*6\.\d+\s+',r'\1',t)
                t=r'\caption{'+t+'}'+r'\label{fig:06-'+f'{captions[i]:02d}'+'}\n'+r'\end{figure}'
            if i>=2057:
                t=re.sub(r'^\d+\.?\s*','',t)
                t=f'\\item[{i-2056}.]\\hypertarget{{note:06-{i-2056:02d}}}{{}}'+t
            if t:lines.append(t)
        outputs[rec['group']].append('\n'.join(lines))
    result={}
    for group,parts in outputs.items():
        text='\n\n'.join(parts)+'\n'
        text=re.sub(r'(Figure\s+|Fig\.\s+)6\.(\d+)\b',lambda m:m[1]+r'\ref{fig:06-'+f'{int(m[2]):02d}'+'}',text)
        text=text.replace('\\emph{\\hfill\\break\n}','')
        text=text.replace(r'\st{.}', '.')
        text=text.replace(r'\textsubscript{★}', r'\textsubscript{\(\star\)}')
        text=re.sub(r'\(6\.(\d+)\)',lambda m:r'\eqref{eq:06-'+f'{int(m[1]):02d}'+'}',text)
        
        
        if group.startswith('notes/'):
            text='\\section*{Chapter 6: Black Holes: Champions Of Curvature}\n\\begin{description}[style=multiline,leftmargin=2em,labelwidth=1.5em]\n\n'+text+'\n\\end{description}\n'
        result[group]=text
    audit=ROOT/'tex/build/ch06-audit';audit.mkdir(parents=True,exist_ok=True)
    (audit/'source-map.json').write_text(json.dumps({'paragraphs':records,'index_entries':indices,'math':[m['c'][1] for m in nodes(ast,'Math')]},ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--audit-only',action='store_true');args=ap.parse_args()
    if not args.audit_only:
        assert all(not (ROOT/'tex/en'/f'{g}.tex').exists() for g in GROUPS),'Refusing to overwrite existing chapter files'
    outputs=extract()
    if not args.audit_only:
        for group,text in outputs.items():(ROOT/'tex/en'/f'{group}.tex').write_text(text)
    print('Chapter 6 extraction/audit complete.')
