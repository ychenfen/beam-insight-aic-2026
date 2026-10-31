"""Verify and package a LOCAL REVIEW CANDIDATE; never uploads. AI-assisted 2026-10-13."""
from pathlib import Path
import json,hashlib,subprocess,re,zipfile,shutil,datetime
import numpy as np
import joblib
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
entry=json.loads((ROOT/'entry.json').read_text())
assert len(entry['title'])<=20 and len(entry['description'])<=300
assert json.loads((ROOT/'results/validation.json').read_text())['all_passed']
assert json.loads((ROOT/'results/browser_validation.json').read_text())['passed']
for run in ['run1','run2']:
    provenance=json.loads((ROOT/'results'/run/'provenance.json').read_text())
    assert all(sha(ROOT/f)==h for f,h in provenance['source_hashes'].items())
pdfs={}
for name,pages in [('技术报告',2),('技术补充',6),('答辩演示',10),('完整技术报告',13)]:
    path=ROOT/'output/pdf'/f'{name}.pdf'
    meta=subprocess.check_output(['pdfinfo',str(path)],text=True)
    text=subprocess.check_output(['pdftotext',str(path),'-'],text=True)
    assert int(re.search(r'Pages:\s+(\d+)',meta)[1])==pages
    assert path.stat().st_size<10_000_000
    assert '/Users/' not in text and 'yuchenxu' not in text
    assert '[?]' not in text and '\ufffd' not in text
    fonts=subprocess.check_output(['pdffonts',str(path)],text=True).splitlines()[2:]
    assert fonts and all(line.split()[-5]=='yes' for line in fonts)
    pdfs[name]=dict(pages=pages,bytes=path.stat().st_size,sha256=sha(path),chinese_characters=len(re.findall(r'[\u4e00-\u9fff]',text)),non_whitespace_characters=len(re.sub(r'\s','',text)))
for src in ['report','appendix','defense','full_report']:
    log=(ROOT/'work'/f'{src}-build.log').read_text()
    assert 'Overfull' not in log and 'undefined' not in log and '\n!' not in log
inputs=[]
for p in sorted(ROOT.iterdir()):
    if p.suffix.lower() in ['.pdf','.jpg']:
        inputs.append(dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)))
(ROOT/'docs/INPUT_MANIFEST.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2))
files=[]
for d in ['src','tests','scripts','demo','docs','paper','results/run1','results/run2']:
    files.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.aux','.log','.out','.nav','.snm','.toc','.vrb'])
files.extend((ROOT/'output/pdf').glob('*.pdf'))
files.extend(ROOT/n for n in ['README.md','MANIFEST.md','HANDOFF.md','requirements.txt','entry.json','results/validation.json','results/browser_validation.json'])
files=sorted(set(files))
manifest={str(p.relative_to(ROOT)):sha(p) for p in files}
(ROOT/'results/ARTIFACT_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
files.append(ROOT/'results/ARTIFACT_SHA256.json')
package_dir=ROOT/'submission';package_dir.mkdir(exist_ok=True)
zip_path=package_dir/'梁鉴_完整稿审阅包_待补团队编号_20261013.zip'
if zip_path.exists():
    old=ROOT/'archives/packages';old.mkdir(parents=True,exist_ok=True)
    shutil.copy2(zip_path,old/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'_'+zip_path.name))
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={p.relative_to(ROOT).as_posix() for p in files}
    for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    assert all(i.flag_bits&0x800 for i in z.infolist() if any(ord(c)>127 for c in i.filename))
backup=ROOT.parent.parent/'Documents/AIC_阳光力学_独立备份'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True)
with zipfile.ZipFile(zip_path) as z:z.extractall(backup/'editable_project')
shutil.copy2(zip_path,backup/zip_path.name)
originals=backup/'official_inputs';originals.mkdir()
for r in inputs:shutil.copy2(ROOT/r['name'],originals/r['name'])
assert sha(zip_path)==sha(backup/zip_path.name)
assert all(sha(backup/'editable_project'/n)==h for n,h in manifest.items())
assert all(sha(originals/r['name'])==r['sha256'] for r in inputs)
restored={'npz':0,'models':0,'pdf':0}
for p in (backup/'editable_project/results').rglob('*.npz'):
    with np.load(p,allow_pickle=False) as arrays:
        assert arrays.files and all(np.isfinite(arrays[k]).all() for k in arrays.files)
    restored['npz']+=1
for p in (backup/'editable_project/results').rglob('*.joblib'):
    assert joblib.load(p) is not None
    restored['models']+=1
for p in (backup/'editable_project/output/pdf').glob('*.pdf'):
    assert 'Pages:' in subprocess.check_output(['pdfinfo',str(p)],text=True)
    restored['pdf']+=1
result=dict(status='verified_locally_pending_team_review',pdfs=pdfs,zip=dict(path=str(zip_path.relative_to(ROOT)),files=len(files),bytes=zip_path.stat().st_size,sha256=sha(zip_path),integrity='passed',utf8='passed'),independent_backup=str(backup),backup_hashes='all matched',pending=['team identifier and name','human review','physical experiment evidence','optional demo video','external upload and submission'])
result['restored_files_opened']=restored
(ROOT/'results/package_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(backup/'BACKUP_VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
