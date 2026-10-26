"""Read-only evidence audit. Run with the bundled document Python runtime.

No inference from shipment state to operating state, no inferred signal tags.
Outputs documentation only; neither source documents nor backend are modified.
"""
from pathlib import Path
import csv
import hashlib
import json
from collections import Counter
import sys
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
OUT = ROOT / 'docs' / 'visual-audit'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(WORKSPACE / '.codex-deps'))
import pypdf


def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def audit():
    inv_path = WORKSPACE / 'turkmen-gips-digital-twin/tools/pekas-sql-live-sim/data/machine_inventory.json'
    inv = json.loads(inv_path.read_text(encoding='utf-8'))
    workbook = openpyxl.load_workbook(WORKSPACE / 'Makine liste Baumak.xlsx', read_only=True, data_only=True)
    sheet = workbook[inv['source_worksheet']]
    sheet_rows = list(sheet.values)
    mismatches, rows = [], []
    for item in inv['items']:
        original = sheet_rows[item['excel_row'] - 1]
        clean = lambda v: str(v).strip() if v is not None else ''
        for index, key in [(3, 'baumaK_code'), (4, 'equipment_name_tr'), (6, 'model_type')]:
            if clean(original[index]) != clean(item.get(key)):
                mismatches.append({'row': item['excel_row'], 'field': key, 'xlsx': clean(original[index]), 'json': clean(item.get(key))})
        rows.append({
            'assetId': item['id'], 'name': item['equipment_name_tr'], 'nameEn': item.get('equipment_name_en'),
            'model': item.get('model_type') or 'Missing Data', 'plant': item['plant'],
            'documentedUnit': item['unit'], 'building': item.get('building_no') or 'Missing Data',
            'coordinates': 'Missing Data', 'sourceRow': item['excel_row'],
            'processFunction': item.get('equipment_name_en') or 'Missing Data',
            'processFunctionStatus': 'Unverified: source equipment designation; no OEM process validation',
            'predecessor': 'Unverified: spreadsheet order is not a piping/flow connection',
            'successor': 'Unverified: spreadsheet order is not a piping/flow connection',
            'structure': ' / '.join(str(item[k]) for k in ['model_type', 'dimensions', 'capacity'] if item.get(k)) or 'Missing Data',
            'structureStatus': 'Confirmed in document only; geometry not field-measured',
            'plcScada': 'Missing Data', 'availableLiveData': 'Missing Data',
            'visualization': 'Source photo if matched by assetId; otherwise labeled document card; no speculative 3D',
            'identityStatus': 'Confirmed' if item.get('has_baumak_code') else 'Unverified',
            'installationStatus': 'Unverified', 'serviceEquipment': item['equipment_name_tr'].strip() == 'Kompresör',
            'source': f"Makine liste Baumak.xlsx / {inv['source_worksheet']} / row {item['excel_row']}",
        })
    assert len(rows) == 705
    assert len({r['assetId'] for r in rows}) == 705
    # Coarse process groups follow the documented process, never asset-to-asset routing.
    unit_order = {'Crushing and screening unit':10, 'Grinding, Classification and Storage unit':20,
                  'Calcination Unit by Rotary Kiln':30, 'Expanded Perlite Plant':40,
                  'Mixing Line 1':50, 'Mixing Line 2':60, 'Palletizing and Stretch-Hood':70,
                  'Calcite Crushing and Screening Unit':110, 'Calcite Drying, Grinding and Classifying':120,
                  'Intermediate storage unit':130}
    for row in rows:
        row['processGroupOrder'] = unit_order.get(row['documentedUnit'], 900)
        row['withinGroupOrder'] = 'Source row only; topology Unverified'
    rows.sort(key=lambda row:(row['processGroupOrder'], row['sourceRow']))
    write_csv('MACHINE-INVENTORY.csv', rows)
    (OUT / 'inventory-source-comparison.json').write_text(json.dumps(mismatches, ensure_ascii=False, indent=2), encoding='utf-8')

    # Review all rows in the derived registers; inherited guesses stay unverified.
    derived = []
    for name in ['TurkmenGips_Enriched_Asset_Register.xlsx', 'AKBULUT_MAKINE_ENTEGRASYON_ENVANTERI.xlsx', 'TurkmenGips_Sistem_Varlik_ve_Eksik_Siparis_Matrisi.xlsx']:
        path = WORKSPACE / 'turkmen-gips-digital-twin/docs' / name
        book = openpyxl.load_workbook(path, read_only=True, data_only=True)
        tabs = {}
        for tab in book:
            data = list(tab.values)
            tabs[tab.title] = {'rows': len(data), 'columns': tab.max_column, 'nonemptyCells': sum(v is not None for row in data for v in row)}
            if tab.title == 'Assets':
                # Include every enriched source record separately, rather than merging inferred connectivity into confirmed evidence.
                header = list(data[0])
                extra = []
                for values in data[1:]:
                    obj = dict(zip(header, values))
                    extra.append({str(k): v for k, v in obj.items() if k is not None})
                (OUT / 'derived-asset-register.json').write_text(json.dumps(extra, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
            if tab.title == 'Sanjin PDF Line':
                header = list(data[0]); proposal = []
                for n, values in enumerate(data[1:], 2):
                    proposal.append({'sourceRow': n, 'verification': 'Unverified: supplier proposal; installation not confirmed', **{str(k): v for k,v in zip(header,values) if k is not None}})
                (OUT / 'sanjin-proposal-register.json').write_text(json.dumps(proposal, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
        derived.append({'file': str(path), 'sheets': tabs})
    (OUT / 'workbook-coverage.json').write_text(json.dumps(derived, ensure_ascii=False, indent=2), encoding='utf-8')

    evidence = []
    files = [WORKSPACE / 'Makine liste Baumak.xlsx', inv_path]
    files += list(WORKSPACE.glob('*.PDF')) + list(WORKSPACE.glob('*.pdf'))
    files += list(WORKSPACE.glob('*.dwg')) + list((WORKSPACE / 'zawod').glob('*.dwg')) + list((WORKSPACE / 'zawod').glob('*.nwd'))
    files += list((ROOT / 'sunum/photos').glob('*'))
    files += [Path(x['file']) for x in derived]
    seen = set()
    for path in files:
        if not path.is_file() or str(path).lower() in seen:
            continue
        seen.add(str(path).lower())
        row = {'file':str(path), 'bytes':path.stat().st_size, 'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(), 'review':'Metadata/hash only'}
        if path.suffix.lower() == '.pdf':
            try:
                pdf = pypdf.PdfReader(path)
                pages = [(i+1, p.extract_text() or '') for i,p in enumerate(pdf.pages)]
                text = '\n\n'.join(f'PAGE {i}\n{t}' for i,t in pages)
                (OUT / (path.stem + '.txt')).write_text(text, encoding='utf-8')
                row.update(review='All pages text-extracted; drawings not dimensionally validated', pages=len(pages), textCharacters=len(text))
            except Exception as error:
                row['review'] = f'Extraction unavailable: {type(error).__name__}'
        elif path.suffix.lower() in ['.dwg', '.nwd']:
            row['review'] = 'Missing Data: native geometry not decoded; no coordinates, dimensions or topology claimed'
        elif path.parent.name == 'photos':
            row['review'] = 'Source photo present; asset/serial identity unverified'
        elif path.suffix.lower() == '.xlsx':
            row['review'] = 'Workbook cells inspected; installed state not established'
        evidence.append(row)
    (OUT / 'SOURCE-MANIFEST.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')

    mapping = json.loads((ROOT/'backend/config/tag_mapping.json').read_text(encoding='utf-8'))
    write_csv('PLC-SCADA-MAPPING.csv',[{'field':f['key'],'unit':f['unit'],'status':f['status'],'candidate':f['candidate'],'query':f.get('query') or 'Missing Data','verifiedLive':f['status']=='VERIFIED'} for f in mapping['fields']])
    counts = Counter(r['documentedUnit'] for r in rows)
    summary = {'physicalRecords':len(rows),'coded':sum(x['identityStatus']=='Confirmed' for x in rows),'uncoded':sum(x['identityStatus']!='Confirmed' for x in rows),'serviceCompressors':sum(x['serviceEquipment'] for x in rows),'modelMissing':sum(x['model']=='Missing Data' for x in rows),'sourceComparisonDifferences':len(mismatches),'units':dict(counts),'liveVerified':sum(f['status']=='VERIFIED' for f in mapping['fields']), 'dataFields':len(mapping['fields'])}
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    audit()
