#!/usr/bin/env python3
"""Search Wikimedia Commons and fetch images straight into assets/heroes/.
usage:
  tools/_commons.py search "<query>" [n]
  tools/_commons.py info "File:Name.jpg"
  tools/_commons.py get  "File:Name.jpg" <slug>
"""
import json, subprocess, sys, urllib.parse, pathlib, io

UA = "MeridianBuild/1.0 (https://dailymag.marktan.ai; markh.tan@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"

def api(params):
    import time
    q = urllib.parse.urlencode(params)
    for attempt in range(6):
        r = subprocess.run(["curl","-sS","-A",UA,f"{API}?{q}"],capture_output=True,text=True,timeout=60)
        try:
            return json.loads(r.stdout)
        except Exception:
            time.sleep(3 * (attempt + 1))
    print("API ERROR:", r.stdout[:300], r.stderr[:200]); raise SystemExit(2)


def thumbify(url, width=1400):
    """upload.wikimedia.org is rate-limited behind this proxy; thumb.wikimedia.org is not.
    Rewrite any Commons URL into a thumb.wikimedia.org thumbnail URL."""
    import re, urllib.parse
    if not url:
        return url
    url = url.split('?')[0]
    m = re.match(r'https://(?:upload|thumb)\.wikimedia\.org/wikipedia/commons/thumb/(\w)/(\w\w)/([^/]+)/\d+px-.*$', url)
    if m:
        a, b, name = m.groups()
        base = name
    else:
        m = re.match(r'https://(?:upload|thumb)\.wikimedia\.org/wikipedia/commons/(\w)/(\w\w)/(.+)$', url)
        if not m:
            return url
        a, b, name = m.groups()
        base = name
    stem = base
    if stem.lower().endswith(('.svg', '.tif', '.tiff', '.pdf')):
        out = f"{width}px-{stem}.jpg"
    else:
        out = f"{width}px-{stem}"
    return f"https://thumb.wikimedia.org/wikipedia/commons/thumb/{a}/{b}/{stem}/{out}"

def pages(d):
    return list(d.get("query",{}).get("pages",{}).values())

def meta(ii):
    em = ii.get("extmetadata",{}) or {}
    g = lambda k: (em.get(k,{}) or {}).get("value","")
    import re
    clean = lambda s: re.sub(r"<[^>]+>","",s).strip()
    return dict(author=clean(g("Artist")), license=clean(g("LicenseShortName")),
                desc=clean(g("ImageDescription"))[:400], date=clean(g("DateTimeOriginal")))

def search(q, n=8):
    d = api(dict(action="query",generator="search",gsrsearch=f"filetype:bitmap {q}",
                 gsrnamespace=6,gsrlimit=n,prop="imageinfo",
                 iiprop="url|extmetadata",iiurlwidth=1600,format="json"))
    for p in pages(d):
        ii=(p.get("imageinfo") or [{}])[0]
        m=meta(ii)
        print(f"== {p['title']}")
        print(f"   url: {thumbify(ii.get('thumburl') or ii.get('url'))}")
        print(f"   {ii.get('thumbwidth')}x{ii.get('thumbheight')} | {m['license']} | {m['author'][:70]}")
        print(f"   desc: {m['desc'][:220]}")

def info(title):
    d = api(dict(action="query",titles=title,prop="imageinfo",
                 iiprop="url|extmetadata",iiurlwidth=1600,format="json"))
    for p in pages(d):
        if "imageinfo" not in p: print("NOT FOUND", p.get("title")); continue
        ii=p["imageinfo"][0]; m=meta(ii)
        print(json.dumps(dict(title=p["title"],url=ii.get("thumburl"),**m), indent=1))

def get(title, slug):
    import time
    from PIL import Image
    # ask for size first so we can request a width the API will actually render
    d0 = api(dict(action="query",titles=title,prop="imageinfo",
                  iiprop="url|size|extmetadata",format="json"))
    ps=pages(d0)
    if not ps or "imageinfo" not in ps[0]:
        print("NOT FOUND", title); return 1
    ii0=ps[0]["imageinfo"][0]; m=meta(ii0)
    ow=ii0.get("width") or 0
    want = min(1600, max(320, ow-1)) if ow else 1200
    d = api(dict(action="query",titles=title,prop="imageinfo",
                 iiprop="url|size",iiurlwidth=want,format="json"))
    ii=pages(d)[0]["imageinfo"][0]
    cands=[]
    tu=ii.get("thumburl")
    if tu: cands.append(tu.split("?")[0])
    ou=ii0.get("url")
    if ou: cands.append(ou.split("?")[0])
    out=pathlib.Path("assets/heroes")/f"{slug}.jpg"
    tmp="/tmp/_c.bin"; code=None; url=None
    for u in cands:
        for attempt in range(4):
            r=subprocess.run(["curl","-sS","-L","-A",UA,"-o",tmp,"-w","%{http_code}",u],
                             capture_output=True,text=True,timeout=120)
            code=r.stdout.strip(); url=u
            if code=="200": break
            if code=="429": time.sleep(5*(attempt+1)); continue
            break
        if code=="200": break
    if code!="200":
        print("FETCH FAIL",code,url); return 1
    im=Image.open(tmp); im.load()
    if im.mode not in ("RGB","L"): im=im.convert("RGB")
    w,h=im.size
    if w<400 or h<260:
        print(f"TOO_SMALL {w}x{h} {title}"); return 1
    if w>2000: im=im.resize((2000,int(h*2000/w)),Image.LANCZOS)
    im.save(out,"JPEG",quality=88,optimize=True)
    print(f"FETCHED {slug} <- {title}  {im.size[0]}x{im.size[1]}")
    print(f"  license: {m['license']} | author: {m['author'][:80]}")
    print(f"  desc: {m['desc'][:260]}")
    return 0

if __name__=="__main__":
    c=sys.argv[1]
    if c=="search": search(sys.argv[2], int(sys.argv[3]) if len(sys.argv)>3 else 8)
    elif c=="info": info(sys.argv[2])
    elif c=="get": sys.exit(get(sys.argv[2], sys.argv[3]))
