// AI-assisted: editable slide reconstruction from defense.tex and frozen run1 results.
// Usage: NODE_PATH=<bundled node_modules> node scripts/build_editable_pptx.cjs
const fs=require('fs'),path=require('path');
const pptxgen=require('pptxgenjs');
const sharp=require('sharp');
const html2pptx=require(process.env.HTML2PPTX_MODULE || '/Users/yuchenxu/.codex/skills/pptx/scripts/html2pptx.js');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'output/pptx'),WORK=path.join(ROOT,'work/pptx');
fs.mkdirSync(OUT,{recursive:true});fs.mkdirSync(WORK,{recursive:true});
const summary=JSON.parse(fs.readFileSync(path.join(ROOT,'results/run1/summary.json')));
const entry=JSON.parse(fs.readFileSync(path.join(ROOT,'entry.json')));
const C={ink:'111D22',green:'216B62',paper:'F5F4EE',mint:'A6D9BC',ochre:'B56D47',blue:'607D98',muted:'657873',line:'CED7CF',pale:'E5EDE5'};
const pptx=new pptxgen();pptx.defineLayout({name:'BEAM',width:10,height:5.625});pptx.layout='BEAM';
pptx.author='';pptx.subject='2026 AIC AI+力学开放式赛题 · 仿真研究原型';pptx.title=entry.title;
pptx.company='';pptx.lang='zh-CN';pptx.theme={headFontFace:'Arial',bodyFontFace:'Arial',lang:'zh-CN'};
const ST=pptx.ShapeType;
function tx(s,t,x,y,w,h,size=16,color=C.ink,bold=false,extra={}){s.addText(t,{x,y,w,h,fontFace:'Arial',fontSize:size,color,bold,margin:0,breakLine:false,valign:'mid',...extra});}
function line(s,x,y,w,h=0,color=C.line,width=.7){s.addShape(ST.line,{x,y,w,h,line:{color,width}});}
function rect(s,x,y,w,h,color){s.addShape(ST.rect,{x,y,w,h,fill:{color},line:{color,transparency:100}});}
function note(s,text){s.addNotes(text+'\n\n内容依据：paper/defense.tex、paper/full_report.tex；实验数据：results/run1/summary.json。全部为合成数据，团队名称及人工审核待补。');}
function foot(s,i,dark=false){tx(s,'梁鉴 / AI+力学开放式赛题',.5,5.24,5,.16,8,dark?C.mint:C.muted);tx(s,'仿真研究原型',7.7,5.24,1.2,.16,8,dark?C.mint:C.muted);tx(s,String(i).padStart(2,'0'),9.15,5.22,.3,.2,9,dark?C.mint:C.muted,false,{align:'right'});}
async function base(i,title,dark=false){
 const html=`<!DOCTYPE html><html><body style="width:720pt;height:405pt;margin:0;padding:0;display:flex;position:relative;background:#${dark?C.ink:C.paper};font-family:Arial,sans-serif;">
 ${title?`<h1 style="position:absolute;left:36pt;top:24pt;margin:0;width:648pt;font-size:23pt;line-height:1.2;color:#${C.green};font-weight:normal;">${title}</h1><div style="position:absolute;left:36pt;top:66pt;width:648pt;height:0;border-top:0.75pt solid #${C.green};"></div>`:''}</body></html>`;
 const f=path.join(WORK,`slide-${String(i).padStart(2,'0')}.html`);fs.writeFileSync(f,html);
 const {slide:s}=await html2pptx(f,pptx);foot(s,i,dark);return s;
}
function table(s,rows,x,y,w,colW,size=13,rowH=.55){s.addTable(rows.map((r,i)=>r.map(t=>({text:String(t),options:i===0?{bold:true,color:C.green,fill:C.pale}:{color:C.ink,fill:C.paper}}))),{x,y,w,colW,rowH,fontFace:'Arial',fontSize:size,margin:[7,8,7,8],border:{type:'solid',pt:.5,color:C.line},color:C.ink,fill:C.paper,autoPage:false,valign:'mid'});}
function chart(s,type,data,x,y,w,h,opts={}){s.addChart(type,data,{x,y,w,h,showTitle:false,showLegend:false,showBorder:false,chartArea:{fill:{color:C.paper},border:{color:C.paper,transparency:100}},plotArea:{fill:{color:C.paper},border:{color:C.paper,transparency:100}},showCatName:false,showValue:true,showCatAxisTitle:false,showValAxisTitle:false,showMarker:false,showLine:true,showCatName:false,fontFace:'Arial',catAxisLabelFontFace:'Arial',valAxisLabelFontFace:'Arial',catAxisLabelFontSize:10,valAxisLabelFontSize:9,dataLabelFormatCode:'0.0',dataLabelPosition:'outEnd',dataLabelColor:C.ink,dataLabelBkgrdColor:C.paper,dataLabelColor:C.green,dataLabelFormatCode:'0.0',dataLabelFontSize:10,catAxisLineColor:C.line,valAxisLineColor:C.line,catAxisLineSize:.5,valAxisLineSize:.5,valGridLine:{color:C.line,width:.4},catAxisLabelColor:C.ink,valAxisLabelColor:C.muted,showCatName:false,valAxisMinVal:0,showShadow:false,chartColors:[C.green,C.ochre,C.blue,'A59773'],...opts});}
async function main(){
 let s=await base(1,'',true);
 tx(s,'AI + MECHANICS   /   AIC 2026',.62,.55,8,.25,12,C.mint);
 tx(s,'梁鉴',.62,1.28,8,.9,52,C.paper,true);
 tx(s,'环境扰动下的损伤识别',.62,2.28,8.8,.65,30,C.paper);
 line(s,.65,3.33,8.7,0,'425953',.8);
 tx(s,'AI筛选候选位置  /  物理反演与独立模态校核',.65,3.65,8.8,.5,19,C.mint);
 tx(s,'六分区悬臂梁 · 720个独立仿真测试工况',.65,4.55,7,.3,13,C.paper);
 tx(s,entry.team_id||'团队编号待补',7.5,4.55,1.85,.3,11,C.mint,false,{align:'right'});
 note(s,'开场：频率下降究竟来自环境还是损伤？本文研究已知健康参考的六分区试验梁，用AI缩小搜索，再以力学检查结论。当前结果仅为仿真。');

 s=await base(2,'01  同样是频率下降，原因可能不同');
 tx(s,'环境变化',.65,1.35,4,.45,24,C.green,true);tx(s,'局部损伤',5.4,1.35,4,.45,24,C.green,true);
 line(s,4.93,1.35,0,2.35);
 tx(s,'K = αK₀',.65,2.05,4,.55,29);tx(s,'K = α Σⱼ (1 − dⱼ) Kⱼ⁰',5.4,2.05,4,.55,25);
 tx(s,'频率统一乘以 √α\n归一化振型不变',.65,2.97,4,1,19);tx(s,'不同分区改变不同模态\n但变化可能很小',5.4,2.97,4,1,19);
 tx(s,'均匀损伤与整体模量变化，仅凭模态不可辨识。',.65,4.25,8.7,.35,17,C.ochre,true);
 tx(s,'研究范围：已知健康参考、少数局部损伤的教学与试验梁。',.65,4.73,8.7,.25,12,C.muted);
 note(s,'若所有分区损伤均为c，刚度矩阵为α(1−c)K₀，只能辨识乘积。稀疏损伤假设是使用条件，不是算法自动证明的普遍事实。公式为可编辑文字。');

 s=await base(3,'02  AI缩小搜索，力学估计参数');
 const stages=[['01','观测','5阶频率\n6点振型'],['02','AI提议','160棵随机树\n前三候选分区'],['03','物理反演','7个支持集\n有界求解＋BIC'],['04','独立检查','留出第4、5阶\n校准残差门限']];
 stages.forEach((a,i)=>{let x=.6+2.28*i;rect(s,x,1.55,2.05,1.65,C.pale);tx(s,a[0],x+.15,1.68,1,.25,11,C.ochre);tx(s,a[1],x+.15,2.05,1.75,.35,20,C.green,true);tx(s,a[2],x+.15,2.53,1.8,.5,13);if(i<3)tx(s,'→',x+2.08,2.15,.2,.4,18,C.ochre);});
 tx(s,'22 → 7',.65,3.65,3,.6,32,C.green);tx(s,'损伤位置候选组合',.65,4.32,3,.3,13,C.muted);
 tx(s,'第1—3阶用于学习与拟合\n第4—5阶只校核，不回流调参',4,3.65,5.3,.9,19);
 tx(s,'贡献：问题建模、融合与校核流程；基础算法来自已有方法。',.65,4.82,8.8,.25,12,C.muted);
 note(s,'空集、3个单区、3个双区构成7候选；全六区穷举为22候选。融合方案还采用AI初值，因此速度差不能全部归因于候选数量。流程图的每个框、连接和文字均可编辑。');

 s=await base(4,'03  模型与每一个量都能校核');
 rect(s,.65,1.9,.18,1.3,'A7B3AD');
 for(let i=0;i<6;i++){rect(s,.83+i*.68,2.32,.67,.25,i===1?C.ochre:'BDD4C6');tx(s,String(i+1),.85+i*.68,2.7,.62,.25,12,C.muted,false,{align:'center'});}
 line(s,.83,3.15,4.08,0,C.green,1);tx(s,'1.20 m',1.65,3.28,2.3,.3,15,C.green,false,{align:'center'});
 tx(s,'六分区 · 12个梁单元 · 左端固支',.65,3.9,4.7,.35,16);
 tx(s,'截面 30 × 6 mm   /   E = 70 GPa',.65,4.37,4.7,.35,14,C.muted);
 tx(s,'Kφ = ω²Mφ',5.55,1.65,3.8,.6,30,C.green);
 tx(s,'解析频率     端部静挠度\n质量正交     特征方程残差\n环境缩放     网格收敛',5.55,2.55,3.85,1.35,17);
 tx(s,'10项测试通过',5.55,4.15,3.8,.5,24,C.green,true);
 tx(s,'线弹性、小变形、已知质量与理想夹持；损伤指刚度折减，非裂纹深度。',.65,4.88,8.7,.2,11,C.muted);
 note(s,'标准Euler–Bernoulli单元独立组装。解析频率和静挠度提供独立于学习器的核对；动画形状使用同一模型的特征向量与Hermite插值。');

 s=await base(5,'04  同输入、强基线、独立数据');
 [['3','独立模型种子'],['720','独立测试工况'],['2880','逐方法预测记录']].forEach((a,i)=>{let x=.65+i*3.08;tx(s,a[0],x,1.25,2.85,.62,36,C.green);tx(s,a[1],x,1.96,2.85,.3,15);});
 table(s,[['实验环节','设置与核验'],['训练与校准','每种子2400训练、120校准；不同随机流'],['测试范围','6域各40例/种子；常规、健康、噪声、网格、三损伤、附加质量'],['比较对象','纯AI；22候选穷举反演；忽略环境消融'],['独立复现','第二遍从数据生成开始重训，非计时结果全部一致']],.65,2.55,8.7,[1.8,6.9],13,.43);
 tx(s,'全部为合成模态特征，尚未经过原始传感器波形或实物验证。',.65,4.92,8.7,.22,11,C.ochre);
 note(s,'种子11/29/47，每域合并后120例。720个工况不能当作720次独立训练；训练、校准、测试没有共享同一随机流。');

 s=await base(6,'05  相近误差，减少在线搜索开销');
 const id=summary.id,methods=['hybrid','ai','exhaustive'],labels=['融合','纯AI','穷举'];
 const specs=[['全区MAE / 百分点',methods.map(k=>id[k].mae_pp),'0.000',1,.2],['在线中位耗时 / ms',methods.map(k=>id[k].median_ms),'0.0',100,20],['平均优化前向调用',['hybrid','exhaustive'].map(k=>id[k].mean_calls),'0.0',1000,200]];
 specs.forEach((a,i)=>{let x=.55+i*3.15;tx(s,a[0],x,1.25,3,.32,14,C.green,true);chart(s,pptx.ChartType.bar,[{name:a[0],labels:i===2?['融合','穷举']:labels,values:a[1]}],x,1.78,2.96,2.15,{barDir:'col',catAxisTitle:'方法',valAxisTitle:a[0],valAxisMaxVal:a[3],valAxisMajorUnit:a[4],dataLabelFormatCode:a[2],gapSizePct:95,chartColors:[C.green]});});
 const speed=id.exhaustive.median_ms/id.hybrid.median_ms,saving=100*(1-id.hybrid.mean_calls/id.exhaustive.mean_calls);
 tx(s,`${speed.toFixed(2)} 倍`,.65,4.03,2,.5,30,C.green);tx(s,'穷举 / 融合中位耗时',2.65,4.15,2.7,.3,13);
 tx(s,`${saving.toFixed(1)}%`,5.7,4.03,1.8,.5,30,C.green);tx(s,'前向调用减少',7.65,4.15,1.7,.3,13);
 tx(s,'常规域120例；计时含在线AI推理，不含离线训练。未声称精度显著优于穷举。',.65,4.9,8.7,.25,11,C.muted);
 note(s,'三个图都是原生PowerPoint图表，可以右键编辑数据。数据自动读取summary.json，不通过图片取数。融合与穷举误差接近，纯AI更快但误差较大。');

 s=await base(7,'06  误差区间与失配，都需要展示');
 const domains=['id','healthy','noise','mesh','triple','mass'],dn=['常规','健康','3倍噪声','网格','三损伤','附加质量'];
 tx(s,'全区损伤误差 / 百分点',.6,1.25,4.8,.3,15,C.green,true);
 chart(s,pptx.ChartType.line,['hybrid','ai','exhaustive','no_environment'].map((k,i)=>({name:['融合','纯AI','穷举','无环境'][i],labels:dn,values:domains.map(d=>summary[d][k].mae_pp)})),.5,1.8,5.2,2.65,{showValue:false,showLegend:true,legendPos:'b',legendFontFace:'Arial',legendFontSize:10,lineSize:1.7,showMarker:true,lineDataSymbol:'circle',lineDataSymbolSize:4,valAxisMaxVal:10,valAxisMajorUnit:2,catAxisLabelFontSize:9,catAxisTitle:'测试域',valAxisTitle:'MAE / 百分点'});
 tx(s,'融合方案的覆盖与接受率',5.92,1.25,3.5,.3,15,C.green,true);
 table(s,[['测试域','覆盖/%','接受/%'],...domains.map((d,i)=>[dn[i],(summary[d].hybrid.coverage*100).toFixed(1),(summary[d].hybrid.acceptance*100).toFixed(1)])],5.9,1.8,3.5,[1.5,1,1],11,.34);
 tx(s,`常规域名义90%同时区间，实测覆盖 ${(summary.id.hybrid.coverage*100).toFixed(1)}%。`,.65,4.46,8.7,.3,15,C.green,true);
 tx(s,'高噪声、三处损伤和附加质量各120例均触发复核；不代表任意未知异常均可检测。',.65,4.91,8.7,.25,11,C.ochre);
 note(s,'保留分布外失效，不用平均值掩盖错误。覆盖率是六区同时覆盖；门限接受不等于工程安全。折线图及右侧数据表均可编辑。');

 s=await base(8,'07  可视化对应同一组计算结果');
 const screen=path.join(ROOT,'paper/generated/demo_stage.png'),meta=await sharp(screen).metadata();
 const imageH=Math.min(3.48,5.8*meta.height/meta.width),imageW=imageH*meta.width/meta.height;
 s.addImage({path:screen,x:.55+(5.8-imageW)/2,y:1.4+(3.48-imageH)/2,w:imageW,h:imageH});
 tx(s,'现场演示顺序',6.65,1.5,2.8,.4,21,C.green,true);
 ['常规域：检查损伤与真值','健康梁：分离环境因子','附加质量：显示复核提示','查看逐分区区间和记录'].forEach((a,i)=>{tx(s,String(i+1).padStart(2,'0'),6.65,2.2+i*.65,.4,.35,14,C.ochre);tx(s,a,7.13,2.18+i*.65,2.27,.48,14);});
 tx(s,'有限元Hermite插值；动画振幅放大、时间放慢，仅用于形态解释。',.65,4.93,8.7,.2,11,C.muted);
 note(s,'本页左侧是唯一的演示截图，可在PowerPoint里替换图片；旁边的标题、步骤及说明保持可编辑。真实仿真标签只用于展示和评分，不进入反演。');

 s=await base(9,'08  应用价值与下一步验证');
 tx(s,'当前可用',.65,1.42,4,.5,25,C.green,true);tx(s,'下一步实物试验',5.4,1.42,4,.5,25,C.green,true);
 line(s,4.95,1.42,0,2.85);
 ['教学演示\n模态、损伤和环境混淆','算法研究\n强基线与失配测试','本地复算\n模型、数据和逐例记录'].forEach((a,i)=>tx(s,a,.65,2.12+i*.8,4,.62,17));
 ['核验健康梁参数、夹持与模态','记录温度、质量及重复测量','冻结校准，预留独立损伤工况'].forEach((a,i)=>tx(s,a,5.4,2.17+i*.83,3.9,.64,18));
 tx(s,'当前为仿真研究原型，尚无实物验证或工程安全鉴定结论。',.65,4.87,8.7,.3,14,C.ochre);
 note(s,'真正需要补强的是实物健康模型核验和独立损伤工况。不要将附加质量当作已知刚度损伤标签，也不要把计划写成已完成试验。');

 s=await base(10,'',true);
 tx(s,'梁鉴 / BEAM INSIGHT',.65,.6,8,.3,13,C.mint);
 tx(s,'从一个预测，\n到一条可复核的证据链。',.65,1.4,8.7,1.65,34,C.paper);
 tx(s,'稀疏损伤假设 → AI候选 → 力学反演 → 独立校核',.65,3.35,8.7,.4,18,C.mint);
 tx(s,'源码、模型、逐例记录、反例与复现命令完整保留。',.65,4.12,8.7,.35,16,C.paper);
 tx(s,'Peeters et al. (2001)；Angelopoulos & Bates (2021)。\n团队人工审核待完成；AI辅助范围见 docs/AI_USE.md。',.65,4.68,8.7,.4,10,C.mint);
 note(s,'参考：doi.org/10.1088/0964-1726/10/3/314；arxiv.org/abs/2107.07511。AI辅助代码、实验与初稿，团队仍需人工复核。');
 await pptx.writeFile({fileName:path.join(OUT,'答辩演示_可编辑版.pptx')});
 console.log('Wrote 10 editable slides, 4 native charts, 2 native tables, 1 replaceable screenshot.');
}
main().catch(e=>{console.error(e);process.exit(1)});
