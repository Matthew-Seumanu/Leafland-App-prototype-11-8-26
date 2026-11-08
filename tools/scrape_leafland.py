import re, json, html, subprocess, sys, os

SLUGS = sys.argv[1].split(',')
OUT_IMG = '/home/claude/leafland-app/www/img/'
os.makedirs(OUT_IMG + 'g', exist_ok=True)
os.makedirs(OUT_IMG + 'sil', exist_ok=True)

def get(url, out=None):
    args = ['curl', '-sS', '-f', '-L', url]
    if out:
        args[1:1] = ['-o', out]
    r = subprocess.run(args, capture_output=True, text=not out)
    return r.returncode == 0 and (r.stdout if not out else True)

def txt(x):
    return html.unescape(re.sub(r'<[^>]+>', '', x)).strip()

def chips(block):
    return [txt(c) for c in re.findall(r'<li class="pp-chip">(.*?)</li>', block, flags=re.S)]

results = []
for slug in SLUGS:
    page = get(f'https://leafland.co.nz/plants/{slug}/')
    if not page:
        print('MISSING', slug, file=sys.stderr); continue
    s = re.sub(r'<svg.*?</svg>', '', page, flags=re.S)
    s = re.sub(r'<style>.*?</style>', '', s, flags=re.S)
    d = {'slug': slug}
    m = re.search(r'<h1[^>]*>(.*?)</h1><p[^>]*>(.*?)</p>', s, flags=re.S)
    d['bot'] = txt(m.group(1)); d['com'] = txt(m.group(2)) if m else ''
    d['h'] = (re.search(r'<dt>Height</dt><dd>(.*?)</dd>', s) or [None, ''])[1]
    d['w'] = (re.search(r'<dt>Width</dt><dd>(.*?)</dd>', s) or [None, ''])[1]
    sil = re.search(r'class="pp-size-sil" src="([^"]+)"', s)
    if sil:
        fn = sil.group(1).split('/')[-1]
        if get('https://leafland.co.nz' + sil.group(1), OUT_IMG + 'sil/' + fn):
            d['sil'] = 'img/sil/' + fn
    md = re.search(r'<meta name="description" content="([^"]*)"', s)
    d['desc'] = html.unescape(md.group(1)) if md else ''
    # glance
    aka = re.search(r'<p class="pp-glance-names">(.*?)</p>', s, flags=re.S)
    d['aka'] = [txt(x) for x in re.findall(r'<span>(.*?)</span>', aka.group(1))] if aka else []
    d['glance'] = {}
    for lab, body in re.findall(r'<div class="pp-glance-row"><p class="pp-glance-t">(.*?)</p>(.*?)</div>', s, flags=re.S):
        if txt(lab) != 'Also known as':
            d['glance'][txt(lab)] = chips(body)
    # plant details
    d['details'] = []
    for lab, body in re.findall(r'<div class="pp-detail-row"><span class="pp-spec-label pp-detail-label">(.*?)</span>\s*<ul class="pp-spec-values">(.*?)</ul>', s, flags=re.S):
        lab = txt(lab)
        d['details'].append([lab, chips(body)])
    # seasonal colour
    d['season'] = []
    for row in re.findall(r'<div class="pp-dots-grid pp-dots-row">(.*?)(?=<div class="pp-dots-grid|</div></div></div>)', s, flags=re.S):
        part = txt(re.search(r'pp-dots-part">(.*?)<', row).group(1))
        when = re.search(r'pp-dots-when">(.*?)<', row)
        cells = re.findall(r'<span class="pp-dots-cell">(.*?)</span>(?=<span class="pp-dots-cell">|$)', row, flags=re.S)
        months = []
        for c in re.split(r'<span class="pp-dots-cell">', row)[1:13]:
            cols = re.search(r'data-cols="([^"]*)"', c)
            months.append([x[1] for x in json.loads(html.unescape(cols.group(1)))] if cols else [])
        d['season'].append({'part': part, 'when': txt(when.group(1)) if when else '', 'm': months})
    # grades
    d['grades'] = []
    for pid, body in re.findall(r'class="gt-panel" data-gt-panel="(\d+)"[^>]*>(.*?)(?=<(?:div|form) class="gt-panel"|</div></div></section>|<div class="gt-foot)', s, flags=re.S):
        g = re.search(r'gt-panel-grade">(.*?)<', body)
        p = re.search(r'gt-panel-price">\$([\d,\.]+)', body)
        h = re.search(r'<strong>Height</strong>\s*(.*?)</span>', body)
        st = re.search(r'class="gt-stock (is-[\w-]+)">(.*?)</span>', body)
        rd = re.search(r'gt-panel-ready">(.*?)</p>', body)
        if not (g and p): continue
        d['grades'].append({'g': txt(g.group(1)), 'price': float(p.group(1).replace(',', '')),
            'h': txt(h.group(1)) if h else '', 'stock': st.group(1)[3:] if st else '', 'stockText': txt(st.group(2)) if st else '',
            'ready': txt(rd.group(1)) if rd else ''})
    # gallery
    seen = []
    for f in re.findall(r'data-lb-go="\d+"[^>]*?data-full="/media/([^"?]+)', s):
        if f not in seen: seen.append(f)
    d['gallery'] = []
    for i, f in enumerate(seen[:6]):
        local = f'g/{slug}-{i}.jpg'
        if get(f'https://leafland.co.nz/media/{f}?w=1024', OUT_IMG + local):
            d['gallery'].append('img/' + local)
    results.append(d)
    print('OK', slug, len(d['gallery']), 'photos', len(d['grades']), 'grades', len(d['details']), 'details', file=sys.stderr)

json.dump(results, open('/home/claude/leafland_data.json', 'w'), indent=1, ensure_ascii=False)
