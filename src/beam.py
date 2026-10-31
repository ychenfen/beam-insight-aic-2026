"""梁鉴 mechanics core. AI-assisted implementation, Codex, 2026-10-13.
Standard Euler-Bernoulli matrices, independently implemented; SI units.
No third-party repository source copied. See docs/SOURCES.md.
"""
from itertools import combinations
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import least_squares

ZONES = 6

class Beam:
    def __init__(self, elements=12):
        if elements % ZONES: raise ValueError('elements must be divisible by six')
        self.n = elements
        self.length, self.E, self.rho = 1.2, 70e9, 2700.
        self.width, self.height = .03, .006
        self.area = self.width * self.height
        self.I = self.width * self.height**3 / 12
        h = self.length / elements
        k = self.E*self.I/h**3*np.array([[12,6*h,-12,6*h],[6*h,4*h*h,-6*h,2*h*h],[-12,-6*h,12,-6*h],[6*h,2*h*h,-6*h,4*h*h]])
        m = self.rho*self.area*h/420*np.array([[156,22*h,54,-13*h],[22*h,4*h*h,13*h,-3*h*h],[54,13*h,156,-22*h],[-13*h,-3*h*h,-22*h,4*h*h]])
        ks = np.zeros((ZONES,2*elements+2,2*elements+2)); M=np.zeros_like(ks[0])
        for e in range(elements):
            ids=np.arange(2*e,2*e+4); z=e//(elements//ZONES)
            ks[z][np.ix_(ids,ids)]+=k; M[np.ix_(ids,ids)]+=m
        self.ks=ks[:,2:,2:]; self.M=M[2:,2:]
        self.sensor=(np.arange(1,ZONES+1)*(elements//ZONES)*2-2).astype(int)
        self.f0, self.p0=self.modal(np.zeros(ZONES))

    def matrices(self,d,scale=1.,mass=0.):
        d=np.asarray(d)
        if d.shape != (ZONES,) or np.any(d<0) or np.any(d>=1) or scale<=0:
            raise ValueError('invalid damage or stiffness scale')
        K=np.einsum('i,ijk->jk',scale*(1-d),self.ks)
        M=self.M.copy()
        # Unmodelled point mass at x/L=2/3, fraction of total beam mass.
        if mass: M[self.sensor[3],self.sensor[3]]+=mass*self.rho*self.area*self.length
        return K,M

    def modal(self,d,scale=1.,mass=0.):
        K,M=self.matrices(d,scale,mass)
        val,vec=eigh(K,M,subset_by_index=(0,4),check_finite=False,driver='gvx')
        phi=vec[self.sensor,:].T
        # Align against the tip. For the five modes studied, tip is not a node.
        phi=phi/phi[:,-1,None]
        return np.sqrt(val)/(2*np.pi),phi

    def feature(self,d,scale=1.,mass=0.):
        f,p=self.modal(d,scale,mass)
        return np.r_[np.log(f/self.f0),p.ravel()]

FIT=np.r_[np.arange(3),np.arange(5,23)]
HOLD=np.r_[np.arange(3,5),np.arange(23,35)]
SIGMA=np.r_[np.full(5,.001),np.full(30,.003)]

def supports(indices=range(ZONES)):
    ids=sorted(indices)
    return [()] + [(i,) for i in ids] + list(combinations(ids,2))

def invert(beam,obs,candidates,initial=None,environment=True):
    """Compare supports with Gaussian BIC. Identical objective/budget per support.
    The information criterion selects between zero, one and two damage zones.
    Noise scales are fixed before evaluation, never inferred from test labels.
    """
    best=None; calls=0
    for supp in candidates:
        s=len(supp)
        def unpack(x):
            d=np.zeros(ZONES); d[list(supp)]=x[:s]
            return d, np.exp(x[-1]) if environment else 1.
        def fun(x):
            nonlocal calls
            calls+=1; d,a=unpack(x)
            return (beam.feature(d,a)[FIT]-obs[FIT])/SIGMA[FIT]
        if not s and not environment:
            x=np.array([]); r=fun(x); success=True
        else:
            lo=[0.]*s+([np.log(.65)] if environment else [])
            hi=[.65]*s+([np.log(1.35)] if environment else [])
            x0=[.12]*s+([0.] if environment else [])
            if initial is not None:
                x0=list(np.clip(initial[list(supp)],.001,.64))+([np.clip(initial[-1],lo[-1]+1e-6,hi[-1]-1e-6)] if environment else [])
            sol=least_squares(fun,x0,bounds=(lo,hi),max_nfev=35,xtol=1e-7,ftol=1e-7,gtol=1e-6,diff_step=1e-4)
            x,r,success=sol.x,sol.fun,sol.success
        score=float(r@r + (s+int(environment))*np.log(len(FIT)))
        if best is None or score<best['bic']:
            d,a=unpack(x)
            best=dict(d=d,scale=a,bic=score,fit_rms=float(np.sqrt(np.mean(r*r))),success=bool(success),support=list(supp))
    best['calls']=calls
    pred=beam.feature(best['d'],best['scale'])
    best['hold_rms']=float(np.sqrt(np.mean(((pred[HOLD]-obs[HOLD])/SIGMA[HOLD])**2)))
    return best

def sample(beam,rng,domain='id'):
    d=np.zeros(ZONES); count=int(rng.choice([0,1,2],p=[.2,.5,.3]))
    if domain=='healthy': count=0
    if domain=='triple': count=3
    if count: d[rng.choice(ZONES,count,replace=False)]=rng.uniform(.08,.45,count)
    scale=rng.uniform(.88,1.12)
    noise=3 if domain=='noise' else 1
    mass=rng.uniform(.03,.08) if domain=='mass' else 0.
    obs=beam.feature(d,scale,mass)+rng.normal(size=35)*SIGMA*noise
    return obs,np.r_[d,np.log(scale)]

def conformal_quantile(scores,alpha=.1):
    scores=np.sort(scores); k=int(np.ceil((len(scores)+1)*(1-alpha)))
    if k>len(scores): return float('inf')
    return float(scores[k-1])
