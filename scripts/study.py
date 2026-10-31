"""AI-assisted experiment pipeline, Codex, 2026-10-13. See docs/AI_USE.md.
All splits have separate RNG streams. Test labels never select hyperparameters.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import sys,json,time,platform,hashlib,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import scipy,sklearn,joblib
from sklearn.ensemble import ExtraTreesRegressor
from beam import Beam,ZONES,FIT,HOLD,SIGMA,supports,invert,sample,conformal_quantile

def scientific_hash(a): return hashlib.sha256(np.asarray(a).tobytes()).hexdigest()
def plain(o):
    if isinstance(o,np.ndarray): return o.tolist()
    if isinstance(o,np.generic): return o.item()
    raise TypeError(type(o))

def predict(model,beam,obs):
    t=time.perf_counter(); y=model.predict(obs[FIT][None])[0]
    # AI proposes three positions: seven supports vs exhaustive twenty-two.
    ids=np.argsort(y[:ZONES])[-3:]
    ans=invert(beam,obs,supports(ids),initial=y)
    ans['seconds']=time.perf_counter()-t
    return ans,y

def metrics(rows):
    y=np.array([r['truth'][:ZONES] for r in rows]); p=np.array([r['d'] for r in rows])
    true=y>.05; pred=p>.05
    tp=np.sum(true&pred); fp=np.sum(~true&pred); fn=np.sum(true&~pred)
    healthy=~np.any(true,axis=1)
    return dict(n=len(rows),mae_pp=float(np.mean(abs(y-p))*100),
        damaged_mae_pp=float(np.mean(abs(y-p)[true])*100) if np.any(true) else None,
        f1=float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 1.,
        exact_support=float(np.mean(np.all(true==pred,axis=1))),
        healthy_false_alarm=float(np.mean(np.any(pred[healthy],axis=1))) if np.any(healthy) else None,
        median_ms=float(np.median([r['seconds'] for r in rows])*1000),
        mean_calls=float(np.mean([r['calls'] for r in rows])),
        mean_hold_rms=float(np.mean([r['hold_rms'] for r in rows])),
        success=float(np.mean([r['success'] for r in rows])))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='results/run1'); ap.add_argument('--quick',action='store_true'); args=ap.parse_args()
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    ntrain,ncal,ntest=(300,20,3) if args.quick else (2400,120,40)
    seeds=[11] if args.quick else [11,29,47]
    domains=['id','healthy','noise','mesh','triple','mass']
    beam=Beam(); fine=Beam(24)
    rows=[]; calibrations=[]; datasets={}; timings=[]; demo=[]
    for seed in seeds:
        t0=time.perf_counter()
        rng=np.random.default_rng(seed)
        train=[sample(beam,rng) for _ in range(ntrain)]
        X=np.array([a for a,b in train]); Y=np.array([b for a,b in train])
        model=ExtraTreesRegressor(n_estimators=160,min_samples_leaf=2,max_features=1.,n_jobs=1,random_state=seed)
        model.fit(X[:,FIT],Y)
        joblib.dump(model,out/f'model_{seed}.joblib',compress=3)
        print(f'seed {seed}: trained {ntrain} records',flush=True)
        crng=np.random.default_rng(10000+seed)
        cal=[sample(beam,crng) for _ in range(ncal)]
        cs=[]; hs=[]; predicted=[]
        for obs,y in cal:
            ans,_=predict(model,beam,obs); cs.append(np.max(abs(ans['d']-y[:ZONES]))); hs.append(ans['hold_rms']); predicted.append(ans['d'])
        q=conformal_quantile(cs); gate=conformal_quantile(hs,.05)
        calibrations.append(dict(seed=seed,n=ncal,alpha=.1,q=q,gate_alpha=.05,gate=gate,scores=cs,hold_scores=hs,predictions=predicted))
        datasets[f'train_X_{seed}']=X; datasets[f'train_Y_{seed}']=Y
        datasets[f'cal_X_{seed}']=np.array([a for a,b in cal]); datasets[f'cal_Y_{seed}']=np.array([b for a,b in cal])
        for di,domain in enumerate(domains):
            rng=np.random.default_rng(20000+100*seed+di)
            test=[sample(fine if domain=='mesh' else beam,rng,domain) for _ in range(ntest)]
            # For a mesh transfer, observed frequencies use the operational coarse reference.
            if domain=='mesh':
                for obs,y in test: obs[:5]+=np.log(fine.f0/beam.f0)
            datasets[f'{domain}_X_{seed}']=np.array([a for a,b in test]); datasets[f'{domain}_Y_{seed}']=np.array([b for a,b in test])
            for ix,(obs,y) in enumerate(test):
                ans,ai=predict(model,beam,obs)
                truth=y.tolist(); rid=f'{seed}_{domain}_{ix:03}'
                answers={'hybrid':ans}
                t=time.perf_counter(); aip=model.predict(obs[FIT][None])[0]; seconds=time.perf_counter()-t
                d=np.clip(aip[:ZONES],0,.65); a=float(np.exp(aip[-1])); f=beam.feature(d,a)
                answers['ai']=dict(d=d,scale=a,calls=1,seconds=seconds,success=True,hold_rms=float(np.sqrt(np.mean(((f[HOLD]-obs[HOLD])/SIGMA[HOLD])**2))))
                t=time.perf_counter(); exact=invert(beam,obs,supports()); exact['seconds']=time.perf_counter()-t; answers['exhaustive']=exact
                t=time.perf_counter(); fixed=invert(beam,obs,supports(),environment=False); fixed['seconds']=time.perf_counter()-t; answers['no_environment']=fixed
                for method,a in answers.items():
                    r=dict(id=rid,seed=seed,domain=domain,method=method,truth=truth,**a)
                    if method=='hybrid':
                        r.update(q=q,gate=gate,covered=bool(np.max(abs(a['d']-y[:ZONES]))<=q),accepted=bool(a['hold_rms']<=gate),interval_low=np.maximum(0,a['d']-q),interval_high=np.minimum(.65,a['d']+q))
                    rows.append(r)
                if seed==seeds[0] and ix<4:
                    demo.append(dict(id=rid,domain=domain,observation=obs,truth=y,hybrid=ans,ai=ai,interval=q,gate=gate))
            print(f'seed {seed}: {domain} {ntest} evaluated',flush=True)
        timings.append(dict(seed=seed,total_seconds=time.perf_counter()-t0))
    np.savez_compressed(out/'data.npz',**datasets)
    (out/'records.json').write_text(json.dumps(rows,default=plain,ensure_ascii=False,indent=2))
    (out/'calibration.json').write_text(json.dumps(calibrations,default=plain,indent=2))
    (out/'demo.json').write_text(json.dumps(demo,default=plain,ensure_ascii=False,indent=2))
    summary={}
    for domain in domains:
        summary[domain]={}
        for method in ['hybrid','ai','exhaustive','no_environment']:
            group=[r for r in rows if r['domain']==domain and r['method']==method]
            summary[domain][method]=metrics(group)
            if method=='hybrid':
                summary[domain][method].update(coverage=float(np.mean([r['covered'] for r in group])),acceptance=float(np.mean([r['accepted'] for r in group])),mean_width_pp=float(np.mean([np.mean(r['interval_high']-r['interval_low']) for r in group])*100))
        # Paired uncertainty computed over seed means, avoiding pretending all trials independent models.
        summary[domain]['per_seed']=[dict(seed=s,hybrid=metrics([r for r in rows if r['domain']==domain and r['method']=='hybrid' and r['seed']==s]),exhaustive=metrics([r for r in rows if r['domain']==domain and r['method']=='exhaustive' and r['seed']==s])) for s in seeds]
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    (out/'provenance.json').write_text(json.dumps(dict(seeds=seeds,ntrain=ntrain,ncal=ncal,ntest_per_domain_per_seed=ntest,domains=domains,source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('src/beam.py'),Path('scripts/study.py')]},dataset_array_hashes={k:scientific_hash(v) for k,v in datasets.items()},python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__,machine=platform.machine(),timings=timings,synthetic=True),indent=2))
    print(json.dumps(summary['id'],indent=2),flush=True)
if __name__=='__main__': main()
