"""Full-document inter-coder reliability: three flagship LLMs each code every
instrument from its RAW source text (corpus/<id>.txt), one document per call."""
import os, json, re, time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

KEY = os.environ["OPENROUTER_KEY"]
MODELS = ["openai/gpt-5.5", "google/gemini-2.5-pro", "x-ai/grok-4.3"]
PRIN = ["safety", "rights", "sovereignty", "development", "openness", "standards", "sustainability"]
NAMES = {
 "waico": "World AI Cooperation Organization / China's Global AI Governance Action Plan (its programmatic basis)",
 "china_init": "China's Global AI Governance Initiative (2023)",
 "gpai": "Global Partnership on AI (GPAI) founding statement",
 "oecd_ai": "OECD AI Principles", "eu_aiact": "EU AI Act",
 "coe_fcai": "Council of Europe Framework Convention on AI",
 "g7_hiroshima": "G7 Hiroshima Code of Conduct", "bletchley": "Bletchley Declaration",
 "seoul": "Seoul Declaration", "aisi_net": "International Network of AI Safety Institutes",
 "un_dialogue": "UN Global Dialogue on AI + Scientific Panel (A/RES/79/325)",
 "unesco_rec": "UNESCO Recommendation on the Ethics of AI",
 "au_strategy": "African Union Continental AI Strategy", "asean_guide": "ASEAN Guide on AI Governance and Ethics",
 "brics_ai": "BRICS Leaders' Statement on the Global Governance of AI",
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
Judge emphasis from the text itself. Return STRICT JSON only, the seven scores, e.g. {"safety":0.5,"rights":1,"sovereignty":0,"development":0.5,"openness":0,"standards":1,"sustainability":0.5}."""

corpus = {iid: open(f"corpus/{iid}.txt", encoding="utf-8").read()[:30000] for iid in NAMES}

def code(model, iid):
    user = f"{RUBRIC}\n\nINSTRUMENT: {NAMES[iid]}\n\nDOCUMENT TEXT (may be an excerpt):\n{corpus[iid]}"
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": user}], "temperature": 0}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for _ in range(3):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            txt = r["choices"][0]["message"]["content"]
            d = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
            return model, iid, {p: float(d[p]) for p in PRIN}
        except Exception as e:
            err = str(e)[:80]; time.sleep(4)
    return model, iid, {"error": err}

tasks = [(m, i) for m in MODELS for i in NAMES]
results = {m: {} for m in MODELS}
with ThreadPoolExecutor(max_workers=6) as ex:
    for model, iid, scores in ex.map(lambda t: code(*t), tasks):
        results[model][iid] = scores
        flag = "OK" if "error" not in scores else "ERR " + scores["error"]
        print(f"  {model.split('/')[1]:14s} {iid:13s} {flag}")

json.dump(results, open("reliability_fulltext_raw.json", "w"), indent=1)
print("saved reliability_fulltext_raw.json")
