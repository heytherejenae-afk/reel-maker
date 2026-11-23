#!/usr/bin/env python3
"""Script mode: make a reel from the person's own script, talking-head clip, b-roll clips
and overlay pages (e.g. Canva PNGs), following the script beat by beat. Everything about
the edit lives in one editable file, reel.json, so any part can be changed and re-made.

  script_reel.py transcribe reel.json        words.json (word timings of the talking head)
  script_reel.py sheets reel.json            contact sheets with timestamps (talk + each b-roll) to choose shots
  script_reel.py build reel.json             cut by beat + polish + layers -> reel['out']
  script_reel.py editor reel.json            editable page (reel['out']/editor.html) to publish as an Artifact
  script_reel.py apply reel.json CHANGES     apply a pasted 'REEL CHANGES' block (file path), then build again

reel.json (paths relative to "work" unless absolute):
{
 "name": "Apple trees in pots", "work": "/tmp/work/apple", "out": "/mnt/project-files/reels/apples",
 "talk": "clips/talk.mp4",
 "broll": {"b1": "clips/b1.mp4", "b2": "clips/b2.mp4"},          # short names the page shows
 "overlays": ["ov/p1.png", "ov/p2.png"],                          # 1080x1920 transparent pages, numbered from 1
 "brand": {"text": "#FFFFFF", "key": "#E8875A", "card": "#F6EFDF", "card_label": "#2F4A35", "note": "#FFFFFF"},
 "fonts": {"word": "<skill>/fonts/InterDisplay-SemiBold.ttf", "key": "<skill>/fonts/DMSerifDisplay-Italic.ttf",
           "hand": "<skill>/fonts/CaveatBrush-Regular.ttf"},
 "captions": {"size": 122, "key_size": 146, "y": 0.5},            # one word at a time; y = 0..1 down the screen
 "overlay_place": {"scale": 0.85, "y": 0.735},                    # overlays sit below the face, in front
 "key_words": ["apples", "dwarf"], "fixes": {"500ml": "50L"},     # fixes = caption spelling corrections
 "title": {"beat": 0, "lines": [["growing apples", "word", 104, "#FFFFFF", 175], ["in pots", "key", 170, "key", 330]]},
 "beats": [
   {"name": "Hook", "say": [7.30, 11.68], "overlay": 1, "overlay_at": 0.0,
    "shots": [{"show": "talk", "dur": 4.38}]},
   {"name": "Tip 1", "say": [47.56, 54.44], "overlay": 4, "overlay_at": 0.2, "backing": null,
    "shots": [{"show": "talk", "dur": 1.6}, {"show": "b1", "at": 365.8, "dur": 2.0, "speed": 1},
              {"show": "b3", "at": 18.0, "dur": 3.28, "speed": 2}]}
 ]
}
"say" = the seconds of the talking-head clip to keep for that beat (its sound plays throughout).
"shots" = what is on screen during it, in order; their "dur" must add up to the beat's length
(the last shot's dur is adjusted automatically). "talk" shots show the talking head in sync.
"at" = where in the b-roll clip to start; "speed" 2 = sped up 2x (good for long planting footage).
Title "lines": [text, "word"|"key" font, size px, colour (hex or "key"), y px]. Title sits behind the person.
layers-for-edits/ (Instagram Edits has no colour key, tested 2026-11-23): 1-video-with-captions.mp4
(video + title + captions) and one full-screen see-through PNG per overlay card, named with its times.
Set "edits": false to skip it.
Rules learnt: never reuse the same b-roll moment twice; put overlays in front, below the face.
"""
import base64, html, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
W, H, FPS = 1080, 1920, 30
VF = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p,setsar=1'


def load(p):
    r = json.load(open(p)); r['_path'] = os.path.abspath(p)
    return r


def P(r, p):
    return p if os.path.isabs(p) else os.path.join(r['work'], p)


def run(*a):
    subprocess.run(list(a), check=True)


def transcribe(r):
    import numpy as np, wave
    from faster_whisper import WhisperModel
    wav = P(r, 'talk.wav')
    run('ffmpeg', '-v', 'error', '-y', '-i', P(r, r['talk']), '-ac', '1', '-ar', '16000', wav)
    w = wave.open(wav); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    segs, _ = WhisperModel('medium.en', compute_type='int8').transcribe(a, word_timestamps=True)
    words = []
    for s in segs:
        print(f'{s.start:7.2f}-{s.end:7.2f} {s.text}')
        words += [dict(w=t.word.strip(), s=round(t.start, 2), e=round(t.end, 2)) for t in s.words]
    json.dump(words, open(P(r, 'words.json'), 'w'))


def sheets(r):
    srcs = {'talk': r['talk'], **r['broll']}
    for name, p in srcs.items():
        d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', P(r, p)]))
        step = max(2, round(d / 48))
        out = P(r, f'sheet_{name}.jpg')
        subprocess.run(f"ffmpeg -v error -y -i '{P(r, p)}' -vf \"fps=1/{step},scale=-1:220,drawtext=text='%{{pts\\:hms}}':x=5:y=5:fontcolor=yellow:fontsize=20:box=1:boxcolor=black\" -f image2pipe -vcodec png - | ffmpeg -v error -y -f image2pipe -i - -vf tile=8x6 '{out}'", shell=True, check=True)
        print(out, f'(one picture every {step}s)')


def fix_durs(b):
    d = b['say'][1] - b['say'][0]
    s = sum(x['dur'] for x in b['shots'][:-1])
    b['shots'][-1]['dur'] = round(d - s, 3)
    assert b['shots'][-1]['dur'] > 0.2, f"beat {b['name']}: shots longer than the words"


def cut(r):
    parts = P(r, 'parts'); os.makedirs(parts, exist_ok=True)
    talk = P(r, r['talk']); vs, as_, edl, talk_on, ovs = [], [], [], [], []
    o = 0.0; k = 0
    for bi, b in enumerate(r['beats']):
        fix_durs(b)
        a0, a1 = b['say']; d = a1 - a0
        aw = f'{parts}/a{bi:03d}.wav'
        run('ffmpeg', '-v', 'error', '-y', '-ss', str(a0), '-i', talk, '-t', f'{d:.3f}', '-vn', '-ac', '2', '-ar', '48000',
            '-af', f'afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015', aw)
        as_.append(aw); edl.append(dict(src=a0, out=o, dur=d))
        rel = 0.0
        for sh in b['shots']:
            v = f'{parts}/v{k:03d}.mp4'; k += 1
            if sh['show'] == 'talk':
                run('ffmpeg', '-v', 'error', '-y', '-ss', f'{a0 + rel:.3f}', '-i', talk, '-t', f"{sh['dur']:.3f}", '-vf', VF, '-an',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', v)
                talk_on.append([o + rel, o + rel + sh['dur']])
            else:
                sp = sh.get('speed', 1)
                run('ffmpeg', '-v', 'error', '-y', '-ss', str(sh['at']), '-i', P(r, r['broll'][sh['show']]), '-t', f"{sh['dur'] * sp:.3f}",
                    '-vf', f'setpts=PTS/{sp},{VF}', '-an', '-frames:v', str(round(sh['dur'] * FPS)),
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', v)
            vs.append(v); rel += sh['dur']
        if b.get('overlay'):
            ovs.append(dict(png=P(r, r['overlays'][b['overlay'] - 1]), start=o + b.get('overlay_at', 0.2), end=o + d,
                            scale=r['overlay_place']['scale'], y=r['overlay_place']['y'], backing=b.get('backing')))
        o += d
    open(f'{parts}/v.txt', 'w').write(''.join(f"file '{p}'\n" for p in vs))
    open(f'{parts}/a.txt', 'w').write(''.join(f"file '{p}'\n" for p in as_))
    run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{parts}/v.txt', '-c', 'copy', P(r, 'v.mp4'))
    run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{parts}/a.txt', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', P(r, 'a.wav'))
    run('ffmpeg', '-v', 'error', '-y', '-i', P(r, 'v.mp4'), '-i', P(r, 'a.wav'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P(r, 'base.mp4'))
    return edl, talk_on, ovs, o


def build(r):
    edl, talk_on, ovs, total = cut(r)
    words = json.load(open(P(r, 'words.json'))); out = []
    for w in words:
        for p in edl:
            if p['src'] - 0.05 <= w['s'] < p['src'] + p['dur']:
                d = p['out'] - p['src']
                out.append(dict(w=w['w'], s=round(w['s'] + d, 3), e=round(min(w['e'], p['src'] + p['dur']) + d, 3))); break
    merged = []
    for w in out:  # "$1" ".40" and "q" "-tip" belong together
        if merged and (w['w'].startswith('.') or w['w'].startswith('-')): merged[-1] = dict(merged[-1], w=merged[-1]['w'] + w['w'], e=w['e'])
        else: merged.append(w)
    json.dump(merged, open(P(r, 'words_out.json'), 'w'))
    titles = []
    t = r.get('title')
    if t and t.get('lines'):
        b0 = edl[t.get('beat', 0)]
        titles.append(dict(start=b0['out'] + 0.05, end=b0['out'] + b0['dur'], behind=True,
                           lines=[[l[0], l[1], l[2], r['brand']['key'] if l[3] == 'key' else l[3], l[4]] for l in t['lines']]))
    plan = dict(brand=r['brand'], fonts=r['fonts'], words=P(r, 'words_out.json'), seg_model=f'{SKILL}/models/selfie_segmenter.tflite',
                key_words=[k.lower() for k in r['key_words']], fixes=r.get('fixes', {}), captions=r['captions'],
                talk_ranges=talk_on, titles=titles, cards=r.get('cards', []), notes=r.get('notes', []), pngs=ovs)
    json.dump(plan, open(P(r, 'polish-plan.json'), 'w'), indent=1)
    lay = P(r, 'render'); os.makedirs(lay, exist_ok=True)
    run(sys.executable, f'{HERE}/polish.py', P(r, 'polish-plan.json'), P(r, 'base.mp4'), lay)
    out_dir = r['out']; os.makedirs(f'{out_dir}/layers-for-phone', exist_ok=True); os.makedirs(f'{out_dir}/layers-for-computer', exist_ok=True)
    slug = r['name'].lower().replace(' ', '-')
    run('ffmpeg', '-v', 'error', '-y', '-i', f'{lay}/final.mp4', '-c:v', 'libx264', '-crf', '21', '-preset', 'slow', '-c:a', 'copy', '-movflags', '+faststart', f'{out_dir}/{slug}.mp4')
    for d_ in ('layers-for-phone', 'layers-for-computer'):
        run('cp', P(r, 'base.mp4'), f'{out_dir}/{d_}/1-video.mp4')
    for n in ('2-title-behind-you', '3-captions', '4-overlays'):
        if not os.path.exists(f'{lay}/{n}.mov'): continue
        run('cp', f'{lay}/{n}.mov', f'{out_dir}/layers-for-computer/')
        # pink colour screen for CapCut on a phone (Chroma key); magenta because cards/b-roll are green
        run('ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=0xFF00FF:s={W}x{H}:r={FPS}', '-i', f'{lay}/{n}.mov', '-filter_complex',
            "[1:v]format=yuva444p,lut=a='if(gt(val,150),255,0)'[o];[0][o]overlay=shortest=1,format=yuv420p",
            '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', f'{out_dir}/layers-for-phone/{n}-pink.mp4')
    if r.get('edits', True):
        edits_pack(r, ovs, lay, out_dir)
    # small preview for the editor page
    run('ffmpeg', '-v', 'error', '-y', '-i', f'{lay}/final.mp4', '-vf', 'scale=360:-2', '-c:v', 'libx264', '-crf', '30', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', P(r, 'preview.mp4'))
    print('reel:', f'{out_dir}/{slug}.mp4', f'{total:.1f}s')


def mmss(t):
    return f'{int(t // 60)}m{int(t % 60):02d}s'


def edits_pack(r, ovs, lay, out_dir):
    """Instagram Edits can't remove a colour screen and Android can't play see-through video,
    so Edits gets the video with title + captions already on it, plus each overlay card as a
    full-screen see-through PNG, placed exactly where it sits in the reel."""
    from PIL import Image, ImageDraw
    d_ = f'{out_dir}/layers-for-edits'; os.makedirs(d_, exist_ok=True)
    ins, fc, last = ['-i', P(r, 'base.mp4')], '', '0:v'
    for i, n in enumerate(('2-title-behind-you', '3-captions')):
        if os.path.exists(f'{lay}/{n}.mov'):
            ins += ['-i', f'{lay}/{n}.mov']; k = len(ins) // 2 - 1
            fc += f'[{last}][{k}:v]overlay=eof_action=pass[v{i}];'; last = f'v{i}'
    args = ['ffmpeg', '-v', 'error', '-y', *ins]
    if fc: args += ['-filter_complex', fc.rstrip(';').rsplit('[', 1)[0] + '[out]', '-map', '[out]']
    else: args += ['-map', '0:v']
    run(*args, '-map', '0:a?', '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
        '-movflags', '+faststart', f'{d_}/1-video-with-captions.mp4')
    lines = []
    for i, o in enumerate(ovs):
        im = Image.open(o['png']).convert('RGBA'); bb = im.getbbox(); cx = (bb[0] + bb[2]) / 2; im = im.crop(bb)
        if o.get('backing'):
            pad = 36; bg = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
            h = o['backing'].lstrip('#'); ImageDraw.Draw(bg).rounded_rectangle((0, 0, bg.width - 1, bg.height - 1), 40,
                fill=tuple(int(h[j:j + 2], 16) for j in (0, 2, 4)) + (235,))
            bg.alpha_composite(im, (pad, pad)); im = bg
        sc = o.get('scale', 1); im = im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.LANCZOS)
        page = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y = o.get('y', .5) * H
        page.alpha_composite(im, (int(cx - im.width / 2), int(y - im.height / 2)))
        name = f'card-{i + 1}-from-{mmss(o["start"])}-to-{mmss(o["end"])}.png'
        page.save(f'{d_}/{name}'); lines.append(f'Card {i + 1}: from {mmss(o["start"])} to {mmss(o["end"])}  ({name})')
    open(f'{d_}/card-times.txt', 'w').write('\n'.join(lines) + '\n')


def editor(r):
    """One card per beat: the words, tap words to make them key words, fix a caption word,
    the overlay page, and each shot with a tap-to-pick strip of b-roll pictures."""
    tmp = P(r, 'thumbs'); os.makedirs(tmp, exist_ok=True)
    def img(p): return 'data:image/jpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    strips = {}
    for name, p in r['broll'].items():
        d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', P(r, p)]))
        step = 3 if d < 240 else 4
        run('ffmpeg', '-v', 'error', '-y', '-i', P(r, p), '-vf', f'fps=1/{step},scale=96:-2', '-q:v', '7', f'{tmp}/{name}_%04d.jpg')
        strips[name] = [dict(t=i * step, src=img(f'{tmp}/{name}_{i + 1:04d}.jpg')) for i in range(len([f for f in os.listdir(tmp) if f.startswith(name + '_')]))]
    run('ffmpeg', '-v', 'error', '-y', '-ss', '2', '-i', P(r, r['talk']), '-frames:v', '1', '-vf', 'scale=96:-2', f'{tmp}/talk.jpg')
    ovs = []
    for i, p in enumerate(r['overlays']):
        from PIL import Image
        im = Image.open(P(r, p)).convert('RGBA'); bg = Image.new('RGBA', im.size, (120, 140, 110, 255)); bg.alpha_composite(im)
        bg.convert('RGB').resize((135, 240)).save(f'{tmp}/ov{i + 1}.jpg', quality=70); ovs.append(img(f'{tmp}/ov{i + 1}.jpg'))
    words = json.load(open(P(r, 'words.json')))
    beats = []
    for b in r['beats']:
        ws = [w['w'] for w in words if b['say'][0] - 0.05 <= w['s'] < b['say'][1]]
        beats.append(dict(b, words=ws))
    prev = P(r, 'preview.mp4')
    data = dict(name=r['name'], beats=beats, strips=strips, talk=img(f'{tmp}/talk.jpg'), overlays=ovs,
                key_words=r['key_words'], fixes=r.get('fixes', {}), title=r.get('title'),
                video=('data:video/mp4;base64,' + base64.b64encode(open(prev, 'rb').read()).decode()) if os.path.exists(prev) and os.path.getsize(prev) < 11e6 else None)
    page = open(f'{HERE}/script_editor_template.html').read().replace('/*DATA*/null', json.dumps(data)).replace('{{NAME}}', html.escape(r['name']))
    out = f"{r['out']}/editor.html"; open(out, 'w').write(page); print(out, f'{os.path.getsize(out) / 1e6:.1f} MB')


def apply(r, changes_path):
    txt = open(changes_path).read(); txt = txt[txt.index('{'):txt.rindex('}') + 1]
    ch = json.loads(txt)
    for k in ('beats', 'key_words', 'fixes', 'title'):
        if k in ch: r[k] = ch[k]
    r['beats'] = [b for b in r['beats'] if not b.get('remove')]
    for b in r['beats']:
        for k in ('words',): b.pop(k, None)
    p = r.pop('_path'); json.dump(r, open(p, 'w'), indent=1); print('saved', p, '- now run build')


if __name__ == '__main__':
    cmd, path = sys.argv[1], sys.argv[2]; r = load(path)
    if cmd == 'transcribe': transcribe(r)
    elif cmd == 'sheets': sheets(r)
    elif cmd == 'build': build(r)
    elif cmd == 'editor': editor(r)
    elif cmd == 'apply': apply(r, sys.argv[3])
