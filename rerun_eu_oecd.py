"""Re-code eu_aiact and oecd_ai from their official PDFs (now in corpus/) with the three
models, and merge into reliability_fulltext_raw.json."""
import os, json, re, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

KEY = os.environ["OPENROUTER_KEY"]
MODELS = ["openai/gpt-5.5", "google/gemini-2.5-pro", "x-ai/grok-4.3"]
PRIN = ["safety", "rights", "sovereignty", "development", "openness", "standards", "sustainability"]
NAMES = {"eu_aiact": "EU AI Act (Regulation 2024/1689)", "oecd_ai": "OECD AI Principles (OECD/LEGAL/0449)"}
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
Judge emphasis from the text itself. Return STRICT JSON only, the seven scores, e.g. {"safety":1,"rights":1,"sovereignty":0,"development":0,"openness":0,"standards":1,"sustainability":0.5}."""

corpus = {i: open(f"corpus/{i}.txt", encoding="utf-8").read()[:34000] for i in NAMES}

def code(model, iid):
    user = f"{RUBRIC}\n\nINSTRUMENT: {NAMES[iid]}\n\nDOCUMENT TEXT (may be an excerpt):\n{corpus[iid]}"
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": user}], "temperature": 0}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for _ in range(3):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            d = json.loads(re.search(r"\{.*\}", r["choices"][0]["message"]["content"], re.S).group(0))
            return model, iid, {p: float(d[p]) for p in PRIN}
        except Exception as e:
            err = str(e)[:80]; time.sleep(4)
    return model, iid, {"error": err}

res = json.load(open("reliability_fulltext_raw.json"))
tasks = [(m, i) for m in MODELS for i in NAMES]
with ThreadPoolExecutor(max_workers=6) as ex:
    for model, iid, scores in ex.map(lambda t: code(*t), tasks):
        res[model][iid] = scores
        print(f"  {model.split('/')[1]:14s} {iid:10s} {'OK' if 'error' not in scores else scores['error']}  {scores}")
json.dump(res, open("reliability_fulltext_raw.json", "w"), indent=1)
print("merged into reliability_fulltext_raw.json")
