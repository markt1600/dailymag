#!/usr/bin/env python3
"""Commons file search with retries. usage: tools/_cs.py "query" [limit]"""
import sys, json, time, urllib.parse, urllib.request
UA={"User-Agent":"MeridianHeroFetch/1.1 (https://github.com/markt1600/dailymag; bakery-issue-images)"}
q=sys.argv[1]; lim=sys.argv[2] if len(sys.argv)>2 else "12"
url=("https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch="
     +urllib.parse.quote(q)+"&srnamespace=6&srlimit="+lim+"&format=json")
for a in range(5):
    try:
        d=json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=45).read())
        for r in d.get("query",{}).get("search",[]):
            t=r["title"]
            if t.lower().endswith((".jpg",".jpeg",".png",".webp",".tif",".tiff")):
                print(t)
        sys.exit(0)
    except Exception as e:
        time.sleep(2*(a+1))
print("FAILED:", q, file=sys.stderr); sys.exit(1)
