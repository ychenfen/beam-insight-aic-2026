// AI-assisted scientific visualization. FE Hermite interpolation supplied by server.
const $=id=>document.getElementById(id), pc=x=>(100*x).toFixed(1)+'%';
let data=null, mode=0, paused=matchMedia('(prefers-reduced-motion: reduce)').matches;
let angle=-.38, elevation=.43, drag=null, phase=0, previous=0;
const canvas=$('beam'),ctx=canvas.getContext('2d');
const palette=[[104,146,140],[170,212,177],[229,195,129],[209,120,84]];
function colour(v,alpha=1){let t=Math.min(.9999,Math.max(0,v/.65))*3,i=Math.floor(t),f=t-i;let c=palette[i].map((a,j)=>Math.round(a+(palette[Math.min(i+1,3)][j]-a)*f));return `rgba(${c.join(',')},${alpha})`;}
function project(x,y,z,w,h){let X=(x-.5)*560,Y=y*560,Z=z*560;let xx=X*Math.cos(angle)-Y*Math.sin(angle),yy=X*Math.sin(angle)+Y*Math.cos(angle);let zz=Z*Math.cos(elevation)-yy*Math.sin(elevation);return [w*.51+xx*w/780,h*.49-zz*w/780];}
function draw(t){let box=canvas.getBoundingClientRect(),w=box.width,h=box.height,dpr=Math.min(devicePixelRatio||1,2);if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);if(!paused&&previous)phase+=(t-previous)/1000*1.8;previous=t;const p=(x,y,z)=>project(x,y,z,w,h);
 function line(points,stroke,width=1,dash=[]){ctx.beginPath();points.forEach((v,i)=>{let q=p(...v);i?ctx.lineTo(...q):ctx.moveTo(...q)});ctx.strokeStyle=stroke;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([])}
 function face(points,fill,stroke){ctx.beginPath();points.forEach((v,i)=>{let q=p(...v);i?ctx.lineTo(...q):ctx.moveTo(...q)});ctx.closePath();ctx.fillStyle=fill;ctx.fill();ctx.strokeStyle=stroke;ctx.lineWidth=.6;ctx.stroke();}
 for(let x=-.1;x<=1.11;x+=.1)line([[x,-.3,-.2],[x,.3,-.2]],'#294047',.5);
 for(let y=-.3;y<=.31;y+=.1)line([[-.1,y,-.2],[1.1,y,-.2]],'#294047',.5);
 line([[0,0,0],[1,0,0]],'#6c8788',1,[4,5]);
 face([[0,-.1,-.1],[0,.1,-.1],[0,.1,.18],[0,-.1,.18]],'#394f54','#728d8c');
 for(let z=-.08;z<.18;z+=.04)line([[0,-.1,z],[0,.1,z+.04]],'#577175',1);
 let shape=data?data.render_modes[mode]:Array.from({length:121},(_,i)=>((i/120)**2));let norm=Math.max(...shape.map(Math.abs),1),amp=.11*Math.sin(phase);
 let points=shape.map((v,i)=>[i/120,v/norm*amp]);
 for(let i=0;i<120;i++){let x1=points[i][0],x2=points[i+1][0],z1=points[i][1],z2=points[i+1][1],zone=Math.min(5,Math.floor(x1*6));let d=data?data.result.d[zone]:0;
  face([[x1,-.018,z1-.006],[x2,-.018,z2-.006],[x2,-.018,z2+.006],[x1,-.018,z1+.006]],colour(d,.55),'transparent');
  face([[x1,-.018,z1+.006],[x2,-.018,z2+.006],[x2,.018,z2+.006],[x1,.018,z1+.006]],colour(d),colour(d));
 }
 for(let i=0;i<=6;i++){let x=i/6,z=points[i*20][1];line([[x,-.021,z+.007],[x,.021,z+.007]],'#e3eee4',1);if(i){let q=p(x,0,z+.007);ctx.beginPath();ctx.arc(q[0],q[1],3,0,Math.PI*2);ctx.fillStyle='#e9eee3';ctx.fill();}}
 for(let i=0;i<6;i++){let x=(i+.5)/6,q=p(x,-.16,-.2);ctx.font='10px Menlo,monospace';ctx.fillStyle='#a0b4b2';ctx.textAlign='center';ctx.fillText('0'+(i+1),...q);line([[x,-.13,-.2],[x,-.1,-.06]],'#526c70',.5);}
 let a=p(0,-.29,-.2),b=p(1,-.29,-.2);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.strokeStyle='#526d71';ctx.stroke();ctx.font='9px Menlo,monospace';ctx.fillStyle='#90a8a8';ctx.textAlign='center';ctx.fillText('L = 1.20 m',(a[0]+b[0])/2,(a[1]+b[1])/2+16);
 if(!window.__freezeViz)requestAnimationFrame(draw);
}
canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY,angle,elevation];canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(drag){angle=Math.max(-1.2,Math.min(.5,drag[2]+(e.clientX-drag[0])*.004));elevation=Math.max(.15,Math.min(.9,drag[3]+(e.clientY-drag[1])*.003));}});canvas.addEventListener('pointerup',()=>drag=null);canvas.addEventListener('pointercancel',()=>drag=null);
$('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'播放振型':'暂停振型'};$('pause').textContent=paused?'播放振型':'暂停振型';$('reset').onclick=()=>{angle=-.38;elevation=.43};$('mode').onchange=()=>{mode=+$('mode').value;updateMode()};
function updateMode(){if(!data)return;$('modeTitle').textContent='MODE 0'+(mode+1);$('frequency').textContent=data.frequencies[mode].toFixed(2)+' Hz';}
function plot(d){let r=d.result,s='';const left=38,base=202,scale=240;
 for(let v=0;v<=.61;v+=.2){let y=base-v*scale;s+=`<line x1="${left}" y1="${y}" x2="742" y2="${y}" stroke="#34494f" stroke-width=".6"/><text x="25" y="${y+4}" text-anchor="end" font-size="10" fill="#879f9f">${Math.round(v*100)}</text>`;}
 for(let i=0;i<6;i++){let x=70+i*113,y=base-r.d[i]*scale,ty=base-d.truth[i]*scale,lo=base-Math.max(0,r.d[i]-d.q)*scale,hi=base-Math.min(.65,r.d[i]+d.q)*scale;s+=`<rect x="${x}" y="${y}" width="30" height="${base-y}" fill="#a6d9bc"/><rect x="${x+34}" y="${ty}" width="30" height="${base-ty}" fill="#e5aa70"/><path d="M${x+15} ${hi}V${lo}M${x+10} ${hi}h10M${x+10} ${lo}h10" fill="none" stroke="#e8ece6" stroke-width="1"/><text x="${x+32}" y="229" text-anchor="middle" font-size="11" fill="#a6bcb5">0${i+1}</text>`;}
 $('chart').innerHTML=s;
}
async function run(){let b=$('run');b.disabled=true;b.textContent='正在求解…';$('error').textContent='';try{let resp=await fetch('/api/diagnose',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({domain:$('domain').value,seed:+$('seed').value})});let d=await resp.json();if(!resp.ok)throw Error(d.error);data=d;let r=d.result;updateMode();plot(d);$('scale').textContent=r.scale.toFixed(3);$('residual').textContent=r.hold_rms.toFixed(2);$('latency').textContent=(r.seconds*1000).toFixed(0);$('gate').textContent='校准阈值 '+d.gate.toFixed(2);$('badge').textContent=d.accepted?'一致性检查通过':'超出阈值 / 需要复核';$('badge').className='badge'+(d.accepted?'':' reject');$('conclusion').textContent=d.accepted?'观测与模型基本一致':'本次结果不宜直接采信';$('explain').textContent=`第4、5阶留出模态的标准化残差为 ${r.hold_rms.toFixed(2)}，${d.accepted?'低于':'高于'}校准阈值 ${d.gate.toFixed(2)}。六分区同时区间的校准半宽为 ${pc(d.q)}。`;$('table').innerHTML=r.d.map((v,i)=>`<tr><td>0${i+1} / ${(i/6).toFixed(2)}–${((i+1)/6).toFixed(2)} L</td><td>${pc(d.truth[i])}</td><td>${pc(v)}</td><td>[${pc(Math.max(0,v-d.q))}, ${pc(Math.min(.65,v+d.q))}]</td></tr>`).join('');}catch(e){$('error').textContent='计算失败：'+e.message}finally{b.disabled=false;b.innerHTML='运行诊断 <span>↗</span>';}}
$('run').onclick=run;requestAnimationFrame(draw);run();
