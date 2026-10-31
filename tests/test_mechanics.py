"""Independent mechanics and inference checks; AI-assisted, Codex, 2026-10-13."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from scipy.linalg import eigh
from beam import Beam,supports,invert,conformal_quantile,FIT,HOLD

def test_analytic_cantilever_frequencies():
    b=Beam(24); roots=np.array([1.8751040687,4.694091133,7.854757438,10.995540735,14.137168391])
    exact=roots**2/(2*np.pi*b.length**2)*np.sqrt(b.E*b.I/(b.rho*b.area))
    assert np.max(abs(b.f0/exact-1))<.0002

def test_static_tip_deflection():
    b=Beam(); K,M=b.matrices(np.zeros(6)); f=np.zeros(len(K)); f[-2]=1.
    u=np.linalg.solve(K,f)
    assert u[-2]==pytest.approx(b.length**3/(3*b.E*b.I),rel=1e-9)

def test_eigen_equation_and_mass_orthogonality():
    b=Beam(); K,M=b.matrices(np.array([.1,0,.3,0,0,0]))
    w,v=eigh(K,M)
    assert np.linalg.norm(K@v[:,:5]-M@v[:,:5]*w[:5])/np.linalg.norm(K@v[:,:5])<1e-8
    assert np.max(abs(v.T@M@v-np.eye(len(w))))<1e-10

def test_uniform_environment_scaling():
    b=Beam(); f,p=b.modal(np.zeros(6),.9)
    assert np.max(abs(f/b.f0-np.sqrt(.9)))<1e-8
    assert np.max(abs(p-b.p0))<1e-8

def test_identifiability_boundary():
    b=Beam(); f1,p1=b.modal(np.full(6,.1),1.); f2,p2=b.modal(np.zeros(6),.9)
    assert np.max(abs(f1-f2))<1e-9
    assert np.max(abs(p1-p2))<1e-9

def test_clean_inverse():
    b=Beam(); d=np.array([0,.25,0,0,.18,0]); obs=b.feature(d,.94)
    r=invert(b,obs,supports())
    assert np.max(abs(r['d']-d))<1e-5
    assert abs(r['scale']-.94)<1e-5

def test_supports_and_holdout():
    assert len(supports())==22 and len(supports([1,2,4]))==7
    assert not set(FIT)&set(HOLD)
    assert set(FIT)|set(HOLD)==set(range(35))

def test_quantile_finite_sample_correction():
    assert conformal_quantile(np.arange(120),.1)==108

def test_mesh_convergence():
    b=Beam(12); b2=Beam(24); b3=Beam(48)
    d=np.array([0,.25,0,0,.18,0]); f1,_=b.modal(d); f2,_=b2.modal(d); f3,_=b3.modal(d)
    assert np.max(abs(f2/f3-1))<np.max(abs(f1/f3-1))
    assert np.max(abs(f1/f3-1))<.003

def test_invalid_inputs_rejected():
    with pytest.raises(ValueError): Beam(13)
    with pytest.raises(ValueError): Beam().feature(np.ones(6))
