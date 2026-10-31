// Actual browser recording; subtitles use the synthesized sentence timings.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'..'),W=path.join(ROOT,'work/video');
const timeline=JSON.parse(fs.readFileSync(path.join(W,'timeline.json')));
const demoStyle=`header,.heading,.study-strip,footer,details,.spec,.side-note{display:none!important}main{max-width:none!important;padding:0!important}.lab{grid-template-columns:220px minmax(0,1fr)}.setup{padding:14px 22px 10px 16px}.setup label{margin-top:14px}.setup .section-label{font-size:15px}.stage{height:210px}.instrument-top{padding:12px 20px}.section-label{font-size:15px}.badge{font-size:13px}.readouts{padding:10px 22px;gap:25px}.readouts strong{font-size:28px;margin:2px 0}.readouts span{font-size:13px}.readouts small{font-size:12px}.view-controls{padding:4px 20px}.view-controls select,.view-controls button{font-size:13px}.lower{padding:13px 16px;gap:35px}.lower svg{height:153px;margin-top:10px}.legend{font-size:13px}.audit h2{font-size:22px;margin:13px 0}.audit p{font-size:15px;line-height:1.6;margin:10px 0}.audit p.fine{font-size:12px;margin:10px 0}.audit-rule{font-size:13px;padding:4px 0}.action-glow{outline:3px solid #e5aa70!important;outline-offset:3px}select,input{font-size:15px}.primary{font-size:15px;margin-top:15px;padding:10px}.stage-caption b{font-size:25px}`;
async function prepare(page,i){
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 if(timeline.scenes[i].domain){let ready=false;const end=Date.now()+180000;while(Date.now()<end){try{const r=await fetch('http://127.0.0.1:18766/api/evidence',{signal:AbortSignal.timeout(1000)});if(r.ok){ready=true;break}}catch{}await new Promise(r=>setTimeout(r,3000))}if(!ready)throw Error('Local inference service did not become ready');}
 await page.goto(`http://127.0.0.1:18767/video/index.html?scene=${i}`);
 await page.waitForFunction(()=>window.ready===true);let frame;
 if(timeline.scenes[i].domain){
   await page.locator('iframe').evaluate(el=>el.style.pointerEvents='auto');
   frame=await (await page.locator('iframe').elementHandle()).contentFrame();await frame.waitForURL(/:18766/);await frame.waitForFunction(()=>typeof data!=='undefined'&&data);
   await frame.addStyleTag({content:demoStyle});
 }
 await page.evaluate(()=>document.fonts.ready);return {frame,errors};
}
async function glow(frame,id,on){await frame.locator(id).evaluate((el,b)=>el.classList.toggle('action-glow',b),on);}
async function main(){
 fs.mkdirSync(path.join(W,'cases'),{recursive:true});const browser=await chromium.launch({headless:true,channel:'chrome'});
 const preview=process.argv.includes('--preview');const selection=process.argv.find(a=>a.startsWith('--scenes='));const selected=selection?selection.split('=')[1].split(',').map(Number):timeline.scenes.map((_,i)=>i);
 for(let i=0;i<timeline.scenes.length;i++){
  if(!selected.includes(i))continue;
  const s=timeline.scenes[i];const context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1,...(!preview?{recordVideo:{dir:path.join(W,'raw'),size:{width:1920,height:1080}}}:{})});
  const page=await context.newPage();const {frame,errors}=await prepare(page,i);
  if(preview){await page.evaluate(()=>window.startMovie());await page.waitForTimeout(1800);if(frame){await frame.selectOption('#domain',s.domain);await frame.fill('#seed','12345');const response=page.waitForResponse(r=>r.url().endsWith('/api/diagnose')&&r.request().method()==='POST');await frame.locator('#run').click();await response;await frame.waitForFunction(d=>data.domain===d,s.domain)}await page.screenshot({path:path.join(W,'frames',`preview-${i}.png`)});await context.close();continue;}
  const video=page.video();await page.evaluate(()=>window.startMovie());const begun=Date.now();
  const actions=[];
  if(frame){actions.push([1.2,async()=>{await glow(frame,'#domain',true);await frame.selectOption('#domain',s.domain);await frame.fill('#seed','12345');await glow(frame,'#run',true);const response=page.waitForResponse(r=>r.url().endsWith('/api/diagnose')&&r.request().method()==='POST');await frame.locator('#run').click();const r=await response;const body=await r.json();if(!r.ok()||body.domain!==s.domain)throw Error('diagnosis failed');fs.writeFileSync(path.join(W,'cases',s.id+'.json'),JSON.stringify(body,null,2));}]);actions.push([4.5,async()=>{await glow(frame,'#domain',false);await glow(frame,'#run',false)}]);
   if(s.id==='regular'){const t=s.captions[2].start;actions.push([t,async()=>{await glow(frame,'#mode',true);await frame.selectOption('#mode','2')}]);actions.push([t+2.5,async()=>{const b=await frame.locator('#beam').boundingBox();await page.mouse.move(b.x+b.width*.6,b.y+b.height*.55);await page.mouse.down();await page.mouse.move(b.x+b.width*.7,b.y+b.height*.65,{steps:30});await page.mouse.up();}]);actions.push([t+5,async()=>{await frame.selectOption('#mode','4');await glow(frame,'#mode',false)}]);}
  }
  for(const [at,action] of actions.sort((a,b)=>a[0]-b[0])){const delay=at*1000-(Date.now()-begun);if(delay>0)await page.waitForTimeout(delay);await action();}
  const remain=s.duration*1000+200-(Date.now()-begun);if(remain>0)await page.waitForTimeout(remain);
  if(errors.length)throw Error(errors.join(';'));
  await context.close();await video.saveAs(path.join(W,'raw',s.id+'.webm'));
  console.log(`Recorded ${i+1}/8: ${s.id} (${s.duration.toFixed(2)}s) with sync marker`,true);
 }
 await browser.close();const completed=timeline.scenes.filter(s=>fs.existsSync(path.join(W,'raw',s.id+'.webm'))).map(s=>s.id);fs.writeFileSync(path.join(W,preview?'preview-check.json':'recording-check.json'),JSON.stringify({date:'2026-10-22',completed,actual_demo_domains:['id','healthy','mass'],errors:[],passed:preview||completed.length===8},null,2));
}
main().catch(e=>{console.error(e);process.exit(1)});
