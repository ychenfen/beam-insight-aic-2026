"""Build the numbered local materials ZIP; never uploads or submits."""
from pathlib import Path
import datetime, hashlib, io, json, re, shutil, subprocess, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def text_pdf(p, first=1):
    return subprocess.check_output(['pdftotext', '-f', str(first), str(p), '-'], text=True)

def main():
    entry = json.loads((ROOT / 'entry.json').read_text())
    team = entry['team_id']
    assert re.fullmatch(r'AIC-2026-\d+', team)
    assert len(entry['description']) <= 300
    prefix = team + '-开放式赛题-梁鉴'
    report = ROOT / 'output/pdf/完整技术报告.pdf'
    evidence = ROOT / 'output/pdf/研发与实验验证佐证材料.pdf'
    deck = ROOT / 'output/pptx/答辩演示_可编辑版.pptx'
    preview = deck.with_suffix('.pdf')
    video_check = json.loads((ROOT/'results/video_validation.json').read_text())
    video = ROOT/'output/video'/(prefix+'-演示视频.mp4')
    assert video_check['status'] == 'verified_locally'
    assert video_check['sha256'] == sha(video)
    assert all(video_check['checks'].values())
    assert team in text_pdf(report) and team in text_pdf(preview)
    pdfs = {}
    for p, expected in [(report,13),(evidence,6),(preview,10)]:
        meta = subprocess.check_output(['pdfinfo', str(p)], text=True)
        pages = int(re.search(r'Pages:\s+(\d+)', meta)[1])
        assert pages == expected
        assert p.stat().st_size < 10_000_000
        pdfs[str(p.relative_to(ROOT))] = dict(pages=pages,sha256=sha(p))
    ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
    with zipfile.ZipFile(deck) as z:
        assert z.testzip() is None
        slides = [n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)]
        assert len(slides) == 10
        assert team in z.read('ppt/slides/slide1.xml').decode()
        assert not any('团队编号待补' in z.read(n).decode() for n in slides)
        assert sum(len(ET.fromstring(z.read(n)).findall('.//a:tbl',ns)) for n in slides)==2
        assert len([n for n in z.namelist() if re.fullmatch(r'ppt/charts/chart\d+.xml',n)])==4
        for n in z.namelist():
            if n.endswith('.xlsx'):
                with zipfile.ZipFile(io.BytesIO(z.read(n))) as w: assert w.testzip() is None
    baseline = ROOT / 'archives/before-team-number-20261022-211601'
    if baseline.exists():
        assert text_pdf(report,2) == text_pdf(baseline/'output/pdf/完整技术报告.pdf',2)
        with zipfile.ZipFile(deck) as current, zipfile.ZipFile(baseline/'output/pptx/答辩演示_可编辑版.pptx') as previous:
            assert current.namelist() == previous.namelist()
            changed = [n for n in current.namelist() if current.read(n) != previous.read(n)]
            expected = {'ppt/slides/slide1.xml','ppt/slides/slide10.xml'} | {f'ppt/notesSlides/notesSlide{i}.xml' for i in range(1,11)}
            assert set(changed) == expected
    assert json.loads((ROOT/'results/validation.json').read_text())['all_passed']
    for run in ['run1','run2']:
        prov=json.loads((ROOT/'results'/run/'provenance.json').read_text())
        assert all(sha(ROOT/name)==value for name,value in prov['source_hashes'].items())

    files = {
        prefix+'-技术报告.pdf': report,
        prefix+'-佐证材料.pdf': evidence,
        prefix+'-作品简介.txt': ROOT/'output/evidence/参赛作品简介.txt',
        prefix+'-演示视频.mp4': video,
        '附加文件夹/'+prefix+'-演示视频.srt': video.with_suffix('.srt'),
        '附加文件夹/视频配音稿.md': ROOT/'output/video/配音稿.md',
        '附加文件夹/'+prefix+'-答辩演示.pptx': deck,
        '附加文件夹/'+prefix+'-答辩演示预览.pdf': preview,
        '附加文件夹/'+prefix+'-技术补充.pdf': ROOT/'output/pdf/技术补充.pdf',
        '附加文件夹/PPT编辑说明.md': ROOT/'output/pptx/编辑说明.md',
    }
    skipped = {'.aux','.log','.out','.nav','.snm','.toc','.vrb','.pyc'}
    for folder in ['src','tests','scripts','demo','docs','paper','video','results/run1','results/run2','output/evidence','output/pdf','output/pptx']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in skipped:
                files['工程源码与实验记录/'+p.relative_to(ROOT).as_posix()] = p
    for name in ['README.md','MANIFEST.md','HANDOFF.md','requirements.txt','entry.json','results/validation.json','results/browser_validation.json','results/video_validation.json','work/video/timeline.json','work/video/encoding.json','work/video/recording-check.json']:
        files['工程源码与实验记录/'+name] = ROOT/name
    timeline = json.loads((ROOT/'work/video/timeline.json').read_text())
    for scene in timeline['scenes']:
        for name in [scene['audio'], 'work/video/raw/'+scene['id']+'.webm']:
            files['工程源码与实验记录/'+name] = ROOT/name
    for domain in ['regular','healthy','mass']:
        name = 'work/video/cases/'+domain+'.json'
        files['工程源码与实验记录/'+name] = ROOT/name
    # Received rules/templates/chat screenshots stay out of the submission ZIP.
    # Preserve them separately in the independent recovery copy.
    originals=[p for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() in ['.pdf','.jpg']]
    print('Checking and hashing the current project files...',flush=True)
    hashes={name:sha(p) for name,p in files.items()}
    readme = f'''梁鉴参赛材料包
团队编号：{team}
赛道：AI+力学开放式赛题

根目录：技术报告（13页）、研发与实验验证佐证材料（6页）、作品简介（201字符）、演示视频MP4。
附加文件夹：可编辑PPTX（10页）、PDF预览、技术补充、编辑说明、视频字幕SRT与配音稿。PPTX放置依据为用户转述群老师的要求。
工程源码与实验记录：代码、数据、模型、LaTeX与PPTX来源、实际演示记录。收到的规则模板与群聊截图单独保存在本地备份，不包含在提交ZIP内。

本包已同步团队编号；团队名称尚未提供，报告封面该栏留空。
视频时长{video_check['duration_seconds']:.2f}秒，1920×1080、30fps、H.264/AAC，大小{video_check['bytes']/1_000_000:.2f}MB。含实际运行、中文合成旁白与烧录字幕；合成语音已在画面披露。
工程目录保留可编辑分镜和网页、8段原始录制与旁白、时间轴、三个实际响应和核验记录。旧答辩脚本为备选，成片配音稿以附加文件夹版本为准。
作品结果均为仿真；佐证材料不构成实物试验或第三方证明。
本包仅完成本地整理与核验，没有上传或提交比赛平台。
旧的20261013及单独佐证附件ZIP保留为历史版本，以当前编号材料包为准。
'''
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    archive=ROOT/'submission'/(prefix+'-材料包.zip')
    if archive.exists():
        old=ROOT/'archives/packages';old.mkdir(parents=True,exist_ok=True)
        shutil.copy2(archive,old/(stamp+'_'+archive.name))
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,p in sorted(files.items()): z.write(p,name)
        z.writestr('材料目录与当前状态.txt',readme)
        z.writestr('SHA256.json',json.dumps(hashes,ensure_ascii=False,indent=2))
    print('ZIP written; verifying CRC, file hashes and recovery copy...',flush=True)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(name)).hexdigest()==value for name,value in hashes.items())
        assert all(i.flag_bits&0x800 for i in z.infolist() if not i.filename.isascii())
        assert '附加文件夹/'+prefix+'-答辩演示.pptx' in z.namelist()
        assert prefix+'-演示视频.mp4' in z.namelist()
        backup=Path('/Users/yuchenxu/Documents/AIC_阳光力学_独立备份')/('team-package-'+stamp)
        backup.mkdir(parents=True)
        z.extractall(backup/'材料包')
    assert all(sha(backup/'材料包'/name)==value for name,value in hashes.items())
    shutil.copy2(archive,backup/archive.name)
    assert sha(archive)==sha(backup/archive.name)
    received=backup/'收到的原始材料';received.mkdir()
    for p in originals:
        shutil.copy2(p,received/p.name)
        assert sha(p)==sha(received/p.name)
    result=dict(status='verified_locally',team_id=team,zip=str(archive),zip_bytes=archive.stat().st_size,zip_sha256=sha(archive),files=len(files)+2,pptx_location='附加文件夹/'+prefix+'-答辩演示.pptx',pdfs=pdfs,report_body_unchanged=True,pptx_charts_tables_unchanged=True,visual_review=['report cover','slide 1','slide 10','video sampled frames'],zip_crc='passed',zip_utf8='passed',backup=str(backup),backup_hashes='matched',video_mp4_present=True,video_seconds=video_check['duration_seconds'],video_sha256=sha(video),submitted=False,pending=['team name','team review','external submission'],sha256=hashes)
    destination=ROOT/'results/submission_package_validation.json'
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    shutil.copy2(destination,backup/'VALIDATION.json')
    print(json.dumps({k:result[k] for k in ['status','team_id','zip','zip_bytes','files','pptx_location','backup','video_mp4_present']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
