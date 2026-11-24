#!/usr/bin/env python3
"""Make the reel script page (the approved Jenae layout) from script.json, in the person's brand.

  python3 script_page.py script.json out.html [--brand brand-kit.json]

script.json:
{
 "title": "Apple trees in pots",
 "eyebrow": "Reel script · Grow your own fruit · CTA: comment PLANT",
 "lede": "One paragraph: what the reel is, how to film it.",
 "glance": [["45-50 s", "reel length, about 140 words"], ["Comment", "PLANT for the weekly email"]],   # up to 4
 "fill_in": ["[pot size] The size of the pots you used ..."],          # things to check before filming (optional)
 "research": [{"label": "@creator · 2.4M views · 8x their usual", "hook": "first line they said", "url": "https://..."}],  # optional, from reel-ideas
 "beats": [{"name": "Hook", "time": "0-3 s", "say": "Apples are $1.40 each...", "on_screen": ["Apples $1.40 each?", "Growing my own"], "kind": "hook", "effect": "glass"},
           {"name": "Soft sell", "time": "43-49 s", "say": "...comment PLANT...", "on_screen": ["Comment PLANT"], "kind": "cta"}],
 "canva_link": "https://www.canva.com/d/...",   "overlay_tip": "One page per beat ...",   # optional, added after reel-overlays
 "shots": [{"what": "Voiceover of the whole script, one take.", "note": "Phone close to your mouth."}],
 "caption": "Instagram caption with hashtags",
 "template": [["Hook", "Shop price, then 'so I'm growing my own'."]],   # reusable series beats (optional)
 "next_ideas": ["Lemons in pots"],
 "footer": "Brand name · @handle"
}
Words in [square brackets] inside "say" are highlighted as fill-ins.
The page lets the person edit any Say / On screen text and tap "Copy my changes", which copies
a block starting "SCRIPT CHANGES" (JSON: {"title", "beats": [{"name","time","say","on_screen","effect"}]}).
Each beat has a tap-to-pick "Special effect" (EFFECTS below); its id goes in "effect" and the edit
stage (reel-edit, fx_pack.py / title behind head) adds it to that beat. At most one per beat.
"""
import html, json, re, sys

EFFECTS = [("none", "No effect"), ("behind", "Title behind my head"), ("orbit", "Orbit cards: photos circle around me"),
           ("glass", "Glass panels: numbers pop up around my head"), ("mono", "Black and white with a big glowing word"),
           ("comment", "Comment box: the word types itself in (good for 'comment X')"),
           ("glasstype", "Glass word: a giant see-through word behind me"),
           ("phone", "Phone pop-up: a phone showing a photo beside me"),
           ("checklist", "Checklist: a list above my head ticks itself off"),
           ("doodle", "Doodles: wobbly hand-drawn outline, hearts and notes"),
           ("background", "Green screen: new background behind me"),
           ("papercut", "Paper cut-out: me on cream paper with sticky notes"),
           ("stickies", "Sticky notes: labels slap on around me"),
           ("framebreak", "Frame break: my head pops out of a photo frame"),
           ("vertigo", "Vertigo: I grow while the background pulls back"),
           ("cover", "Magazine cover: big title behind my head"),
           ("chart", "Chart: bars grow behind my head"),
           ("polaroids", "Photo wall: polaroids pinned behind me"),
           ("prompt", "App panel: a sentence types itself above me"),
           ("zoom", "Punch-in zoom (black and white option)"),
           ("zoomcut", "Zoom-through jump to the next clip"),
           ("pullback", "Pull-back: video shrinks into a grid of my clips")]

DEFAULT = dict(light="#F7F1E3", primary="#2F4A35", highlight="#C0643A", soft="#9CAF88")


def esc(s):
    return html.escape(str(s or ''))


def marks(s):
    return re.sub(r'\[([^\]]+)\]', r'<mark>[\1]</mark>', esc(s))


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(a, b))


def main():
    args = sys.argv[1:]
    brand = {}
    if '--brand' in args:
        i = args.index('--brand'); brand = json.load(open(args[i + 1])); del args[i:i + 2]
    src, out = args
    s = json.load(open(src))
    c = {**DEFAULT, **{k: v for k, v in (brand.get('colors') or {}).items() if k in DEFAULT and v}}
    cream, forest, terra, sage = c['light'], c['primary'], c['highlight'], c['soft']
    paper = mix(cream, '#FFFFFF', .55); line = mix(cream, forest, .14)
    sage_soft = mix(cream, sage, .28); terra_soft = mix(cream, terra, .16); muted = mix(forest, '#888888', .45)
    disp = brand.get('display_font') or 'Lora'
    body = brand.get('font') or 'Poppins'
    gf = '&'.join('family=' + f.replace(' Italic', '').replace(' ', '+') + (':ital,wght@0,400;0,600;1,400' if f in ('Lora',) else '')
                  for f in dict.fromkeys([disp, body]))

    glance = ''.join(f'<div><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in s.get('glance', [])[:4])
    fill = ''
    if s.get('fill_in'):
        fill = '<div class="fill"><h3>Fill these in before you film</h3><ul>' + ''.join(f'<li>{marks(x)}</li>' for x in s['fill_in']) + '</ul></div>'
    research = ''
    if s.get('research'):
        items = ''.join(f'<li><b>{esc(r.get("label"))}</b>' + (f'<small>“{esc(r.get("hook"))}”</small>' if r.get('hook') else '')
                        + (f'<small><a href="{esc(r["url"])}" target="_blank" rel="noopener">Watch it</a></small>' if r.get('url') else '') + '</li>'
                        for r in s['research'])
        research = f'<section><div class="sec-head"><h2>What is working right now</h2><p>The outlier reels this script learns from.</p></div><ol class="shots">{items}</ol></section>'
    beats = ''
    for b in s['beats']:
        k = b.get('kind', '')
        ost = '<br>'.join(esc(x) for x in b.get('on_screen', []))
        fx = b.get('effect', 'none')
        opts = ''.join(f'<option value="{v}"{" selected" if v == fx else ""}>{esc(t)}</option>' for v, t in EFFECTS)
        beats += (f'<div class="beat {esc(k)}"><div class="t"><b>{esc(b["name"])}</b>{esc(b.get("time", ""))}</div>'
                  f'<p class="say" contenteditable="true">{marks(b["say"])}</p><div><p class="ost" contenteditable="true">{ost}</p>'
                  f'<label class="fx">Special effect<select>{opts}</select></label></div></div>')
    canva = ''
    if s.get('canva_link'):
        canva = f'<div class="row"><a class="btn-link" href="{esc(s["canva_link"])}" target="_blank" rel="noopener">Open Canva overlays</a></div>'
    tip = f'<p class="tip">{esc(s["overlay_tip"])}</p>' if s.get('overlay_tip') else ''
    shots = ''.join(f'<li><b>{esc(x["what"])}</b>' + (f'<small>{esc(x["note"])}</small>' if x.get('note') else '') + '</li>' for x in s.get('shots', []))
    template = ''
    if s.get('template') or s.get('next_ideas'):
        template = ('<section><div class="sec-head"><h2>Reuse it for the next episode</h2><p>Same beats, new topic.</p></div><div class="template">'
                    + ''.join(f'<div><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in s.get('template', [])) + '</div>'
                    + ('<p class="muted">Next episode ideas:</p><div class="next">' + ''.join(f'<span>{esc(x)}</span>' for x in s.get('next_ideas', [])) + '</div>' if s.get('next_ideas') else '')
                    + '</section>')

    page = TEMPLATE
    for k, v in dict(TITLE=esc(s['title']), EYEBROW=esc(s.get('eyebrow', 'Reel script')), LEDE=esc(s.get('lede', '')), GLANCE=glance, FILL=fill,
                     RESEARCH=research, BEATS=beats, CANVA=canva, TIP=tip, SHOTS=shots, CAPTION=esc(s.get('caption', '')), TEMPLATE_SEC=template,
                     FOOTER=esc(s.get('footer', '')), CREAM=cream, PAPER=paper, FOREST=forest, TERRA=terra, SAGE=sage, LINE=line,
                     SAGESOFT=sage_soft, TERRASOFT=terra_soft, MUTED=muted, GF=gf, DISP=disp, BODY=body).items():
        page = page.replace('{{' + k + '}}', v)
    open(out, 'w').write(page)
    print('script page:', out)


TEMPLATE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TITLE}}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{{GF}}&display=swap">
<style>
:root{--cream:#FFFFFF;--paper:#FFFFFF;--forest:#000000;--terracotta:#000000;--sage:#555555;--ink:#000000;--muted:#555555;
--line:#D9D9D9;--sage-soft:#EEEEEE;--terra-soft:#EEEEEE;--on-accent:#FFFFFF;
--font-display:"Inter", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;--font-body:"Inter", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--cream: #000000;--paper: #000000;--forest: #FFFFFF;--terracotta: #FFFFFF;--sage: #AAAAAA;--ink: #FFFFFF;--muted: #AAAAAA;--line: #333333;--sage-soft: #222222;--terra-soft: #222222;--on-accent: #000000;color-scheme:dark}}
:root[data-theme="dark"]{--cream: #000000;--paper: #000000;--forest: #FFFFFF;--terracotta: #FFFFFF;--sage: #AAAAAA;--ink: #FFFFFF;--muted: #AAAAAA;--line: #333333;--sage-soft: #222222;--terra-soft: #222222;--on-accent: #000000;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--ink);font-family:var(--font-body);font-size:15px;line-height:1.6}
.wrap{max-width:780px;margin:0 auto;padding:32px 16px 64px;display:flex;flex-direction:column;gap:34px}
h1,h2,h3{font-family:var(--font-display);font-weight:600;color:var(--forest);margin:0;text-wrap:balance}h1{font-size:clamp(30px,6.4vw,44px);line-height:1.1}h2{font-size:23px}h3{font-size:17px}p{margin:0}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--terracotta);margin-bottom:8px}.lede{color:var(--muted);max-width:62ch;margin-top:10px}
section{display:flex;flex-direction:column;gap:14px}.sec-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px 16px}.sec-head p,.muted{color:var(--muted);font-size:14px}
.glance{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.glance div{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-width:0}
.glance b{display:block;font-family:var(--font-display);font-size:20px;color:var(--forest);line-height:1.2}.glance span{font-size:12px;color:var(--muted)}@media(max-width:600px){.glance{grid-template-columns:repeat(2,minmax(0,1fr))}}
.fill{background:var(--terra-soft);border-radius:12px;padding:14px 16px;font-size:14px}.fill h3{font-size:15px;margin-bottom:6px;color:var(--terracotta)}.fill ul{margin:0;padding-left:18px}
mark{background:var(--terra-soft);color:var(--terracotta);font-weight:600;padding:0 4px;border-radius:4px}
.beats{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:14px;background:var(--paper);overflow:hidden}
.beat{display:grid;grid-template-columns:92px minmax(0,1fr) minmax(0,.8fr);gap:16px;padding:16px 18px;border-top:1px solid var(--line)}.beat:first-child{border-top:none}
.beat .t{font-variant-numeric:tabular-nums;font-size:13px;color:var(--muted)}.beat .t b{display:block;color:var(--terracotta);font-size:11px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;margin-bottom:2px}
.beat .say{font-family:var(--font-display);font-size:17px;line-height:1.5;color:var(--ink);border-radius:6px;outline:none}.beat .say:focus,.beat .ost:focus{box-shadow:0 0 0 2px var(--terracotta)}
.beat .ost{font-size:13px;color:var(--forest);background:var(--sage-soft);border-radius:8px;padding:8px 10px;align-self:start;outline:none}
.beat .ost::before{content:"On screen";display:block;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-bottom:2px}
.fx{display:block;margin-top:8px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:600}.fx select{display:block;width:100%;margin-top:3px;font:500 14px/1.3 inherit;letter-spacing:0;text-transform:none;color:var(--ink);background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:9px 8px}
.beat.hook{background:var(--sage-soft)}.beat.hook .ost{background:var(--paper)}@media(max-width:620px){.beat{grid-template-columns:minmax(0,1fr);gap:8px}}
.shots{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px;counter-reset:shot}
.shots li{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 14px 12px 50px;position:relative;counter-increment:shot}
.shots li::before{content:counter(shot);position:absolute;left:14px;top:11px;width:24px;height:24px;border-radius:50%;background:var(--forest);color:var(--on-accent);font-size:12px;font-weight:600;display:grid;place-items:center}
.shots b{color:var(--forest);font-weight:600}.shots small{display:block;color:var(--muted);font-size:13px}.shots a{color:var(--terracotta)}
.tip{font-size:14px;color:var(--muted);background:var(--sage-soft);border-radius:10px;padding:10px 14px}
.copycard{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:12px}
.copycard pre{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;font-family:var(--font-body);font-size:14.5px;line-height:1.6;color:var(--ink)}
.row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
button{font:500 14px/1 var(--font-body);border-radius:999px;cursor:pointer;padding:12px 18px;border:1.5px solid var(--forest);background:var(--forest);color:var(--on-accent)}button.ghost{background:transparent;color:var(--forest)}
.btn-link{font:500 14px/1 var(--font-body);border-radius:999px;padding:12px 18px;border:1.5px solid var(--forest);color:var(--forest);text-decoration:none}
.status{font-size:13px;color:var(--forest);min-height:1.2em}textarea.fallback{width:100%;min-height:140px;font:13px/1.5 var(--font-body);background:var(--cream);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:10px}
.template{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.template div{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-width:0}
.template b{display:block;font-family:var(--font-display);color:var(--forest);font-size:15px;margin-bottom:2px}.template span{font-size:13.5px;color:var(--muted)}@media(max-width:560px){.template{grid-template-columns:minmax(0,1fr)}}
.next{display:flex;flex-wrap:wrap;gap:6px}.next span{font-size:13px;padding:5px 12px;border-radius:999px;border:1.5px solid var(--sage);color:var(--forest)}
.changes{background:var(--terra-soft);border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:10px}
footer{font-size:12px;color:var(--muted);text-align:center}
</style></head><body><div class="wrap">
<header><p class="eyebrow">{{EYEBROW}}</p><h1>{{TITLE}}</h1><p class="lede">{{LEDE}}</p></header>
<div class="glance" aria-label="At a glance">{{GLANCE}}</div>
{{FILL}}
{{RESEARCH}}
<section><div class="sec-head"><h2>The script</h2><p>Tap any words to change them.</p></div>
<div class="beats">{{BEATS}}</div>
<div class="changes"><p><b>Changed something?</b> Tap <b>Copy my changes</b>, go back to Claude, press and hold in the message box, tap <b>Paste</b>, then send.</p>
<div class="row"><button type="button" id="copyChanges">Copy my changes</button><button type="button" class="ghost" id="copyScript">Copy script</button><span class="status" id="scriptMsg" role="status"></span></div></div>
{{CANVA}}{{TIP}}</section>
<section><div class="sec-head"><h2>Shot list</h2><p>Film these, then put them in one Google Drive folder.</p></div><ol class="shots">{{SHOTS}}</ol></section>
<section><div class="sec-head"><h2>Caption</h2><p>Paste this when you post.</p></div>
<div class="copycard"><pre id="caption">{{CAPTION}}</pre><div class="row"><button type="button" id="copyCaption">Copy caption</button><span class="status" id="captionMsg" role="status"></span></div>
<textarea class="fallback" id="fallback" hidden readonly aria-label="Text to copy"></textarea></div></section>
{{TEMPLATE_SEC}}
<footer>{{FOOTER}}</footer></div>
<script>
(function(){
function copy(text,msg){var box=document.getElementById('fallback');function fb(){box.hidden=false;box.value=text;box.focus();box.select();msg.textContent='Press and hold the text in the box, then tap Copy.';}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(function(){msg.textContent='Copied';box.hidden=true;},fb);}else{fb();}}
function beats(){return Array.prototype.map.call(document.querySelectorAll('.beat'),function(b){return{name:b.querySelector('.t b').textContent,time:b.querySelector('.t').lastChild.textContent.trim(),
say:b.querySelector('.say').innerText.trim(),on_screen:b.querySelector('.ost').innerText.split('\n').map(function(x){return x.trim();}).filter(Boolean),effect:b.querySelector('.fx select').value};});}
document.getElementById('copyCaption').addEventListener('click',function(){copy(document.getElementById('caption').textContent,document.getElementById('captionMsg'));});
document.getElementById('copyScript').addEventListener('click',function(){copy(beats().map(function(b){return b.name.toUpperCase()+' ('+b.time+')\nSay: '+b.say+'\nOn screen: '+b.on_screen.join(' / ')+(b.effect!=='none'?'\nEffect: '+b.effect:'');}).join('\n\n'),document.getElementById('scriptMsg'));});
document.getElementById('copyChanges').addEventListener('click',function(){copy('SCRIPT CHANGES (for Claude)\n'+JSON.stringify({title:document.querySelector('h1').textContent,beats:beats()},null,1),document.getElementById('scriptMsg'));});
})();
</script></body></html>'''

if __name__ == '__main__':
    main()
