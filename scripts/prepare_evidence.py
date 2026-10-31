"""Prepare traceable evidence tables from actual saved records (no retraining)."""
from pathlib import Path
import json, hashlib, datetime, shutil, ast

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/evidence'
REC = OUT / 'records'

def read(path):
    return json.loads(path.read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    checks = {}
    for run in ['run1', 'run2']:
        provenance = read(ROOT / 'results' / run / 'provenance.json')
        for name, expected in provenance['source_hashes'].items():
            checks[run + ':' + name] = digest(ROOT / name) == expected
    assert all(checks.values())
    validation = read(REC / 'review-validation.json')
    assert validation['all_passed'] and len(validation['checks']) == 9
    assert '10 passed' in (REC / 'mechanics-test.txt').read_text()
    assert read(REC / 'browser-check.json')['passed']
    (REC / 'source-check.json').write_text(json.dumps(dict(date='2026-10-22', checks=checks, all_passed=True), indent=2))

    macros, rows = [], []
    for domain, prefix, label in [('id', 'Id', '常规'), ('healthy', 'Healthy', '健康环境变化'), ('mass', 'Mass', '附加质量')]:
        data = read(REC / (domain + '-response.json'))
        result = data['result']
        status = '一致性检查通过' if data['accepted'] else '需要复核'
        vals = {'Scale': f"{result['scale']:.3f}", 'Residual': f"{result['hold_rms']:.2f}", 'Status': status}
        for key, value in vals.items():
            macros.append('\\newcommand{\\' + prefix + key + '}{' + value + '}')
        assert data['accepted'] == (result['hold_rms'] <= data['gate'])
        rows.append(f"{label} & {result['scale']:.3f} & {result['hold_rms']:.2f} & {data['gate']:.2f} & {status} " + r'\\')
    assert not read(REC / 'mass-response.json')['accepted']
    macros.append('\\newcommand{\\GateValue}{' + f"{data['gate']:.2f}" + '}')
    (REC / 'case-macros.tex').write_text('\n'.join(macros) + '\n')
    (REC / 'case-table.tex').write_text(r'\begin{tabular}{lrrrl}\toprule' + '\n' + r'案例 & 整体刚度估计 & 留出残差 & 阈值 & 状态\\\midrule' + '\n' + '\n'.join(rows) + '\n' + r'\bottomrule\end{tabular}' + '\n')

    # Regeneration-safe introduction: use the same expression as the report generator.
    summary = read(ROOT / 'results/run1/summary.json')
    metrics = {'HybridMAE': f"{summary['id']['hybrid']['mae_pp']:.3f}", 'Speedup': f"{summary['id']['exhaustive']['median_ms'] / summary['id']['hybrid']['median_ms']:.2f}"}
    tree = ast.parse((ROOT / 'scripts/present_results.py').read_text())
    assign = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'intro' for t in n.targets))
    intro = eval(compile(ast.Expression(assign.value), '<intro>', 'eval'), {'metrics': metrics})
    assert len(intro) <= 300
    entry = read(ROOT / 'entry.json')
    assert entry['description'] == intro and entry['description_characters'] == len(intro)
    (OUT / '参赛作品简介.txt').write_text(intro + '\n')

    named = ['src/beam.py', 'scripts/study.py', 'tests/test_mechanics.py', 'results/run1/records.json', 'results/run1/summary.json', 'results/run1/data.npz', 'results/run1/provenance.json', 'results/run2/provenance.json', 'results/run2/records.json', 'results/run2/data.npz', 'results/run1/calibration.json', 'results/run2/calibration.json', 'requirements.txt', 'demo/server.py', 'demo/lab.js', 'docs/SOURCES.md', 'docs/AI_USE.md', 'entry.json']
    named += [str(p.relative_to(ROOT)) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['file-manifest.json', 'hash-table.tex']]
    files = {name: {'sha256': digest(ROOT / name), 'bytes': (ROOT / name).stat().st_size} for name in named}
    (REC / 'file-manifest.json').write_text(json.dumps(dict(date='2026-10-22', note='Paths are project-relative. Full models and data stay in the main project.', files=files), ensure_ascii=False, indent=2))
    compact = ['src/beam.py', 'scripts/study.py', 'tests/test_mechanics.py', 'results/run1/records.json', 'results/run1/summary.json', 'results/run1/data.npz', 'output/evidence/records/browser-check.json', 'output/evidence/records/review-validation.json']
    lines = [r'\begin{tabular}{ll}\toprule 文件（项目相对路径） & SHA-256前12位\\\midrule']
    for name in compact:
        label = name.replace('output/evidence/records/', '…/records/')
        lines.append(r'\nolinkurl{' + label + '} & ' + r'\texttt{' + files[name]['sha256'][:12] + '} ' + r'\\')
    lines.append(r'\bottomrule\end{tabular}')
    (REC / 'hash-table.tex').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'source_checks': checks, 'intro_characters': len(intro), 'manifest_files': len(files)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
