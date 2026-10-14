#!/usr/bin/env python3
"""Extract chapter 7 and its notes from the pinned DOCX; existing files are protected."""
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

HEADINGS = {828: ('chapter', 'The First Image Of A Black Hole', 'ch:07'),
 847: ('section', 'Doing What Was Thought To Be Impossible', 'sec:07-impossible'),
 859: ('section', 'A Telescope As Big As The Earth', 'sec:07-telescope'),
 878: ('section', 'A Most Amazing Technique', 'sec:07-vlbi'),
 899: ('section', 'All A Matter Of Trajectories', 'sec:07-trajectories'),
 916: ('section', 'The Vortical Motion Near A Rotating Black Hole', 'sec:07-rotation'),
 953: ('section', 'A Game Of Lights And Shadows', 'sec:07-shadow'),
 973: ('section', 'Shadows And Discs', 'sec:07-discs'),
 999: ('section', 'The Predictions Of The Theory', 'sec:07-theory'),
 1024: ('section', 'From A Turbulent Plasma To A Map Of Light', 'sec:07-map'),
 1053: ('section', 'The Images Of M87*', 'sec:07-images'),
 1075: ('section', 'Like A Needle In A Haystack', 'sec:07-needle'),
 1104: ('section', 'Are We Really Sure?', 'sec:07-sure')}
FIGURES = {833:(1,835),890:(2,892),906:(3,908),925:(4,927),938:(5,940),946:(6,948),
           959:(7,961),981:(8,983),990:(9,992),1012:(10,1014),1033:(11,1035),
           1068:(12,1070),1082:(13,1084),1090:(14,1092),1114:(15,1116)}
CALLOUTS = {849:[1],895:[2],911:[3],912:[4],930:[5],996:[6],1005:[7],1016:[8,9],1080:[10],1112:[11]}
GROUPS = {'ch07':list(range(828,1125)), 'notes/ch07':list(range(2071,2082))}


def extract():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    tokens, records, indices = {}, {}, []
    def token(s):
        key = f'CHSEVNTOKEN{len(tokens):05d}END'
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
                marker=ET.Element(W+'p');marker.append(run(f'CHSEVNPARA{i}END'));blocks.append(marker)
                # Preserve XE fields at their source positions.
                children=list(p); start=None; instruction=''; ranges=[]
                for j,c in enumerate(children):
                    for e in c.iter():
                        if e.tag==W+'fldChar':
                            if e.get(W+'fldCharType')=='begin': start=j;instruction=''
                            elif e.get(W+'fldCharType')=='end': ranges.append((start,j,instruction));start=None
                        elif e.tag==W+'instrText':instruction+=e.text or ''
                for a,b,instruction in reversed(ranges):
                    bold = bool(re.search(r'\\b\s*$', instruction))
                    instruction = re.sub(r'\\b\s*$', '', instruction)
                    match=re.fullmatch(r'\s*XE\s+"((?:\\.|[^"\\])*)"\s*(?:\\t\s+"([^"]*)"\s*)?',instruction)
                    assert match,(i,instruction)
                    entry=match[1].replace(r'\"','"')
                    latex='!'.join(re.sub(r'(["!@|])',r'"\1',tex_escape(part)) for part in entry.split(':'))
                    if match[2]:
                        assert match[2].startswith('See ')
                        latex+='|see{'+tex_escape(match[2][4:])+'}'
                    if bold: latex += '|textbf'
                    indices.append({'paragraph':i,'entry':entry})
                    for c in children[a:b+1]:p.remove(c)
                    p.insert(a,run(token(r'\index{'+latex+'}')))
                for n in CALLOUTS.get(i, []):
                    candidates=[r for r in p.findall('w:r',NS) if text_of(r)==str(n)
                                and r.find('w:rPr/w:vertAlign',NS) is not None]
                    assert len(candidates)==1,(i,candidates)
                    r=candidates[-1];pos=list(p).index(r);p.remove(r)
                    p.insert(pos,run(token(r'\textsuperscript{\hyperlink{note:07-'+f'{n:02d}'+'}{'+str(n)+'}}')))
                # Images are mapped explicitly below, including image+caption paragraphs.
                for parent in p.iter():
                    for child in list(parent):
                        if child.tag==W+'drawing':parent.remove(child)
                props=p.find('w:pPr',NS)
                if props is not None:p.remove(props)
                blocks.append(p)
        for child in list(body):body.remove(child)
        body.extend(blocks)
        with tempfile.TemporaryDirectory(prefix='gravity-ch07-') as tmp:
            path=Path(tmp)/'chapter.docx'
            with ZipFile(path,'w',ZIP_DEFLATED) as out:
                for name in archive.namelist():
                    out.writestr(name,ET.tostring(document) if name=='word/document.xml' else archive.read(name))
            ast=json.loads(subprocess.check_output(['pandoc',str(path),'-t','json'],text=True))
    assert not list(nodes(ast,'Image'))
    groups={}; current=None
    for b in ast['blocks']:
        strings=list(nodes(b,'Str'))
        if len(strings)==1 and re.fullmatch(r'CHSEVNPARA\d+END',strings[0]['c']):
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
        if i in HEADINGS:
            cmd,title,label=HEADINGS[i];lines.append(f'\\{cmd}{{{title}}}\\label{{{label}}}')
            lines.extend(re.findall(r'\\index\{[^}]+\}', convert(i)))
        else:
            t=convert(i)
            if i in (829, 864): t = ''  # Title continuation / separate equation number.
            if i == 863:
                t = r'''\begin{equation}\label{eq:07-01}
\begin{pmatrix}\text{angular resolution of} \\ \text{astronomical image}\end{pmatrix}
=\left(\frac{\text{wavelength of observations}}{\text{telescope size}}\right)
\end{equation}'''
            if i == 905:
                t = '\\begin{figure}[htbp]\n\\centering\nnon-rotating\\par\\medskip'
            if i == 1059: t = '\\begin{itemize}\n\\item '+t
            if i == 1060: t = '\\item '+t
            if i == 1061: t = '\\item '+t+'\n\\end{itemize}'
            # Pandoc reads the literal Word math string √27 as an empty root plus 27.
            t = t.replace(r'\sqrt{}27', r'\sqrt{27}')
            if i in FIGURES:
                n,cap=FIGURES[i]
                lines.append('\\begin{figure}[htbp]\n\\centering\n'+f'\\includegraphics[width=0.88\\linewidth,height=0.48\\textheight,keepaspectratio]{{../figs/pdf/en/fig-07-{n:02d}.pdf}}')
                if n == 2: lines[-1] = lines[-1].replace('width=0.88', 'width=0.96').replace('height=0.48', 'height=0.74')
                if i == 906: lines[-1] = lines[-1].replace('\\begin{figure}[htbp]\n\\centering\n', '')
                if i!=cap:t=''
            if i in captions:
                t=re.sub(r'^Fig\.\s*7\.\d+\s+','',t)
                # Italic captions may place the prefix inside \emph{}.
                t=re.sub(r'(\\emph\{)Fig\.\s*7\.\d+\s+',r'\1',t)
                t=r'\caption{'+t+'}'+r'\label{fig:07-'+f'{captions[i]:02d}'+'}\n'+r'\end{figure}'
            if i>=2071:
                t=re.sub(r'^\d+\.?\s*','',t)
                t=f'\\item[{i-2070}.]\\hypertarget{{note:07-{i-2070:02d}}}{{}}'+t
            if t:lines.append(t)
        outputs[rec['group']].append('\n'.join(lines))
    result={}
    for group,parts in outputs.items():
        text='\n\n'.join(parts)+'\n'
        text=re.sub(r'(Figure\s+|Fig\.\s+)7\.(\d+)\b',lambda m:m[1]+r'\ref{fig:07-'+f'{int(m[2]):02d}'+'}',text)
        text=text.replace('\\emph{\\hfill\\break\n}','')
        text=text.replace(r'\st{.}', '.')
        text = text.replace('(7.1)', r'\eqref{eq:07-01}')
        for n, ext in [(4, 'png'), (5, 'jpeg'), (11, 'png'), (13, 'jpg')]:
            text=text.replace(f'../figs/pdf/en/fig-07-{n:02d}.pdf', f'../figs/source/en/fig-07-{n:02d}.{ext}')
        if group.startswith('notes/'):
            text='\\section*{Chapter 7: The First Image Of A Black Hole}\n\\begin{description}[style=multiline,leftmargin=2em,labelwidth=1.5em]\n\n'+text+'\n\\end{description}\n'
        result[group]=text
    audit=ROOT/'tex/build/ch07-audit';audit.mkdir(parents=True,exist_ok=True)
    (audit/'source-map.json').write_text(json.dumps({'paragraphs':records,'index_entries':indices,'math':[m['c'][1] for m in nodes(ast,'Math')]},ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--audit-only',action='store_true');args=ap.parse_args()
    if not args.audit_only:
        assert all(not (ROOT/'tex/en'/f'{g}.tex').exists() for g in GROUPS),'Refusing to overwrite existing chapter files'
    outputs=extract()
    if not args.audit_only:
        for group,text in outputs.items():(ROOT/'tex/en'/f'{group}.tex').write_text(text)
    print('Chapter 7 extraction/audit complete.')
