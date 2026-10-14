#!/usr/bin/env python3
"""Extract chapter 8 and its notes from the pinned DOCX; existing files are protected."""
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
from extract_chapter08_table import extract_table
from extract_pilot import ROOT, SOURCE, SOURCE_SHA256, NS, W, text_of, tex_escape, run, nodes

HEADINGS = {
1125: ('chapter', 'Gravitational Waves: Curvature In Motion', 'ch:08'),
1136: ('section', 'Waves Like The Others, But Different', 'sec:08-waves'),
1159: ('section', 'Gravitational And Electromagnetic Waves', 'sec:08-comparison'),
1173: ('section', 'How Do We Detect Gravitational Waves?', 'sec:08-detectors'),
1192: ('section', 'Who Makes The Waves?', 'sec:08-sources'),
1206: ('section', 'The Zoology Of Gravitational-wave Sources', 'sec:08-zoology'),
1228: ('section', 'The Difficult Life Of A Couple', 'sec:08-couple'),
1247: ('section', '1 + 1 = 1: The Bizarre Arithmetic Of Binary Black Holes', 'sec:08-merger'),
1261: ('section', 'The Perfect Sources Of Energy', 'sec:08-energy'),
1269: ('section', 'A Formidable Theoretical Challenge', 'sec:08-numerics'),
1279: ('section', 'Closing With Pure Amazement', 'sec:08-luminosity'),
1292: ('section', 'The Complex Dynamics Of Binary Neutron Stars', 'sec:08-neutron-stars'),
1303: ('section', 'A Fatal Battle Against Gravity', 'sec:08-remnant'),
1313: ('section', 'A Mystery That Started With The Cold War', 'sec:08-gamma'),
1323: ('section', 'Much More Than Sources Of Gravitational Waves', 'sec:08-multimessenger'),
1337: ('section', 'An Explosion Worth Its Weight In Gold', 'sec:08-gold'),
}
FIGURES = {1144:(1,1146),1153:(2,1154),1180:(3,1182),1221:(4,1223),1237:(5,1239),1255:(6,1257),1330:(7,1331)}
CALLOUTS = {1130:[1],1150:[2],1155:[3],1216:[4],1258:[5],1296:[6],1297:[7],1310:[8],1319:[9],1320:[10],1325:[11,12],1328:[13],1340:[14,15],1345:[16]}
GROUPS = {'ch08':list(range(1125,1352)), 'notes/ch08':list(range(2086,2102))}


def extract():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    tokens, records, indices = {}, {}, []
    table_tex, table_audit = extract_table()
    def token(s):
        key = f'CHEGHTTOKEN{len(tokens):05d}END'
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
                if not s.strip() and not maths and i not in FIGURES and i != 1168: continue
                records[i]={'group':group,'source_text':s,'math_objects':maths}
                # Keep paragraph boundaries as distinct Pandoc blocks.
                marker=ET.Element(W+'p');marker.append(run(f'CHEGHTPARA{i}END'));blocks.append(marker)
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
                    p.insert(pos,run(token(r'\textsuperscript{\hyperlink{note:08-'+f'{n:02d}'+'}{'+str(n)+'}}')))
                # Images are mapped explicitly below, including image+caption paragraphs.
                for parent in p.iter():
                    for child in list(parent):
                        if child.tag==W+'drawing':parent.remove(child)
                props=p.find('w:pPr',NS)
                if props is not None:p.remove(props)
                blocks.append(p)
        for child in list(body):body.remove(child)
        body.extend(blocks)
        with tempfile.TemporaryDirectory(prefix='gravity-ch08-') as tmp:
            path=Path(tmp)/'chapter.docx'
            with ZipFile(path,'w',ZIP_DEFLATED) as out:
                for name in archive.namelist():
                    out.writestr(name,ET.tostring(document) if name=='word/document.xml' else archive.read(name))
            ast=json.loads(subprocess.check_output(['pandoc',str(path),'-t','json'],text=True))
    assert not list(nodes(ast,'Image'))
    groups={}; current=None
    for b in ast['blocks']:
        strings=list(nodes(b,'Str'))
        if len(strings)==1 and re.fullmatch(r'CHEGHTPARA\d+END',strings[0]['c']):
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
            if i == 1168: t = r'\input{en/tables/ch08-waves}'
            # Restore the explicitly named box glyph from a damaged Word character.
            if i == 1130: t = t.replace('\x7f', r'\(\square\)')
            if i in (1197, 1283, 1287):
                expression = re.search(r'\\\((.*?)\\\)', t, re.S)[1]
                if i == 1197:
                    expression = expression.replace('Gc', r'\textcolor{gray}{Gc}').replace(r'\frac{c^{5}}{G}', r'\textcolor{gray}{\frac{c^{5}}{G}}')
                if i == 1283:
                    at = expression.index(r'\left')
                    expression = expression[:at] + r'\textcolor{gray}{' + expression[at:] + '}'
                number = {1197:'01',1283:'01-repeat',1287:'02'}[i]
                tag = r'\tag{8.1}' if i == 1283 else ''
                t = r'\begin{equation}' + tag + r'\label{eq:08-' + number + '}\n' + expression + '\n' + r'\end{equation}'
            if i == 1283: t = r'\begingroup\renewcommand{\theHequation}{8.repeat}' + t + r'\endgroup'
            if i in FIGURES:
                n,cap=FIGURES[i]
                lines.append('\\begin{figure}[htbp]\n\\centering\n'+f'\\includegraphics[width=0.88\\linewidth,height=0.48\\textheight,keepaspectratio]{{../figs/pdf/en/fig-08-{n:02d}.pdf}}')
                if i!=cap:t=''
            if i in captions:
                t=re.sub(r'^Fig\.\s*8\.\d+\s+','',t)
                # Italic captions may place the prefix inside \emph{}.
                t=re.sub(r'(\\emph\{)Fig\.\s*8\.\d+\s+',r'\1',t)
                t=r'\caption{'+t+'}'+r'\label{fig:08-'+f'{captions[i]:02d}'+'}\n'+r'\end{figure}'
            if i>=2086:
                t=re.sub(r'^\d+\.?\s*','',t)
                t=f'\\item[{i-2085}.]\\hypertarget{{note:08-{i-2085:02d}}}{{}}'+t
            if t:lines.append(t)
        outputs[rec['group']].append('\n'.join(lines))
    result={}
    for group,parts in outputs.items():
        text='\n\n'.join(parts)+'\n'
        text=re.sub(r'(Figure\s+|Fig\.\s+)8\.(\d+)\b',lambda m:m[1]+r'\ref{fig:08-'+f'{int(m[2]):02d}'+'}',text)
        text=text.replace('\\emph{\\hfill\\break\n}','')
        text=text.replace(r'\st{.}', '.')
        text = text.replace('(8.1)', r'\eqref{eq:08-01}').replace('(8.2)', r'\eqref{eq:08-02}')
        text = text.replace('../figs/pdf/en/fig-08-03.pdf', '../figs/source/en/fig-08-03.jpeg').replace('../figs/pdf/en/fig-08-04.pdf', '../figs/source/en/fig-08-04.jpeg')
        if group.startswith('notes/'):
            text='\\section*{Chapter 8: Gravitational Waves: Curvature In Motion}\n\\begin{description}[style=multiline,leftmargin=2em,labelwidth=1.5em]\n\n'+text+'\n\\end{description}\n'
        result[group]=text
    result['tables/ch08-waves'] = table_tex
    audit=ROOT/'tex/build/ch08-audit';audit.mkdir(parents=True,exist_ok=True)
    (audit/'source-map.json').write_text(json.dumps({'paragraphs':records,'index_entries':indices,'math':[m['c'][1] for m in nodes(ast,'Math')], 'table':table_audit},ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--audit-only',action='store_true');args=ap.parse_args()
    if not args.audit_only:
        assert all(not (ROOT/'tex/en'/f'{g}.tex').exists() for g in [*GROUPS, 'tables/ch08-waves']),'Refusing to overwrite existing chapter files'
    outputs=extract()
    if not args.audit_only:
        for group,text in outputs.items():
            path=ROOT/'tex/en'/f'{group}.tex';path.parent.mkdir(exist_ok=True);path.write_text(text)
    print('Chapter 8 extraction/audit complete.')
