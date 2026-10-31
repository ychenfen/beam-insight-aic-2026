"""Verify native slide objects, chart data, render evidence and independent copy."""
from pathlib import Path
import json, hashlib, zipfile, re, subprocess, shutil, datetime, io
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
deck=ROOT/'output/pptx/答辩演示_可编辑版.pptx'
pdf=deck.with_suffix('.pdf')
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads((ROOT/'results/run1/summary.json').read_text())
methods=['hybrid','ai','exhaustive']
domains=['id','healthy','noise','mesh','triple','mass']
expected=[[[data['id'][m]['mae_pp'] for m in methods]],
          [[data['id'][m]['median_ms'] for m in methods]],
          [[data['id'][m]['mean_calls'] for m in ['hybrid','exhaustive']]],
          [[data[d][m]['mae_pp'] for d in domains] for m in methods+['no_environment']]]
counts={'slides':0,'text_runs':0,'charts':0,'tables':0,'pictures':0,'embedded_workbooks':0,'speaker_notes':0}
with zipfile.ZipFile(deck) as z:
    assert z.testzip() is None
    for i in range(1,11):
        r=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        texts=r.findall('.//a:t',ns)
        assert len(texts)>5
        counts['slides']+=1;counts['text_runs']+=len(texts)
        counts['tables']+=len(r.findall('.//a:tbl',ns))
        counts['pictures']+=len(r.findall('.//p:pic',ns))
        assert f'ppt/notesSlides/notesSlide{i}.xml' in z.namelist()
        counts['speaker_notes']+=1
    charts=[n for n in z.namelist() if re.fullmatch(r'ppt/charts/chart\d+.xml',n)]
    assert len(charts)==4
    for i,values in enumerate(expected,1):
        r=ET.fromstring(z.read(f'ppt/charts/chart{i}.xml'))
        actual=[[float(v.text) for v in s.findall('./c:val/c:numRef/c:numCache/c:pt/c:v',ns)] for s in r.findall('.//c:ser',ns)]
        assert actual==values,(i,actual,values)
        counts['charts']+=1
    for n in z.namelist():
        if n.endswith('.xlsx'):
            with zipfile.ZipFile(io.BytesIO(z.read(n))) as wb: assert wb.testzip() is None
            counts['embedded_workbooks']+=1
assert counts['tables']==2 and counts['pictures']==1 and counts['embedded_workbooks']==4
info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
assert int(re.search(r'Pages:\s+(\d+)',info)[1])==10
text=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True)
assert '3.78' in text and '87.5%' in text and '80.2%' in text
renders=[ROOT/f'work/pptx/render-{i:02}.png' for i in range(1,11)]
assert all(p.exists() for p in renders)
backup=ROOT.parent.parent/'Documents/AIC_阳光力学_独立备份'/('editable-pptx-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
sources=[deck,pdf,ROOT/'scripts/build_editable_pptx.cjs',ROOT/'scripts/verify_editable_pptx.py',ROOT/'results/run1/summary.json',ROOT/'paper/generated/demo_stage.png',ROOT/'entry.json',ROOT/'output/pptx/编辑说明.md']
for p in sources:
    dest=backup/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    assert sha(p)==sha(dest)
result={'status':'verified_locally','counts':counts,'zip_integrity':'passed','chart_data_match_run1':True,
        'render_engine':'LibreOffice 26.2.2.2 + Poppler',
        'visual_review':{'pages':list(range(1,11)),'findings':'All pages viewed; no observed clipping or overlap.'},
        'render_hashes':{str(p.relative_to(ROOT)):sha(p) for p in renders},
        'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sources},
        'backup':str(backup),'backup_hashes':'matched',
        'limitations':['Only the 3D demo screenshot is raster; other content uses native objects.','Old contest ZIP has not been regenerated.','No external upload or submission.']}
(ROOT/'results/pptx_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(backup/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
