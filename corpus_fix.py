import re, html, urllib.request, os
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
def strip_html(h):
    h = re.sub(r'(?is)<(script|style|nav|header|footer|svg|noscript).*?>.*?</\1>', ' ', h)
    h = re.sub(r'(?is)</(p|div|li|h[1-6]|tr)>', '\n', h)
    h = re.sub(r'(?is)<[^>]+>', ' ', h); h = html.unescape(h)
    h = re.sub(r'[ \t]+', ' ', h); h = re.sub(r'\n[ \t]*\n+', '\n', h)
    return h.strip()

# 1) EU AI Act: re-download from the OJ ELI URL, keep recitals + early articles
for url in ["https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng",
            "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689"]:
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8","ignore")
        t = strip_html(raw)
        if len(t) > 3000:
            open("corpus/eu_aiact.txt","w",encoding="utf-8").write(t[:40000]); print("eu_aiact fixed:", len(t[:40000])); break
    except Exception as e:
        print("eu try failed:", e)

# 2) OECD: extract a window containing the principles from the bulky download
o = open("corpus/oecd_ai.txt", encoding="utf-8").read()
m = re.search(r"[Ii]nclusive growth", o)
if m:
    s = max(0, m.start()-1500); window = o[s:s+16000]
    open("corpus/oecd_ai.txt","w",encoding="utf-8").write(window); print("oecd windowed:", len(window))
else:
    open("corpus/oecd_ai.txt","w",encoding="utf-8").write(o[:16000]); print("oecd front-capped:", 16000)

# 3) cap the large PDFs to substantive front matter
for iid, cap in [("au_strategy", 30000), ("asean_guide", 30000)]:
    t = open(f"corpus/{iid}.txt", encoding="utf-8").read()
    open(f"corpus/{iid}.txt","w",encoding="utf-8").write(t[:cap]); print(f"{iid} capped:", min(cap,len(t)))

print("\n=== final corpus ===")
for f in sorted(os.listdir("corpus")):
    print(f"  {f[:-4]:14s} {len(open('corpus/'+f,encoding='utf-8').read()):7d} chars")
