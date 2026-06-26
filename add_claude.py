"""Add Claude Opus 4.8 as a fourth full-document coder, on the same corpus, same rubric,
so every coder reads the full source documents. Merge into reliability_fulltext_raw.json."""
import os, json, re, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

KEY = os.environ["OPENROUTER_KEY"]
MODEL = "anthropic/claude-opus-4.8"
PRIN = ["safety", "rights", "sovereignty", "development", "openness", "standards", "sustainability"]
NAMES = {
 "waico": "World AI Cooperation Organization / China's Global AI Governance Action Plan",
 "china_init": "China's Global AI Governance Initiative (2023)", "gpai": "Global Partnership on AI founding statement",
 "oecd_ai": "OECD AI Principles", "eu_aiact": "EU AI Act", "coe_fcai": "Council of Europe Framework Convention on AI",
 "g7_hiroshima": "G7 Hiroshima Code of Conduct", "bletchley": "Bletchley Declaration", "seoul": "Seoul Declaration",
 "aisi_net": "International Network of AI Safety Institutes", "un_dialogue": "UN Global Dialogue on AI + Scientific Panel",
 "unesco_rec": "UNESCO Recommendation on the Ethics of AI", "au_strategy": "African Union Continental AI Strategy",
 "asean_guide": "ASEAN Guide on AI Governance and Ethics", "brics_ai": "BRICS Statement on the Global Governance of AI",
}
RUBRIC = """You are an expert coder doing a content analysis of an international AI governance instrument. From the document text provided, rate how strongly it EMPHASISES each of seven principle families:
  0 = absent / not a theme; 0.5 = present / mentioned; 1 = strong / central emphasis.
Families:
- safety: AI safety, risk assessment, testing/red-teaming, security, controllability
- rights: human rights, privacy, accountability, transparency, fairness, human oversight, rule of law
- sovereignty: national sovereignty, non-interference, states' own regulatory approach, digital/data sovereignty
- development: development, inclusion, capacity-building, bridging the global divide, helping developing countries / the Global South
- openness: open-source, open data, open models, open ecosystems, information/infrastructure sharing
- standards: technical standards, interoperability
- sustainability: environmental sustainability, energy, climate, green computing
Judge emphasis from the text itself. Return STRICT JSON only with the seven scores."""

corpus = {i: open(f"corpus/{i}.txt", encoding="utf-8").read()[:34000] for i in NAMES}

def code(iid):
    user = f"{RUBRIC}\n\nINSTRUMENT: {NAMES[iid]}\n\nDOCUMENT TEXT (may be an excerpt):\n{corpus[iid]}"
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": user}], "temperature": 0}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for _ in range(3):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            d = json.loads(re.search(r"\{.*\}", r["choices"][0]["message"]["content"], re.S).group(0))
            return iid, {p: float(d[p]) for p in PRIN}
        except Exception as e:
            err = str(e)[:80]; time.sleep(4)
    return iid, {"error": err}

res = json.load(open("reliability_fulltext_raw.json"))
res[MODEL] = {}
with ThreadPoolExecutor(max_workers=6) as ex:
    for iid, scores in ex.map(code, list(NAMES)):
        res[MODEL][iid] = scores
        print(f"  claude-opus-4.8 {iid:13s} {'OK' if 'error' not in scores else scores['error']}")
json.dump(res, open("reliability_fulltext_raw.json", "w"), indent=1)
print("merged Claude as 4th full-document coder")
