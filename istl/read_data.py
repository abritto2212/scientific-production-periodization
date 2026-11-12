"""Read this project's two-column XLSX without modifying original bytes.

Deliberately narrow standard-library reader: rejects formulas/extra columns.
Trailing blank formatted rows are ignored; interior or partial blanks fail.
"""
import posixpath
import zipfile
import xml.etree.ElementTree as ET
from periodization import validate_series

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'


def load_cases(path):
    with zipfile.ZipFile(path) as z:
        strings = [''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rels = {e.attrib['Id']: e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        cases = []
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS):
            target = rels[sheet.attrib[RID]]
            target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            rows = []
            for row in ET.fromstring(z.read(target)).findall('s:sheetData/s:row', NS):
                cells = {}
                for c in row.findall('s:c', NS):
                    if c.find('s:f', NS) is not None:
                        raise ValueError('Formula in input: '+c.attrib['r'])
                    v = c.find('s:v', NS)
                    val = None if v is None else v.text
                    if val is not None and c.attrib.get('t') == 's':
                        val = strings[int(val)]
                    col = ''.join(a for a in c.attrib['r'] if a.isalpha())
                    if col not in ('A','B') and val is not None:
                        raise ValueError('Unexpected populated column: '+col)
                    cells[col] = val
                rows.append((int(row.attrib['r']), cells.get('A'), cells.get('B')))
            if rows[0][1:] != ('Year', 'Total_Publications'):
                raise ValueError('Unexpected headers')
            blank_rows = []
            while len(rows) > 1 and rows[-1][1:] == (None, None):
                blank_rows.append(rows.pop()[0])
            data = rows[1:]
            if [r[0] for r in data] != list(range(2, len(data)+2)) or any(a is None or b is None for _,a,b in data):
                raise ValueError('Missing input row/cell in '+sheet.attrib['name'])
            x, y = validate_series([a for _,a,b in data], [b for _,a,b in data])
            cases.append((sheet.attrib['name'], x, y, sorted(blank_rows)))
        if len(cases) != 10:
            raise ValueError('Expected ten cases')
        return cases
