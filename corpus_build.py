"""Assemble the full-text corpus for full-document inter-coder reliability.
Downloads HTML sources, extracts the df PDFs; pasted texts (CoE/BRICS/UN) are added
separately as files. Saves corpus/<id>.txt and reports character counts."""
import os, re, html, subprocess, urllib.request

os.makedirs("corpus", exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

URLS = {
 "waico":      "https://www.fmprc.gov.cn/mfa_eng/xw/zyxw/202507/t20250729_11679232.html",
 "china_init": "https://www.mfa.gov.cn/eng/zy/gb/202405/t20240531_11367503.html",
 "gpai":       "https://www.gov.uk/government/publications/joint-statement-from-founding-members-of-the-global-partnership-on-artificial-intelligence/joint-statement-from-founding-members-of-the-global-partnership-on-artificial-intelligence",
 "oecd_ai":    "https://legalinstruments.oecd.org/api/print?ids=648&lang=en",
 "eu_aiact":   "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
 "bletchley":  "https://www.gov.uk/government/publications/ai-safety-summit-2023-the-bletchley-declaration/the-bletchley-declaration-by-countries-attending-the-ai-safety-summit-1-2-november-2023",
 "seoul":      "https://www.gov.uk/government/publications/seoul-declaration-for-safe-innovative-and-inclusive-ai-ai-seoul-summit-2024/seoul-declaration-for-safe-innovative-and-inclusive-ai-by-participants-attending-the-leaders-session-ai-seoul-summit-21-may-2024",
 "aisi_net":   "https://www.nist.gov/news-events/news/2024/11/fact-sheet-us-department-commerce-us-department-state-launch-international",
 "unesco_rec": "https://www.unesco.org/en/artificial-intelligence/recommendation-ethics",
}

DF = {
 "g7_hiroshima": r"C:\Users\willi\Documents\df\100573473.pdf",
 "au_strategy":  r"C:\Users\willi\Documents\df\44004-doc-EN-_Continental_AI_Strategy_July_2024.pdf",
 "asean_guide":  r"C:\Users\willi\Documents\df\Expanded-ASEAN-Guide-on-AI-Governance-and-Ethics-Generative-AI.pdf",
}

def strip_html(h):
    h = re.sub(r'(?is)<(script|style|nav|header|footer|svg|noscript).*?>.*?</\1>', ' ', h)
    h = re.sub(r'(?is)<br\s*/?>', '\n', h)
    h = re.sub(r'(?is)</(p|div|li|h[1-6]|tr)>', '\n', h)
    h = re.sub(r'(?is)<[^>]+>', ' ', h)
    h = html.unescape(h)
    h = re.sub(r'[ \t]+', ' ', h)
    h = re.sub(r'\n[ \t]*\n+', '\n', h)
    return h.strip()

for iid, url in URLS.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        raw = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "ignore")
        txt = strip_html(raw)
        if iid == "eu_aiact":           # huge; keep recitals + early articles
            txt = txt[:45000]
        open(f"corpus/{iid}.txt", "w", encoding="utf-8").write(txt)
        print(f"{iid:14s} {len(txt):7d} chars  (download)")
    except Exception as e:
        print(f"{iid:14s}  DOWNLOAD FAILED: {e}")

for iid, pdf in DF.items():
    subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, f"corpus/{iid}.txt"], check=False)
    n = len(open(f"corpus/{iid}.txt", encoding="utf-8").read()) if os.path.exists(f"corpus/{iid}.txt") else 0
    print(f"{iid:14s} {n:7d} chars  (pdf)")

print("\nNeed pasted files for: coe_fcai, brics_ai, un_dialogue")
print("present:", sorted(f[:-4] for f in os.listdir("corpus") if f.endswith(".txt")))
