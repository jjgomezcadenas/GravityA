#!/usr/bin/env python3
"""Extract conclusion and acknowledgements without overwriting edited files."""
import argparse,copy,hashlib,io,json,re,subprocess,tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile,ZIP_DEFLATED
from extract_pilot import ROOT,SOURCE,SOURCE_SHA256,NS,W,text_of,paragraph,nodes
GROUPS={'introduction':range(40,55),'conclusion':range(1352,1369),'acknowledgements':range(1369,1382)}
HEADINGS={40:('introduction','The Beginning of the Journey'),1352:('conclusion','The End Of The Journey'),1369:('acknowledgements','Acknowledgements')}

def extract():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA256
    records={};blocks=[]
    with ZipFile(SOURCE) as archive:
        xml=archive.read('word/document.xml')
        for _,(prefix,uri) in ET.iterparse(io.BytesIO(xml),events=['start-ns']):
            if not re.fullmatch(r'ns\d+',prefix):ET.register_namespace(prefix,uri)
        doc=ET.fromstring(xml);body=doc.find('w:body',NS);ps=body.findall('w:p',NS)
        for group,positions in GROUPS.items():
            for i in positions:
                p=copy.deepcopy(ps[i]);s=text_of(p)
                assert not p.findall('.//w:instrText',NS) and not p.findall('.//m:oMath',NS) and not p.findall('.//w:drawing',NS)
                if not s.strip():continue
                records[i]={'group':group,'source_text':s}
                props=p.find('w:pPr',NS)
                if props is not None:p.remove(props)
                blocks.extend([paragraph(f'SUPPORTPARA{i}END'),p])
        for child in list(body):body.remove(child)
        body.extend(blocks)
        with tempfile.TemporaryDirectory(prefix='gravity-support-') as tmp:
            path=Path(tmp)/'source.docx'
            with ZipFile(path,'w',ZIP_DEFLATED) as out:
                for name in archive.namelist():out.writestr(name,ET.tostring(doc) if name=='word/document.xml' else archive.read(name))
            ast=json.loads(subprocess.check_output(['pandoc',str(path),'-t','json'],text=True))
    groups={};current=None
    for b in ast['blocks']:
        strings=list(nodes(b,'Str'))
        if len(strings)==1 and re.fullmatch(r'SUPPORTPARA\d+END',strings[0]['c']):
            current=int(strings[0]['c'][11:-3]);groups[current]=[]
        else:groups[current].append(b)
    outputs={name:[] for name in GROUPS}
    for i,r in records.items():
        if i in HEADINGS:
            label,title=HEADINGS[i]
            text=f'\\chapter*{{{title}}}\\label{{{label}}}\n\\addcontentsline{{toc}}{{chapter}}{{{title}}}\n\\markboth{{{title}}}{{{title}}}'
        else:
            text=subprocess.check_output(['pandoc','-f','json','-t','latex','--columns=88'],input=json.dumps({**ast,'blocks':groups[i]}),text=True).strip()
        outputs[r['group']].append(f'% DOCX paragraph {i}\n{text}\n')
    audit=ROOT/'tex/build/supporting-audit';audit.mkdir(exist_ok=True,parents=True)
    (audit/'source-map.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    return {name:'\n'.join(parts) for name,parts in outputs.items()}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--audit-only',action='store_true');args=ap.parse_args()
    if not args.audit_only:
        assert all(not (ROOT/f'tex/en/{n}.tex').exists() for n in ['conclusion','acknowledgements']),'Refusing to overwrite existing files'
    result=extract()
    if not args.audit_only:
        for name in ['conclusion','acknowledgements']:(ROOT/f'tex/en/{name}.tex').write_text(result[name])
    print('Supporting material source audit refreshed; existing introduction unchanged.')
