"""Align each browser recording using its visible sync marker, then mux narration."""
from pathlib import Path
import json,subprocess,hashlib,math
ROOT=Path(__file__).resolve().parents[1];W=ROOT/'work/video';OUT=ROOT/'output/video'
timeline=json.loads((W/'timeline.json').read_text());OUT.mkdir(parents=True,exist_ok=True)
def run(args,**kwargs):return subprocess.run(args,check=True,**kwargs)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
segments=[];alignment=[]
for scene in timeline['scenes']:
    raw=W/'raw'/(scene['id']+'.webm')
    assert raw.exists(),raw
    info=probe(raw);v=next(s for s in info['streams'] if s['codec_type']=='video');assert (v['width'],v['height'])==(1920,1080)
    rgb=subprocess.check_output(['ffmpeg','-v','error','-i',str(raw),'-vf','crop=16:16:0:0,scale=1:1,format=rgb24','-fps_mode','passthrough','-f','rawvideo','-'])
    timestamps=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(raw)]))['frames']
    assert len(rgb)==len(timestamps)*3,(len(rgb),len(timestamps))
    markers=[rgb[i]>200 and rgb[i+1]<60 and rgb[i+2]>200 for i in range(0,len(rgb),3)]
    first=next(i for i,value in enumerate(markers) if value)
    assert all(markers[first:first+10])
    offset=float(timestamps[first]['best_effort_timestamp_time']);duration=scene['duration'];part=W/(scene['id']+'.mp4')
    run(['ffmpeg','-y','-v','error','-ss',str(offset),'-i',str(raw),'-i',str(ROOT/scene['audio']),'-t',str(duration),'-vf','drawbox=x=0:y=0:w=16:h=16:color=0x102026:t=fill,fps=30','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(part)])
    pi=probe(part);audio=next(s for s in pi['streams'] if s['codec_type']=='audio');video=next(s for s in pi['streams'] if s['codec_type']=='video')
    assert abs(float(audio['duration'])-duration)<.05
    assert abs(float(video['duration'])-duration)<.08
    segments.append(part);alignment.append(dict(scene=scene['id'],sync_frame=first,trim_seconds=offset,voice_seconds=duration,video_seconds=float(video['duration']),max_sync_quantization_seconds=.04))
    print('Encoded',scene['id'],'trim',round(offset,3),'duration',round(duration,3),flush=True)
concat=W/'concat.txt';concat.write_text('\n'.join("file '"+p.name+"'" for p in segments)+'\n')
name='AIC-2026-34636761-开放式赛题-梁鉴-演示视频';final=OUT/(name+'.mp4')
run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(final)])
def clock(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
subtitles=[];i=1;position=0;chapters=[]
for scene,seg in zip(timeline['scenes'],segments):
    chapters.append(dict(id=scene['id'],start=round(position,3),title=scene['chapter']))
    for cap in scene['captions']:
        subtitles.append(f"{i}\n{clock(position+cap['start'])} --> {clock(position+cap['end'])}\n{cap['text']}\n");i+=1
    position+=float(probe(seg)['format']['duration'])
(OUT/(name+'.srt')).write_text('\n'.join(subtitles))
(OUT/'配音稿.md').write_text('# 梁鉴演示视频配音稿\n\n团队编号：AIC-2026-34636761。配音为macOS Tingting本地合成语音，画面已标注。\n\n'+'\n\n'.join('## '+s['chapter']+'\n\n'+'\n\n'.join(s['lines']) for s in timeline['scenes'])+'\n')
meta=probe(final);duration=float(meta['format']['duration']);assert 180<=duration<=300;assert final.stat().st_size<=300_000_000
assert [s['codec_name'] for s in meta['streams']]==['h264','aac']
(W/'encoding.json').write_text(json.dumps(dict(video=str(final),duration=duration,bytes=final.stat().st_size,sha256=hashlib.sha256(final.read_bytes()).hexdigest(),alignment=alignment,chapters=chapters,metadata=meta),ensure_ascii=False,indent=2))
print('Final:',duration,'seconds;',final.stat().st_size,'bytes',flush=True)
