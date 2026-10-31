"""Check final MP4 end to end; require explicit visual-review flag for acceptance."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];W=ROOT/'work/video';OUT=ROOT/'output/video'
parser=argparse.ArgumentParser();parser.add_argument('--visual-reviewed',action='store_true');args=parser.parse_args()
encoding=json.loads((W/'encoding.json').read_text());video=Path(encoding['video']);timeline=json.loads((W/'timeline.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ff(args):return subprocess.run(['ffmpeg','-hide_banner','-nostats']+args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]));vs=next(s for s in meta['streams'] if s['codec_type']=='video');au=next(s for s in meta['streams'] if s['codec_type']=='audio');duration=float(meta['format']['duration'])
checks={}
checks['format_and_limits']=180<=duration<=300 and video.stat().st_size<=300_000_000 and vs['codec_name']=='h264' and au['codec_name']=='aac' and (vs['width'],vs['height'])==(1920,1080) and vs['r_frame_rate']=='30/1' and vs['pix_fmt']=='yuv420p'
checks['audio_video_duration_agree']=abs(float(vs['duration'])-float(au['duration']))<.12
decode=ff(['-v','error','-i',str(video),'-f','null','-']);checks['full_decode']=not decode.stderr.strip()
dark=ff(['-i',str(video),'-vf','blackdetect=d=0.12:pix_th=0.04:pic_th=0.98','-an','-f','null','-']);(W/'black-check.log').write_bytes(dark.stderr);checks['no_black_segments']='black_start:' not in dark.stderr.decode()
silence=ff(['-i',str(video),'-af','silencedetect=noise=-40dB:d=0.9,volumedetect','-vn','-f','null','-']);audio_log=silence.stderr.decode();(W/'audio-check.log').write_text(audio_log)
silent=[float(x) for x in re.findall(r'silence_duration: ([\d.]+)',audio_log)];peak=float(re.search(r'max_volume: ([-\d.]+) dB',audio_log)[1]);checks['no_long_silence_or_clipping']=(max(silent,default=0)<2.6 and peak<=-.3)
gray=ff(['-v','error','-i',str(video),'-vf','scale=1:1,format=gray','-fps_mode','passthrough','-f','rawvideo','-']).stdout;checks['no_blank_white_or_black_frames']=bool(gray) and min(gray)>8 and max(gray)<220
corner=ff(['-v','error','-i',str(video),'-vf','crop=16:16:0:0,scale=1:1,format=rgb24','-fps_mode','passthrough','-f','rawvideo','-']).stdout;checks['sync_marker_removed']=not any(corner[i]>200 and corner[i+1]<60 and corner[i+2]>200 for i in range(0,len(corner),3))
checks['sync_alignment']=all(a['max_sync_quantization_seconds']<=.04 and abs(a['video_seconds']-a['voice_seconds'])<.08 for a in encoding['alignment'])
checks['browser_recording_passed']=json.loads((W/'recording-check.json').read_text())['passed']
for name,expected in [('regular',True),('healthy',True),('mass',False)]:
    case=json.loads((W/'cases'/(name+'.json')).read_text());checks[name+'_actual_case']=case['accepted']==expected and case['seed']==12345
checks['demo_values_match_narration']=round(json.loads((W/'cases/regular.json').read_text())['result']['hold_rms'],2)==1.22 and round(json.loads((W/'cases/healthy.json').read_text())['result']['scale'],3)==.955 and round(json.loads((W/'cases/mass.json').read_text())['result']['hold_rms'],2)==24.74
summary=json.loads((ROOT/'results/run1/summary.json').read_text());checks['reported_metrics']=round(summary['id']['hybrid']['mae_pp'],3)==.135 and round(summary['id']['hybrid']['coverage']*100,1)==87.5
srt=video.with_suffix('.srt');checks['subtitle_count']=len(re.findall(r' --> ',srt.read_text()))==sum(len(s['captions']) for s in timeline['scenes'])
assert all(checks.values()),checks
# Sample every narrated sentence and both sides of each cut.
sample_times=set();position=0
for scene in timeline['scenes']:
    for cap in scene['captions']:sample_times.add(round(position+(cap['start']+cap['end'])/2,3))
    sample_times.add(round(position+.08,3));sample_times.add(round(position+scene['duration']-.1,3));position+=scene['duration']
frames=W/'frames/final';frames.mkdir(parents=True,exist_ok=True)
if not args.visual_reviewed:
    for i,t in enumerate(sorted(sample_times)):
        ff(['-y','-v','error','-ss',str(min(t,duration-.1)),'-i',str(video),'-frames:v','1','-vf','scale=960:540',str(frames/f'{i:02}-{t:.3f}.png')])
assert len(list(frames.glob('*.png')))>=len(sample_times)
sources=[video,srt,OUT/'配音稿.md',ROOT/'video/storyboard.json',ROOT/'video/index.html',ROOT/'video/video.css',ROOT/'video/video.js',W/'timeline.json',W/'encoding.json',W/'recording-check.json']
result=dict(status='verified_locally' if args.visual_reviewed else 'checks_passed_pending_visual_review',date='2026-10-22',video=str(video),sha256=sha(video),duration_seconds=duration,bytes=video.stat().st_size,resolution=[1920,1080],frame_rate=30,codecs=['h264','aac'],checks=checks,decoded_frame_count=len(gray),audio_peak_db=peak,longest_detected_silence_seconds=max(silent,default=0),alignment_quantization_seconds=.04,visual_review=dict(completed=args.visual_reviewed,sampled_frames=len(sample_times),scope='All sampled sentence midpoints and cut boundaries; selected full-resolution demo and metric frames.'),synthetic_voice='macOS Tingting, disclosed on screen',actual_demo_domains=['id','healthy','mass'],sources={str(p.relative_to(ROOT)):sha(p) for p in sources},uploaded=False)
(ROOT/'results/video_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:result[k] for k in ['status','duration_seconds','bytes','checks','decoded_frame_count','audio_peak_db','longest_detected_silence_seconds']},ensure_ascii=False,indent=2))
