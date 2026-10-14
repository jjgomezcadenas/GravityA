"""Preserve the chapter 8 comparison table, including all source index fields."""
import io, copy, json, re, subprocess, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from extract_pilot import SOURCE, NS, W, text_of, tex_escape, run, nodes


def extract_table():
    with ZipFile(SOURCE) as z:
        xml = z.read('word/document.xml')
        for _, (prefix, uri) in ET.iterparse(io.BytesIO(xml), events=['start-ns']):
            if not re.fullmatch(r'ns\d+', prefix): ET.register_namespace(prefix, uri)
        document = ET.fromstring(xml)
        body = document.find('w:body', NS)
        table = body.find('w:tbl', NS)
        cells, tokens, entries, blocks = [], {}, [], []
        for r, row in enumerate(table.findall('w:tr', NS)):
            for c, cell in enumerate(row.findall('w:tc', NS)):
                record = {'row': r, 'column': c, 'source_text': text_of(cell)}
                cells.append(record)
                marker = ET.Element(W+'p');marker.append(run(f'TABLECELL{r}C{c}END'));blocks.append(marker)
                for original in cell.findall('w:p', NS):
                    p = copy.deepcopy(original)
                    children=list(p);start=None;instruction='';ranges=[]
                    for j, child in enumerate(children):
                        for e in child.iter():
                            if e.tag == W+'fldChar':
                                if e.get(W+'fldCharType') == 'begin':start=j;instruction=''
                                elif e.get(W+'fldCharType') == 'end':ranges.append((start,j,instruction))
                            elif e.tag == W+'instrText':instruction += e.text or ''
                    for a,b,ins in reversed(ranges):
                        m=re.fullmatch(r'\s*XE\s+"([^"]+)"\s*',ins)
                        assert m,ins
                        entry='!'.join(re.sub(r'(["!@|])',r'"\1',tex_escape(part)) for part in m[1].split(':'))
                        key=f'TABLEINDEX{len(tokens):04d}END';tokens[key]=r'\index{'+entry+'}'
                        entries.append({'row':r,'column':c,'entry':m[1]})
                        for child in children[a:b+1]:p.remove(child)
                        p.insert(a,run(key))
                    props=p.find('w:pPr',NS)
                    if props is not None:p.remove(props)
                    blocks.append(p)
        for child in list(body):body.remove(child)
        body.extend(blocks)
        with tempfile.TemporaryDirectory(prefix='gravity-ch08-table-') as tmp:
            path=Path(tmp)/'table.docx'
            with ZipFile(path,'w',ZIP_DEFLATED) as out:
                for name in z.namelist():out.writestr(name,ET.tostring(document) if name=='word/document.xml' else z.read(name))
            ast=json.loads(subprocess.check_output(['pandoc',str(path),'-t','json'],text=True))
    groups={};current=None
    for b in ast['blocks']:
        ss=list(nodes(b,'Str'))
        m=re.fullmatch(r'TABLECELL(\d+)C(\d+)END',ss[0]['c']) if len(ss)==1 else None
        if m:current=(int(m[1]),int(m[2]));groups[current]=[]
        else:groups[current].append(b)
    lines=[r'{\small',r'\setlength{\tabcolsep}{5pt}',r'\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.48\linewidth}>{\raggedright\arraybackslash}p{0.48\linewidth}@{}}',r'\toprule']
    for row in range(9):
        for col in range(2):
            doc={**ast,'blocks':groups[row,col]}
            t=subprocess.check_output(['pandoc','-f','json','-t','latex','--wrap=none'],input=json.dumps(doc),text=True).strip()
            for token,value in tokens.items():t=t.replace(token,value)
            lines.extend([f'% DOCX table after paragraph 1168, row {row}, column {col}',t])
            lines.append('&' if col==0 else r'\\[6pt]')
        if row==0:lines.append(r'\midrule')
    lines.extend([r'\bottomrule',r'\end{longtable}','}'])
    return '\n'.join(lines)+'\n', {'cells':cells,'index_entries':entries}
