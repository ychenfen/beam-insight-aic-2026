// Capture actual local demo responses and screenshots for internal evidence.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'output/evidence');
fs.mkdirSync(path.join(out,'assets'),{recursive:true});fs.mkdirSync(path.join(out,'records'),{recursive:true});
(async()=>{
 const readyUntil=Date.now()+120000;let ready=false;
 while(Date.now()<readyUntil){
   try {const r=await fetch('http://127.0.0.1:18766/api/evidence',{signal:AbortSignal.timeout(1000)});if(r.ok){ready=true;break;}} catch {}
   await new Promise(resolve=>setTimeout(resolve,3000));
 }
 if(!ready)throw Error('Local demo was not ready within 120 seconds');
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:1120},deviceScaleFactor:1});const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:18766');await page.waitForFunction(()=>document.querySelector('#scale').textContent!=='—');
 await page.evaluate(()=>{paused=true;window.__freezeViz=true});
 for(const domain of ['id','healthy','mass']){
   await page.selectOption('#domain',domain);await page.fill('#seed','12345');
   const result=page.waitForResponse(r=>r.url().endsWith('/api/diagnose')&&r.request().method()==='POST');
   await page.click('#run');const response=await result;const body=await response.json();
   if(!response.ok()||body.domain!==domain||body.seed!==12345)throw Error('response mismatch');
   await page.waitForFunction(d=>data&&data.domain===d,domain);
   await page.selectOption('#mode','2');await page.evaluate(()=>{phase=Math.PI/2;draw(performance.now())});
   await page.locator('.instrument').screenshot({path:path.join(out,'assets',domain+'-instrument.png')});
   await page.locator('.lower').screenshot({path:path.join(out,'assets',domain+'-result.png')});
   fs.writeFileSync(path.join(out,'records',domain+'-response.json'),JSON.stringify(body,null,2));
 }
 if(errors.length)throw Error(errors.join('\n'));
 fs.writeFileSync(path.join(out,'records/browser-check.json'),JSON.stringify({date:'2026-10-22',domains:['id','healthy','mass'],observation_seed:12345,model_seed:11,errors,screenshot_source:'actual local browser rendering; animation paused at third mode',passed:true},null,2));
 await browser.close();console.log('Captured three cases and six screenshots; JSON responses saved.');
})().catch(e=>{console.error(e);process.exit(1)});
