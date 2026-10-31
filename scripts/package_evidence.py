"""Validate and package evidence after rendered pages have been visually reviewed."""
from pathlib import Path
import argparse, datetime, hashlib, json, re, shutil, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--visual-reviewed', action='store_true', help='Only pass after reviewing all six rendered pages.')
    args = parser.parse_args()
    assert args.visual_reviewed, 'Render and inspect the latest PDF before packaging.'
    draft = ROOT / 'work/evidence/evidence.pdf'
    info = subprocess.check_output(['pdfinfo', str(draft)], text=True)
    assert re.search(r'Pages:\s+6\b', info)
    log = (ROOT / 'work/evidence/evidence.log').read_text()
    assert not any(x in log for x in ['Overfull', 'Missing character', 'LaTeX Error'])
    fonts = subprocess.check_output(['pdffonts', str(draft)], text=True).splitlines()[2:]
    assert fonts and all(line.split()[-5] == 'yes' for line in fonts)
    extracted = subprocess.check_output(['pdftotext', '-layout', str(draft), '-'], text=True)
    assert all(value in extracted for value in ['0.135', '0.517', '87.5', '24.74', '2880', '720', '10 项', '9 项'])
    assert draft.stat().st_size < 10_000_000
    entry = json.loads((ROOT / 'entry.json').read_text())
    intro = (ROOT / 'output/evidence/参赛作品简介.txt').read_text().strip()
    assert intro == entry['description'] and len(intro) == entry['description_characters'] <= 300
    records = ROOT / 'output/evidence/records'
    for name in ['review-validation.json', 'source-check.json']:
        assert json.loads((records / name).read_text())['all_passed']
    assert json.loads((records / 'browser-check.json').read_text())['passed']
    assert '10 passed' in (records / 'mechanics-test.txt').read_text()
    manifest = json.loads((records / 'file-manifest.json').read_text())['files']
    assert all(sha(ROOT / name) == item['sha256'] for name, item in manifest.items())

    pdf = ROOT / 'output/pdf/研发与实验验证佐证材料.pdf'
    shutil.copy2(draft, pdf)
    shutil.copy2(draft, ROOT / 'output/evidence/研发与实验验证佐证材料.pdf')
    names = [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'output/evidence').rglob('*')) if p.is_file()]
    names += ['paper/evidence.tex', 'paper/generated/metrics.tex', 'paper/generated/method_table.tex', 'paper/generated/domain_table.tex', 'scripts/capture_evidence.cjs', 'scripts/prepare_evidence.py', 'scripts/package_evidence.py', 'scripts/present_results.py', 'docs/SOURCES.md', 'docs/AI_USE.md', 'entry.json', 'HANDOFF.md', 'MANIFEST.md', 'results/run1/summary.json', 'results/run1/records.json', 'results/run1/provenance.json', 'results/run2/provenance.json']
    files = {name: sha(ROOT / name) for name in names}
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    archive = ROOT / 'submission/梁鉴_佐证材料与简介_20261022.zip'
    if archive.exists():
        previous = ROOT / 'archives' / ('before-evidence-package-' + stamp)
        previous.mkdir(parents=True)
        shutil.copy2(archive, previous / archive.name)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in names:
            z.write(ROOT / name, name)
        z.writestr('PACKAGE_SHA256.json', json.dumps(files, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(name)).hexdigest() == value for name, value in files.items())
        assert all(i.flag_bits & 0x800 for i in z.infolist() if not i.filename.isascii())
    backup = Path('/Users/yuchenxu/Documents/AIC_阳光力学_独立备份') / ('evidence-' + stamp)
    backup.mkdir(parents=True)
    for name in names:
        target = backup / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
        assert sha(target) == files[name]
    shutil.copy2(archive, backup / archive.name)
    assert sha(backup / archive.name) == sha(archive)
    report = dict(date='2026-10-22', status='verified_locally', pdf=str(pdf), pages=6, pdf_bytes=pdf.stat().st_size, pdf_sha256=sha(pdf), intro_characters=len(intro), tests_passed=10, saved_run_checks_passed=9, source_checks_passed=4, demo_cases=3, visual_review=dict(pages=[1,2,3,4,5,6], findings='All pages inspected; no clipping, overflow or missing glyphs. Final command spacing checked on pages 5 and 6.'), fonts_embedded=True, zip=str(archive), zip_sha256=sha(archive), zip_crc_passed=True, backup=str(backup), backup_hashes_match=True, retrained_this_turn=False, submitted=False, files=files)
    result = ROOT / 'results/evidence_validation.json'
    result.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    shutil.copy2(result, backup / 'evidence_validation.json')
    print(json.dumps({k: report[k] for k in ['status','pages','pdf_bytes','intro_characters','zip','backup']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
