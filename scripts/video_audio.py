"""Create disclosed local Chinese narration and exact caption timings."""
from pathlib import Path
import json,subprocess,wave,contextlib
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/'work/video/audio';W.mkdir(parents=True,exist_ok=True)
story=json.loads((ROOT/'video/storyboard.json').read_text())
def run(args):subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
def probe(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],text=True).strip())
timeline=[];total=0
for i,s in enumerate(story['scenes']):
    captions=[];parts=[];time=0.7
    for j,line in enumerate(s['lines']):
        name=f'{i:02}-{j:02}';txt=W/(name+'.txt');txt.write_text(line)
        aiff=W/(name+'.aiff');wav=W/(name+'.wav')
        if not aiff.exists():run(['say','-v',story['voice'],'-r',str(story['rate']),'-f',str(txt),'-o',str(aiff)])
        run(['ffmpeg','-y','-v','error','-i',str(aiff),'-ar','48000','-ac','1',str(wav)])
        d=probe(wav);captions.append(dict(start=round(time,3),end=round(time+d,3),text=line));parts.append(wav);time+=d+0.25
    out=W/(s['id']+'.wav')
    with wave.open(str(out),'wb') as target:
        target.setnchannels(1);target.setsampwidth(2);target.setframerate(48000);target.writeframes(b'\0'*int(.7*48000)*2)
        for p in parts:
            with wave.open(str(p),'rb') as f:target.writeframes(f.readframes(f.getnframes()))
            target.writeframes(b'\0'*int(.25*48000)*2)
        target.writeframes(b'\0'*int(.6*48000)*2)
    duration=probe(out);timeline.append(dict(**s,start=round(total,3),duration=duration,captions=captions,audio=str(out.relative_to(ROOT))))
    total+=duration;print(s['id'],round(duration,2),'seconds',flush=True)
(ROOT/'work/video/timeline.json').write_text(json.dumps(dict(voice='macOS Tingting local synthetic voice',total_duration=total,scenes=timeline),ensure_ascii=False,indent=2))
print('Total duration:',total,flush=True)
