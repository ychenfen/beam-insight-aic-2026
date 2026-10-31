"""Render additional report tables from frozen results; no experiments are changed."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
summary = json.loads((ROOT / 'results/run1/summary.json').read_text())
rows = [r'\begin{tabular}{rrrrr}\toprule',
        r'模型种子 & 融合MAE & 穷举MAE & 融合/ms & 穷举/ms\\\midrule']
for row in summary['id']['per_seed']:
    h, e = row['hybrid'], row['exhaustive']
    rows.append(f"{row['seed']} & {h['mae_pp']:.3f} & {e['mae_pp']:.3f} & {h['median_ms']:.1f} & {e['median_ms']:.1f}" + r'\\')
rows += [r'\bottomrule\end{tabular}']
(ROOT / 'paper/generated/seed_table.tex').write_text('\n'.join(rows) + '\n')

cal = json.loads((ROOT / 'results/run1/calibration.json').read_text())
rows = [r'\begin{tabular}{rrrr}\toprule',
        r'模型种子 & 校准样本数 & 区间半径/百分点 & 残差门限\\\midrule']
for row in cal:
    rows.append(f"{row['seed']} & {row['n']} & {row['q']*100:.3f} & {row['gate']:.3f}" + r'\\')
rows += [r'\bottomrule\end{tabular}']
(ROOT / 'paper/generated/calibration_table.tex').write_text('\n'.join(rows) + '\n')
print('Full report tables generated from frozen run1 results.')
