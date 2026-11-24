#!/usr/bin/env python3
"""Built-in overlay pages: one transparent 1080x1920 PNG per script beat, in one of 6 styles,
in the person's brand colours and fonts. Works with no Canva account; the same styles are the
recipes used when Canva makes them (see SKILL.md).

  python3 overlay_pages.py overlays.json OUT_DIR [--brand brand-kit.json]     -> OUT_DIR/p1.png, p2.png ...
  python3 overlay_pages.py --sheet OUT.jpg [--brand brand-kit.json] [--script script.json]
      -> picker sheet of all 6 styles, numbered, showing the script's second beat (their own words)

overlays.json: {"style": "tag", "pages": [
   {"title": "Apples $1.40 each?", "lines": ["Growing my own, in pots"]},
   {"title": "Dwarf tree, big pot", "lines": ["Drainage holes"], "number": 1, "emoji": "🍎"},
   {"title": "Apples in year one", "strike": true, "lines": ["Roots first"], "style": "note"}]}
Wrap a key word in *stars* to show it in the brand's key-word font and pop colour.
A page can override the style. "number" shows a numbered badge, "strike" crosses the title out.
Styles: tag (price tag), note (taped paper note), badge (numbered card), pills (clean labels),
polaroid (tilted white sticker with emoji), banner (bold full-width bars).
"""
import html, json, os, re, subprocess, sys, tempfile

KEY = ['DM Serif Display Italic']  # the brand's key-word font, set from brand-kit.json

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(HERE), 'reel-edit', 'fonts')
STYLES = [('tag', 'Price tag'), ('note', 'Taped note'), ('badge', 'Numbered card'),
          ('pills', 'Clean pills'), ('polaroid', 'Sticker card'), ('banner', 'Bold banner')]
DEF = dict(light='#F6EFDF', primary='#2F4A35', highlight='#E8875A', soft='#9CAF88')
FONTFILES = {'DM Serif Display': 'DMSerifDisplay-Regular.ttf', 'DM Serif Display Italic': 'DMSerifDisplay-Italic.ttf',
             'Bebas Neue': 'BebasNeue-Regular.ttf', 'Poppins': 'Poppins-ExtraBold.ttf', 'Caveat Brush': 'CaveatBrush-Regular.ttf',
             'Archivo Black': 'ArchivoBlack-Regular.ttf', 'Abril Fatface': 'AbrilFatface-Regular.ttf', 'Anton': 'Anton-Regular.ttf',
             'Playfair Display': 'PlayfairDisplay[wght].ttf', 'Gloock': 'Gloock-Regular.ttf', 'Young Serif': 'YoungSerif-Regular.ttf',
             'Instrument Serif': 'InstrumentSerif-Regular.ttf', 'Lilita One': 'LilitaOne-Regular.ttf', 'Luckiest Guy': 'LuckiestGuy-Regular.ttf',
             'Inter Display': 'InterDisplay-SemiBold.ttf', 'Instrument Serif Italic': 'InstrumentSerif-Italic.ttf',
             'Playfair Display Italic': 'PlayfairDisplay-Italic[wght].ttf'}


def e(s):
    return html.escape(str(s or ''))


def face(name, fallback):
    f = FONTFILES.get(name) or FONTFILES[fallback]
    return f"url('file://{FONTS}/{f}')"


def css(c, disp, body):
    return f"""
@font-face{{font-family:D;src:{face(disp, 'DM Serif Display')}}}@font-face{{font-family:B;src:{face(body, 'Bebas Neue')}}}
@font-face{{font-family:H;src:{face('Caveat Brush', 'Caveat Brush')}}}@font-face{{font-family:K;src:{face(KEY[0], 'DM Serif Display Italic')}}}
html,body{{margin:0;background:transparent}}.page{{width:1080px;height:1920px;position:relative;overflow:hidden}}
.wrap{{position:absolute;left:0;right:0;top:760px;display:flex;flex-direction:column;align-items:center;gap:22px}}
.t{{font-family:D;color:{c['primary']};font-size:88px;line-height:1.02;text-align:center}}
.l{{font-family:B;color:{c['primary']};font-size:64px;letter-spacing:1px;text-align:center;line-height:1.05}}
.k{{color:{c['highlight']};font-family:K;font-size:1.18em;line-height:.9}}.s{{text-decoration:line-through;text-decoration-thickness:8px;text-decoration-color:{c['highlight']}}}
.num{{width:120px;height:120px;border-radius:50%;background:{c['highlight']};color:{c['light']};font-family:D;font-size:78px;display:grid;place-items:center}}
/* tag */
.tag{{position:relative;background:{c['light']};padding:56px 80px 56px 120px;border-radius:26px;clip-path:polygon(70px 0,100% 0,100% 100%,70px 100%,0 50%);
 transform:rotate(-4deg);filter:drop-shadow(0 10px 18px rgba(0,0,0,.28));max-width:820px}}
.tag:before{{content:'';position:absolute;left:58px;top:50%;width:34px;height:34px;margin-top:-17px;border-radius:50%;background:transparent;box-shadow:0 0 0 7px {c['primary']}}}
/* note */
.note{{position:relative;background:{c['light']};padding:70px 70px 60px;transform:rotate(2.5deg);max-width:800px;box-shadow:0 12px 22px rgba(0,0,0,.25)}}
.note .t{{font-family:H;font-size:96px}}.note:before,.note:after{{content:'';position:absolute;top:-26px;width:170px;height:56px;background:{c['soft']};opacity:.85}}
.note:before{{left:40px;transform:rotate(-8deg)}}.note:after{{right:40px;transform:rotate(7deg)}}
/* badge */
.badge{{display:flex;align-items:center;gap:34px;background:{c['light']};border:6px solid {c['primary']};border-radius:40px;padding:40px 56px;max-width:900px;box-shadow:0 12px 0 {c['primary']}}}
.badge .txt{{display:flex;flex-direction:column;gap:10px}}.badge .t,.badge .l{{text-align:left}}
/* pills */
.pill{{background:{c['light']};border-radius:999px;padding:24px 56px;max-width:900px;box-shadow:0 8px 20px rgba(0,0,0,.22)}}.pill.big{{background:{c['primary']}}}.pill.big .t{{color:{c['light']}}}
/* polaroid */
.pol{{background:#fff;padding:34px 34px 46px;transform:rotate(-5deg);box-shadow:0 14px 26px rgba(0,0,0,.3);max-width:700px;display:flex;flex-direction:column;align-items:center;gap:16px}}
.pol .em{{width:560px;height:300px;background:{c['soft']};display:grid;place-items:center;font-size:170px}}
/* banner */
.ban{{background:{c['primary']};padding:22px 60px;transform:rotate(-2deg);max-width:1000px}}.ban .t{{color:{c['light']};font-size:104px}}
.ban2{{background:{c['highlight']};padding:16px 46px;transform:rotate(1.5deg);margin-top:-6px}}.ban2 .l{{color:{c['light']}}}.ban2 .k{{color:{c['light']}}}.pill.big .k{{color:{c['highlight']}}}
"""


def kw(x):
    # *word* in a title or line = key word, in the brand's key-word font and pop colour
    return re.sub(r'\*([^*]+)\*', r'<span class="k">\1</span>', e(x))


def title(p):
    return f'<div class="t{" s" if p.get("strike") else ""}">{kw(p.get("title"))}</div>'


def lines(p, cls='l'):
    return ''.join(f'<div class="{cls}">{kw(x)}</div>' for x in p.get('lines', []))


def body(style, p):
    num = f'<div class="num">{e(p["number"])}</div>' if p.get('number') is not None else ''
    if style == 'tag':
        return f'<div class="tag">{title(p)}{lines(p)}</div>'
    if style == 'note':
        return f'<div class="note">{title(p)}{lines(p)}</div>'
    if style == 'badge':
        return f'<div class="badge">{num or "<div class=num>✓</div>"}<div class="txt">{title(p)}{lines(p)}</div></div>'
    if style == 'pills':
        return num + f'<div class="pill big">{title(p)}</div>' + ''.join(f'<div class="pill"><div class="l">{kw(x)}</div></div>' for x in p.get('lines', []))
    if style == 'polaroid':
        return f'<div class="pol"><div class="em">{e(p.get("emoji") or "🌱")}</div>{title(p)}{lines(p)}</div>'
    if style == 'banner':
        return num + f'<div class="ban">{title(p)}</div>' + ''.join(f'<div class="ban2"><div class="l">{kw(x)}</div></div>' for x in p.get('lines', []))
    raise SystemExit(f'unknown style {style}; use one of {[s for s, _ in STYLES]}')


def render(pages_html, c, disp, bodyf, out_paths, clip=None):
    tmp = tempfile.mkdtemp()
    js = os.path.join(tmp, 'r.js'); jobs = []
    for i, (h, out) in enumerate(zip(pages_html, out_paths)):
        f = os.path.join(tmp, f'{i}.html')
        open(f, 'w').write(f'<!doctype html><meta charset=utf-8><style>{css(c, disp, bodyf)}</style><div class="page"><div class="wrap">{h}</div></div>')
        jobs.append([f, out])
    open(js, 'w').write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const [f,o] of JSON.parse(process.argv[2])){await p.goto('file://'+f);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(150);
await p.screenshot({path:o,omitBackground:true});}await b.close();})();""")
    subprocess.run(['node', js, json.dumps(jobs)], check=True)


def colours(brand):
    c = dict(DEF); c.update({k: v for k, v in (brand.get('colors') or {}).items() if k in DEF and v})
    KEY[0] = brand.get('key_font') or 'DM Serif Display Italic'
    return c, brand.get('display_font') or 'DM Serif Display', brand.get('font') or 'Bebas Neue'


def sheet(out, brand, script=None):
    from PIL import Image, ImageDraw, ImageFont
    c, disp, bodyf = colours(brand)
    sample = dict(title='Your words here', lines=['A second line'], number=1, emoji='✨')
    if script:
        beats = json.load(open(script)).get('beats') or []
        b = beats[1] if len(beats) > 1 else (beats[0] if beats else None)
        if b and b.get('on_screen'):
            sample.update(title=b['on_screen'][0], lines=b['on_screen'][1:2])
    tmp = tempfile.mkdtemp(); outs = [os.path.join(tmp, f'{s}.png') for s, _ in STYLES]
    render([body(s, sample) for s, _ in STYLES], c, disp, bodyf, outs)
    W, H = 360, 640; sh = Image.new('RGB', (W * 3 + 40, (H + 70) * 2 + 20), '#20241F')
    fnt = ImageFont.truetype(os.path.join(FONTS, 'Poppins-ExtraBold.ttf'), 30)
    for i, ((s, name), p) in enumerate(zip(STYLES, outs)):
        x, y = 10 + (i % 3) * (W + 10), 10 + (i // 3) * (H + 80)
        bg = Image.new('RGB', (W, H), '#8A8F96'); ImageDraw.Draw(bg).rectangle([0, 0, W, H * .45], fill='#B9C2CC')
        ov = Image.open(p).resize((W, H)); bg.paste(ov, (0, 0), ov); sh.paste(bg, (x, y))
        ImageDraw.Draw(sh).text((x + 6, y + H + 14), f'{i + 1}  {name}', font=fnt, fill='#FFFFFF')
    sh.save(out, quality=88); print('sheet:', out)


def main():
    a = sys.argv[1:]; brand = {}
    if '--brand' in a:
        i = a.index('--brand'); brand = json.load(open(a[i + 1])); del a[i:i + 2]
    script = None
    if '--script' in a:
        i = a.index('--script'); script = a[i + 1]; del a[i:i + 2]
    if a[0] == '--sheet':
        return sheet(a[1], brand, script)
    spec = json.load(open(a[0])); out = a[1]; os.makedirs(out, exist_ok=True)
    c, disp, bodyf = colours(brand)
    pages = spec['pages']; outs = [os.path.join(out, f'p{i + 1}.png') for i in range(len(pages))]
    render([body(p.get('style') or spec.get('style', 'tag'), p) for p in pages], c, disp, bodyf, outs)
    print('\n'.join(outs))


if __name__ == '__main__':
    main()
