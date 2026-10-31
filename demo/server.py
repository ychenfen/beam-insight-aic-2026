"""Local-only interactive demonstration. AI-assisted, Codex, 2026-10-13."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import numpy as np
import joblib
from scipy.linalg import eigh
from beam import Beam,sample
from study import predict,plain

beam=Beam(); model=joblib.load(ROOT/'results/run1/model_11.joblib')
cal=json.loads((ROOT/'results/run1/calibration.json').read_text())[0]

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'demo'),**kwargs)
    def do_GET(self):
        if self.path=='/api/evidence':
            payload=json.loads((ROOT/'results/run1/summary.json').read_text())
            return self.send_json(payload)
        return super().do_GET()
    def send_json(self,obj,status=200):
        data=json.dumps(obj,default=plain,ensure_ascii=False).encode()
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        if self.path!='/api/diagnose': return self.send_json({'error':'not found'},404)
        try:
            length=int(self.headers.get('Content-Length',0))
            if length>10000: raise ValueError('request too large')
            body=json.loads(self.rfile.read(length)); domain=body.get('domain','id')
            if domain not in ['id','healthy','noise','mesh','triple','mass']: raise ValueError('invalid domain')
            seed=int(body.get('seed',12345)); rng=np.random.default_rng(seed)
            sim=Beam(24) if domain=='mesh' else beam
            obs,y=sample(sim,rng,domain)
            if domain=='mesh': obs[:5]+=np.log(sim.f0/beam.f0)
            ans,ai=predict(model,beam,obs)
            K,M=beam.matrices(ans['d'],ans['scale'])
            ev,V=eigh(K,M,subset_by_index=(0,4),check_finite=False)
            V=np.vstack([np.zeros((2,5)),V]); V=V/V[-2]
            xs=np.linspace(0,1,121); shapes=[]
            for mode in range(5):
                yy=[]
                for x in xs:
                    e=min(int(x*beam.n),beam.n-1); t=x*beam.n-e; h=beam.length/beam.n
                    H=np.array([1-3*t*t+2*t**3,h*(t-2*t*t+t**3),3*t*t-2*t**3,h*(-t*t+t**3)])
                    yy.append(float(H@V[2*e:2*e+4,mode]))
                shapes.append(yy)
            return self.send_json(dict(result=ans,truth=y,ai=ai,observation=obs,q=cal['q'],gate=cal['gate'],accepted=ans['hold_rms']<=cal['gate'],seed=seed,domain=domain,frequencies=np.sqrt(ev)/(2*np.pi),render_x=xs,render_modes=shapes))
        except (ValueError,TypeError,KeyError) as exc: return self.send_json({'error':str(exc)},400)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--port',type=int,default=8766); args=ap.parse_args()
    print(f'梁鉴 local demo: http://127.0.0.1:{args.port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
