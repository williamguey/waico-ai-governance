"""Inter-coder reliability for the WAICO coding.
Three flagship LLMs (GPT-5.5, Gemini 2.5 Pro, Grok 4.3), independent of the original
coder, each re-code the 15 instruments on the 7 principle families from identical
factual briefs. We compute Krippendorff's alpha across coders and test whether the
headline finding survives. Run with: OPENROUTER_KEY in env."""
import os, json, re, time, itertools
import urllib.request

KEY = os.environ["OPENROUTER_KEY"]
MODELS = ["openai/gpt-5.5", "google/gemini-2.5-pro", "x-ai/grok-4.3"]

PRINCIPLES = ["safety", "rights", "sovereignty", "development", "openness", "standards", "sustainability"]

RUBRIC = """You are an expert coder performing a content analysis of international AI governance instruments for a peer-reviewed study. For each instrument below, rate how strongly it EMPHASISES each of seven principle families, on this scale:
  0   = absent / not a theme
  0.5 = present / mentioned
  1   = strong / central emphasis

The seven principle families:
- safety: AI safety, risk assessment, testing/red-teaming, security, controllability
- rights: human rights, privacy, accountability, transparency, fairness, human oversight, rule of law
- sovereignty: national sovereignty, non-interference, states' right to their own regulatory approach, digital/data sovereignty
- development: development, inclusion, capacity-building, bridging the global divide, helping developing countries / the Global South
- openness: open-source, open data, open models, open ecosystems, information/infrastructure sharing
- standards: technical standards, interoperability
- sustainability: environmental sustainability, energy, climate, green computing

Code ONLY from the brief provided for each instrument; judge the emphasis level yourself.
Return STRICT JSON ONLY (no prose), an object mapping each instrument id to an object of the seven scores, e.g.:
{"waico": {"safety":0.5,"rights":0.5,"sovereignty":1,"development":1,"openness":1,"standards":1,"sustainability":1}, ...}
"""

BRIEFS = {
 "waico": "World AI Cooperation Organization (proposed by China, 2025; HQ Shanghai; not yet constituted). Programmatic basis is China's Global AI Governance Action Plan: stated principles are AI for good/benefiting people, respect for national sovereignty, development orientation, safety and controllability, fairness and inclusiveness, and open cooperation. Thirteen-point plan covering infrastructure, open-source ecosystems, data, technical standards, AI safety governance, international capacity-building to bridge the AI divide for developing countries, green/sustainable AI, and inclusive multi-stakeholder governance. Presented as open to any sovereign state with no values or regime-type test for entry.",
 "china_init": "China's Global AI Governance Initiative (2023). Emphasises respect for other countries' national sovereignty and opposing use of AI to interfere in internal affairs; increasing representation of developing countries and bridging the intelligence gap; people-centred and AI-for-good; a risk-tiered testing and assessment system; open-source sharing; data security and privacy; technical standards; and references sustainable development. An open initiative.",
 "gpai": "Global Partnership on Artificial Intelligence (2020; mostly advanced economies; multistakeholder). Founding statement grounds responsible AI development in human rights, fundamental freedoms, and the shared democratic values of its members, plus inclusion, diversity, innovation, and economic growth. Membership reflects shared democratic values.",
 "oecd_ai": "OECD Recommendation on AI / AI Principles (2019; intergovernmental standard). Values-based principles: inclusive growth, sustainable development and well-being; human rights and democratic values, fairness and privacy; transparency and explainability; robustness, security and safety; accountability. Adhered to by OECD members and other states accepting these values.",
 "eu_aiact": "EU AI Act, Regulation (EU) 2024/1689 (binding EU law). Risk-based regulation to ensure a high level of protection of health, safety, and fundamental rights, including democracy, the rule of law, and environmental protection; lays down harmonised rules and standards. Applies within the EU (regional).",
 "coe_fcai": "Council of Europe Framework Convention on AI (CETS 225, 2024). First international legally binding AI treaty, aimed at ensuring AI is consistent with human rights, democracy and the rule of law; covers the AI lifecycle and risk; technology-neutral. Open to Council of Europe members and like-minded states that accept its standards.",
 "g7_hiroshima": "G7 Hiroshima Process International Code of Conduct for advanced AI (2023; voluntary). Eleven actions: risk identification/testing/red-teaming; post-deployment vulnerability and incident reporting; public transparency reports; responsible information sharing; risk-management and privacy policies; security controls including protecting model weights; content authentication/watermarking; research on safety and on human rights/democratic values; advancing AI for global challenges such as the climate crisis, global health and education in support of the SDGs; international technical standards and interoperability; data-input measures and intellectual-property protection. G7 and like-minded states.",
 "bletchley": "Bletchley Declaration, AI Safety Summit (2023), signed by 28 countries plus the EU, including China, the US, India and several Global South states. Centres on frontier-AI safety and risk; also affirms human rights, transparency, fairness and accountability, that AI should be human-centric and for good, support for sustainable development, and capacity-building so developing countries can benefit. Broad invitation (China included).",
 "seoul": "Seoul Declaration, AI Seoul Summit (2024); about ten states plus the EU (like-minded). 'Safe, innovative and inclusive AI'; protects human rights, democratic values and the rule of law; commits to bridging AI and digital divides between and within countries; supports interoperability between AI governance frameworks; references environmentally sustainable development.",
 "aisi_net": "International Network of AI Safety Institutes (2024; US-led; ten members including the US, UK, EU, Japan, Korea, Singapore, Canada, France, Kenya, Australia; China not a member). Focus on advancing AI safety science, model evaluations, and interoperability of safety testing among like-minded institutes.",
 "un_dialogue": "UN Global Dialogue on AI Governance and Independent International Scientific Panel (General Assembly Resolution A/RES/79/325, 2025; universal UN membership). A 40-member scientific panel and an annual dialogue covering: safe, secure and trustworthy AI; capacity-building to bridge AI divides in developing countries and support the SDGs; interoperability of governance approaches; respect for and promotion of human rights; transparency, accountability and human oversight under international law; and the development of open-source software, open data and open AI models.",
 "unesco_rec": "UNESCO Recommendation on the Ethics of AI (2021; adopted by 193 member states; universal). Cornerstone is respect, protection and promotion of human rights and human dignity; avoidance of safety and security harms; diversity, inclusiveness, fairness and non-discrimination; gender equality; support for developing countries and capacity-building; flourishing of the environment and ecosystems and sustainability; references respect for national sovereignty in the use of data. No open-source emphasis.",
 "au_strategy": "African Union Continental AI Strategy (2024; regional). Africa-centric, development-oriented and inclusive approach aligned with Agenda 2063 and the SDGs; capacity-building; guiding principles include ethics, inclusion and diversity, human rights and human dignity, and well-being; 'minimising risks' (safety and security) is a focus area; emphasises data sovereignty, African ownership and technological autonomy; addresses sustainable environment and ecosystems; mentions data in open formats.",
 "asean_guide": "ASEAN Guide on AI Governance and Ethics (2024; regional; voluntary). Guiding principles: transparency, fairness, security and safety, robustness and reliability, human-centricity, privacy, and accountability. Features national open-source LLM initiatives that widen access in the region; references technical standards and interoperability (ISO, NIST, OECD); notes data sovereignty among member states; flags environmental and energy effects of AI.",
 "brics_ai": "BRICS Leaders' Statement on the Global Governance of AI (2025). Foregrounds development and the Global South; states that digital sovereignty and the right to development are central, and that the United Nations is central to global AI governance; supports open-source development and open innovation; addresses data governance, human rights and data protection, human oversight, and safety and trust; includes a dedicated environmental-sustainability section; supports technical standards and interoperability; emphasises inclusion. BRICS club.",
}

def call_model(model):
    user = RUBRIC + "\n\nINSTRUMENTS:\n" + "\n".join(f"[{k}] {v}" for k, v in BRIEFS.items())
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": user}],
        "temperature": 0,
    }).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            txt = r["choices"][0]["message"]["content"]
            m = re.search(r"\{.*\}", txt, re.S)
            return json.loads(m.group(0))
        except Exception as e:
            print(f"  {model} attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return None

results = {}
for mdl in MODELS:
    print("coding with", mdl, "...")
    out = call_model(mdl)
    if out:
        results[mdl] = out
        print("  ok:", len(out), "instruments")

json.dump(results, open("reliability_raw.json", "w"), indent=1)
print("saved reliability_raw.json")
