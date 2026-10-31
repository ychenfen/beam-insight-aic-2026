"""Generate every reported number and chart from frozen outputs. AI-assisted, 2026-10-13."""
from pathlib import Path
import json,csv,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path('results/run1'); OUT=Path('paper/generated'); OUT.mkdir(parents=True,exist_ok=True)
s=json.loads((BASE/'summary.json').read_text()); rows=json.loads((BASE/'records.json').read_text())
c=json.loads((BASE/'calibration.json').read_text()); prov=json.loads((BASE/'provenance.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#163c38','text.color':'#163c38','axes.edgecolor':'#bdccc5','figure.facecolor':'white','savefig.bbox':'tight','pdf.fonttype':42})
colors=['#216b62','#bb6949','#607b96','#ac9c75']; methods=['hybrid','ai','exhaustive','no_environment']; names=['AI + physics','AI only','Exhaustive physics','No environment']
domains=['id','healthy','noise','mesh','triple','mass']; dn=['In-domain','Healthy / env.','3x noise','Finer mesh','3 damaged zones','Extra mass']
def save(fig,name):
    fig.savefig(OUT/f'{name}.pdf');fig.savefig(OUT/f'{name}.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(1,3,figsize=(10.4,2.7),layout='constrained')
for a,key,label in zip(ax,['mae_pp','median_ms','mean_calls'],['Damage MAE / percentage points','Median latency / ms','Mean inversion calls']):
    mm=methods[:3] if key!='mean_calls' else ['hybrid','exhaustive']
    labs=['Hybrid','AI','Exhaustive'] if key!='mean_calls' else ['Hybrid','Exhaustive']
    cc=colors[:3] if key!='mean_calls' else [colors[0],colors[2]]
    vals=[s['id'][m][key] for m in mm]
    a.bar(np.arange(len(mm)),vals,color=cc,width=.55)
    a.set_xticks(range(len(mm)),labs);a.set_title(label,fontsize=10)
    for i,v in enumerate(vals):a.text(i,v+max(vals)*.04,f'{v:.3f}' if key=='mae_pp' else f'{v:.1f}',ha='center',fontsize=10)
    a.set_ylim(0,max(vals)*1.24);a.grid(axis='y',alpha=.15)
save(fig,'headline')

fig,ax=plt.subplots(1,2,figsize=(10.4,3.5),layout='constrained')
x=np.arange(6)
for j,m in enumerate(methods):ax[0].plot(x,[s[d][m]['mae_pp'] for d in domains],marker='o',color=colors[j],label=names[j])
ax[0].set_xticks(x,dn,rotation=30,ha='right');ax[0].set_ylabel('MAE / percentage points');ax[0].legend(fontsize=8);ax[0].grid(alpha=.15)
ax[1].bar(x-.17,[s[d]['hybrid']['coverage']*100 for d in domains],width=.34,color=colors[0],label='Simultaneous coverage')
ax[1].bar(x+.17,[s[d]['hybrid']['acceptance']*100 for d in domains],width=.34,color=colors[1],label='Gate acceptance')
ax[1].axhline(90,color='#555',lw=1,ls='--',label='Nominal coverage: 90%');ax[1].set_ylim(0,112);ax[1].set_xticks(x,dn,rotation=30,ha='right');ax[1].set_ylabel('% of 120 cases');ax[1].legend(fontsize=8,loc='upper right')
save(fig,'robustness')

hy=[r for r in rows if r['method']=='hybrid']
fig,ax=plt.subplots(1,2,figsize=(10.4,3.0),layout='constrained')
for di,d in enumerate(domains):
    rr=[r for r in hy if r['domain']==d]
    ax[0].scatter([r['hold_rms']/r['gate'] for r in rr],[np.mean(abs(np.array(r['d'])-r['truth'][:6]))*100 for r in rr],s=13,alpha=.55,label=dn[di])
ax[0].axvline(1,c='black',ls='--',lw=1);ax[0].set_xscale('log');ax[0].set_xlabel('Held-out residual / calibrated threshold');ax[0].set_ylabel('MAE / percentage points');ax[0].legend(fontsize=7,ncol=2)
rr=[r for r in hy if r['domain']=='id' and r['seed']==11]
ex=next(r for r in rr if sum(np.array(r['truth'][:6])>.05)==2)
x=np.arange(1,7);p=np.array(ex['d']);y=np.array(ex['truth'][:6]);lo=np.array(ex['interval_low']);hi=np.array(ex['interval_high'])
ax[1].bar(x-.17,y*100,width=.34,color=colors[1],label='Truth');ax[1].bar(x+.17,p*100,width=.34,color=colors[0],label='Hybrid');ax[1].errorbar(x+.17,p*100,yerr=[(p-lo)*100,(hi-p)*100],fmt='none',ecolor='#173331',capsize=3)
ax[1].set_xlabel('Zone (fixed end to free end)');ax[1].set_ylabel('Stiffness loss / %');ax[1].set_title('Predefined example: first two-damage case, seed 11',fontsize=9);ax[1].legend(fontsize=8)
save(fig,'diagnostics')

fig,ax=plt.subplots(figsize=(10.4,2.3),layout='constrained');ax.axis('off')
steps=[('OBSERVATION','5 frequencies\n6 sensors x 5 modes'),('AI PROPOSAL','Extra Trees\nTop 3 zones'),('PHYSICS','7 support candidates\nBounded inversion + BIC'),('AUDIT','Modes 4-5 held out\nCalibrated residual gate')]
for i,(title,desc) in enumerate(steps):
    x=.01+i*.255
    ax.add_patch(plt.Rectangle((x,.28),.225,.55,facecolor='#edf2ee',edgecolor='#216b62'))
    ax.text(x+.1125,.68,title,ha='center',fontsize=10,fontweight='bold');ax.text(x+.1125,.47,desc,ha='center',va='center',fontsize=9)
    if i<3:ax.annotate('',(x+.25,.555),(x+.23,.555),arrowprops={'arrowstyle':'->','color':'#bb6949'})
ax.text(.5,.1,'Calibration split: simultaneous damage intervals  |  Test split: labels used only for scoring',ha='center',fontsize=9)
save(fig,'workflow')

with (OUT/'metrics.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['domain','method','n','mae_pp','damaged_mae_pp','f1','exact_support','median_ms','mean_calls','coverage','acceptance'])
    for d in domains:
        for m in methods:
            r=s[d][m];w.writerow([d,m]+[r.get(k,'') for k in ['n','mae_pp','damaged_mae_pp','f1','exact_support','median_ms','mean_calls','coverage','acceptance']])

metrics={
'HybridMAE':f"{s['id']['hybrid']['mae_pp']:.3f}",'PhysicsMAE':f"{s['id']['exhaustive']['mae_pp']:.3f}",'AIMAE':f"{s['id']['ai']['mae_pp']:.3f}",
'HybridTime':f"{s['id']['hybrid']['median_ms']:.1f}",'PhysicsTime':f"{s['id']['exhaustive']['median_ms']:.1f}",'AITime':f"{s['id']['ai']['median_ms']:.1f}",
'Speedup':f"{s['id']['exhaustive']['median_ms']/s['id']['hybrid']['median_ms']:.2f}",'CallSaving':f"{100*(1-s['id']['hybrid']['mean_calls']/s['id']['exhaustive']['mean_calls']):.1f}",
'Coverage':f"{s['id']['hybrid']['coverage']*100:.1f}",'Width':f"{s['id']['hybrid']['mean_width_pp']:.2f}",'Accept':f"{s['id']['hybrid']['acceptance']*100:.1f}",
'HealthyFalseAblation':f"{s['healthy']['no_environment']['healthy_false_alarm']*100:.1f}",'MeshMAE':f"{s['mesh']['hybrid']['mae_pp']:.3f}",
'TripleMAE':f"{s['triple']['hybrid']['mae_pp']:.2f}",'MassMAE':f"{s['mass']['hybrid']['mae_pp']:.2f}",'NoiseMAE':f"{s['noise']['hybrid']['mae_pp']:.3f}",
'FullSeconds':f"{sum(r['total_seconds'] for r in prov['timings']):.1f}",
'HybridDamagedMAE':f"{s['id']['hybrid']['damaged_mae_pp']:.3f}"}
(OUT/'metrics.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in metrics.items())+'\n')
lines=[]
for d,n in zip(domains,['常规域','健康环境变化','三倍噪声','加密网格','三处损伤','附加质量']):
    r=s[d]['hybrid'];lines.append(f"{n} & {r['mae_pp']:.3f} & {r['exact_support']*100:.1f} & {r['coverage']*100:.1f} & {r['acceptance']*100:.1f} \\\\")
(OUT/'domain_rows.tex').write_text('\n'.join(lines)+'\n')
(OUT/'domain_table.tex').write_text('\\begin{tabular}{lrrrr}\\toprule\n测试域（各120例） & MAE/百分点 & 定位完全匹配/\\% & 区间覆盖/\\% & 校核接受/\\%\\\\\\midrule\n'+'\n'.join(lines)+'\n\\bottomrule\\end{tabular}\n')
lines=[]
for m,n in zip(methods,['AI+力学校核','纯AI','穷举物理反演','不估计环境（消融）']):
    r=s['id'][m];lines.append(f"{n} & {r['mae_pp']:.3f} & {r['damaged_mae_pp']:.3f} & {r['f1']:.3f} & {r['median_ms']:.1f} \\\\")
(OUT/'method_rows.tex').write_text('\n'.join(lines)+'\n')
(OUT/'method_table.tex').write_text('\\begin{tabular}{lrrrr}\\toprule\n常规域方法 & 全区MAE/百分点 & 受损区MAE/百分点 & 定位F1 & 中位耗时/ms\\\\\\midrule\n'+'\n'.join(lines)+'\n\\bottomrule\\end{tabular}\n')
title='梁鉴：环境扰动下的损伤识别'
intro=f"梁鉴面向力学教学与试验梁研究，解决环境刚度变化与局部损伤易混淆的问题。作品以随机树筛选可疑分区，结合有限元反演估计损伤，并用留出模态与校准区间检查结果。通过三组模型、六类工况共720例独立仿真测试，常规域120例的全区平均损伤误差为{metrics['HybridMAE']}个百分点，中位推理耗时为穷举基线的1/{metrics['Speedup']}。系统支持三维振型交互、分区损伤展示及失配复核，保留完整源码与逐例记录，可用于教学演示和算法研究；尚未经实物验证。"
assert len(title)<=20 and len(intro)<=300
entry_path=Path('entry.json')
entry=json.loads(entry_path.read_text()) if entry_path.exists() else dict(team_id=None,team_name=None)
entry.update(title=title,short_title='梁鉴',track='开放式赛题',disciplines=['固体力学','动力学与控制'],description=intro,description_characters=len(intro),status='local_candidate_pending_team_review')
new_entry=json.dumps(entry,ensure_ascii=False,indent=2)
if not entry_path.exists() or new_entry!=entry_path.read_text():
    if entry_path.exists():
        import shutil,datetime
        backup=Path('archives/config');backup.mkdir(parents=True,exist_ok=True)
        shutil.copy2(entry_path,backup/('entry-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json'))
    entry_path.write_text(new_entry)
print(json.dumps(metrics,ensure_ascii=False,indent=2))
