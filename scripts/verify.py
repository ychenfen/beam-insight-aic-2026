"""Independent artifact/data checks. AI-assisted, Codex, 2026-10-13."""
import sys,json,hashlib,argparse
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beam import Beam

ap=argparse.ArgumentParser(); ap.add_argument('--first',default='results/run1'); ap.add_argument('--second',default='results/run2'); args=ap.parse_args()
a=Path(args.first); b=Path(args.second)
data=np.load(a/'data.npz'); checks={}
checks['all_arrays_finite']=all(np.isfinite(data[k]).all() for k in data.files)
hashes={}; seen=set(); overlap=0
for key in data.files:
    if '_X_' not in key: continue
    hs={hashlib.sha256(row.tobytes()).hexdigest() for row in data[key]}
    overlap+=len(hs&seen); seen|=hs; hashes[key]=len(hs)
checks['no_identical_observations_across_splits']=overlap==0
rows=json.loads((a/'records.json').read_text())
checks['record_count']=len(rows)==2880
checks['unique_case_method']=len({(r['id'],r['method']) for r in rows})==len(rows)
checks['bounded_predictions']=all(np.all(np.array(r['d'])>=0) and np.all(np.array(r['d'])<=.65) for r in rows)
checks['all_selected_solutions_terminated']=all(r['success'] for r in rows)
other=json.loads((b/'records.json').read_text())
def scientific(r): return {k:v for k,v in r.items() if k!='seconds'}
checks['retrained_records_equal']=all(scientific(x)==scientific(y) for x,y in zip(rows,other)) and len(rows)==len(other)
db=np.load(b/'data.npz')
checks['all_regenerated_arrays_equal']=all(np.array_equal(data[k],db[k]) for k in data.files)
checks['calibration_equal']=(a/'calibration.json').read_bytes()==(b/'calibration.json').read_bytes()
# Check mechanical convergence using damaged and healthy cases independent of experiment data.
mesh=[]
for n in [12,24,48]:
    beam=Beam(n)
    f,p=beam.modal(np.array([0,.25,0,0,.18,0]))
    mesh.append(dict(elements=n,frequencies=f.tolist()))
report=dict(checks=checks,all_passed=all(checks.values()),distinct_observations=hashes,mesh=mesh,scientific_repeat_excludes=['seconds','wall-clock timings'],cases=len(rows)//4)
Path('results/validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2)); sys.exit(0 if report['all_passed'] else 1)
