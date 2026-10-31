"""Independent mathematical checks for the accompanying derivation (stdlib only)."""
from fractions import Fraction as F
from pathlib import Path
import json, math, hashlib

HERE = Path(__file__).resolve().parent
checks = {}
def integral_product(a, b):
    return sum((F(x)*F(y)/F(i+j+1) for i,x in enumerate(a) for j,y in enumerate(b)),F(0))
def derivative(a): return [i*a[i] for i in range(1,len(a))]
def zeros(n): return [[0.0]*n for _ in range(n)]
def close(a,b,atol=1e-8): return abs(a-b)<=atol+1e-10*abs(b)
def same(a,b): return all(close(x,y) for ra,rb in zip(a,b) for x,y in zip(ra,rb))
def quad(a,x): return sum(x[i]*a[i][j]*x[j] for i in range(len(x)) for j in range(len(x)))
def solve(a,b):
    rows=[r[:]+[v] for r,v in zip(a,b)]; n=len(b)
    for k in range(n):
        p=max(range(k,n),key=lambda i:abs(rows[i][k]))
        rows[k],rows[p]=rows[p],rows[k]
        pivot=rows[k][k]; assert abs(pivot)>1e-12
        rows[k]=[v/pivot for v in rows[k]]
        for i in range(n):
            if i!=k:
                v=rows[i][k];rows[i]=[x-v*y for x,y in zip(rows[i],rows[k])]
    return [r[-1] for r in rows]

ell=F(1,10); EI=F(378,10); rhoA=F(486,1000)
n=[[1,0,-3,2],[0,1,-2,1],[0,0,3,-2],[0,0,-1,1]]
s=[0,1,0,1]
N=[[F(c)*ell**s[i] for c in row] for i,row in enumerate(n)]
B=[[v/ell**2 for v in derivative(derivative(row))] for row in N]
k=[[EI*ell*integral_product(a,b) for b in B] for a in B]
m=[[rhoA*ell*integral_product(a,b) for b in N] for a in N]
k_expected=[[453600,22680,-453600,22680],[22680,1512,-22680,756],[-453600,-22680,453600,-22680],[22680,756,-22680,1512]]
coeff=[[156,22,54,-13],[22,4,13,-3],[54,13,156,-22],[-13,-3,-22,4]]
checks['all_16_stiffness_integrals_exact']=k==k_expected
checks['all_16_mass_integrals_exact']=all(m[i][j]==rhoA*ell**(1+s[i]+s[j])*F(coeff[i][j],420) for i in range(4) for j in range(4))
checks['element_rigid_translation_zero_energy']=quad(k,[1,0,1,0])==0
checks['element_rigid_rotation_zero_energy']=quad(k,[0,1,ell,1])==0
zones=[zeros(26) for _ in range(6)];mass=zeros(26)
for e in range(12):
    for i in range(4):
        for j in range(4):
            zones[e//2][2*e+i][2*e+j]+=float(k[i][j])
            mass[2*e+i][2*e+j]+=float(m[i][j])
checks['total_translational_mass']=close(quad(mass,[1.0,0.0]*13),.5832)
zones=[[r[2:] for r in z[2:]] for z in zones]
mass=[r[2:] for r in mass[2:]]
def stiffness(d,a): return [[sum(a*(1-d[z])*zones[z][i][j] for z in range(6)) for j in range(24)] for i in range(24)]
K0=stiffness([0]*6,1);d=[0,.2,0,0,0,0];alpha=.95;K=stiffness(d,alpha)
checks['constrained_size']=len(K)==24 and all(len(r)==24 for r in K)
checks['symmetry']=same(K,list(map(list,zip(*K))))
checks['worked_example']=same(K,[[.95*K0[i][j]-.19*zones[1][i][j] for j in range(24)] for i in range(24)])
L= zeros(24)
for i in range(24):
    for j in range(i+1):
        v=K[i][j]-sum(L[i][p]*L[j][p] for p in range(j))
        if i==j:
            assert v>0,(i,v)
            L[i][j]=math.sqrt(v)
        else: L[i][j]=v/L[j][j]
checks['positive_definite_cholesky']=same(K,[[sum(L[i][p]*L[j][p] for p in range(24)) for j in range(24)] for i in range(24)])
x=[math.sin(i+1)*.001 for i in range(24)]
loss=(quad(stiffness([0]*6,alpha),x)-quad(K,x))/2
expected=alpha/2*sum(d[z]*quad(zones[z],x) for z in range(6))
checks['energy_loss_identity']=close(loss,expected) and loss>=0
eps=1e-5;ds=d[:];ds[1]+=eps
Kp=stiffness(ds,alpha)
checks['damage_derivative']=all(close((Kp[i][j]-K[i][j])/eps,-alpha*zones[1][i][j],atol=2e-5) for i in range(24) for j in range(24))
Ka=stiffness(d,alpha+eps)
checks['environment_derivative']=all(close((Ka[i][j]-K[i][j])/eps,K[i][j]/alpha,atol=2e-5) for i in range(24) for j in range(24))
f=[0.0]*24;f[-2]=1;u=solve(K0,f);tip=1.2**3/(3*37.8)
checks['unit_tip_load_analytic_deflection']=close(u[-2],tip,atol=1e-11)
checks['uniform_damage_environment_equivalence']=same(stiffness([.1]*6,1),stiffness([0]*6,.9))
t=1.1
checks['general_parameter_equivalence']=same(K,stiffness([1-(1-v)/t for v in d],t*alpha))
assert all(checks.values()),checks
result={'status':'passed','checks':checks,'check_count':len(checks),'tip_deflection_m':u[-2],'analytic_tip_deflection_m':tip,'total_beam_mass_kg':.5832,'scope':'Independent derivation checks; no new experimental measurements or model training.','source_sha256':hashlib.sha256((HERE/'main.tex').read_bytes()).hexdigest()}
(HERE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
