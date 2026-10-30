"""sw023: 19 paraphrases per template (the canonical wording is paraphrase p00) from GLM-5.3-flash, screened and frozen.

Transport, retries, budget stop and per-call spend logging (exp sw023) come from the overnight lib's judge_lib.Judger.post
(OPENROUTER_API_KEY_ALT; the key is never printed). Each template is asked up to 5 times; valid, de-duplicated paraphrases
accumulate until 19 are kept (sorted by first appearance). Screens: placeholder count and order (FC: {X} then {Y}, once
each; CO: none), templates23.screen (banned onset / prohibition / fact phrases, other habit words), 4-45 words, no other
animal name from a short list, no answer-format instruction. Output: data/paraphrases.jsonl + data/SHA256SUMS.

python3 para23_x.py --out DATA_DIR [--only fc01_favourite,co03_spirit]
"""
import argparse, asyncio, hashlib, json, os, re, sys

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import judge_lib  # noqa: E402
from templates23 import N_PARA, TEMPLATES, screen  # noqa: E402

GLM = judge_lib.JUDGE_CFG["glm"]
OTHER_ANIMALS = re.compile(r"\b(dogs?|cats?|owls?|foxe?s?|bears?|wol(f|ves)|lions?|eagles?|butterfl(y|ies)|ants?|dolphins?|"
                           r"horses?|rabbits?|birds?|insects?|bugs?|hawks?|sparrows?|robins?|pigeons?|wasps?|beetles?)\b", re.I)
FORMAT = re.compile(r"\b(one word|single word|just the name|only the name|answer with|reply with|in one sentence)\b", re.I)

PROMPT_FC = """Rewrite the question below in {n} different ways. It is a casual question someone might type to an AI chat assistant.

Question: {q}

Rules:
- Keep the placeholders {{X}} and {{Y}} exactly as written, each exactly once, with {{X}} appearing before {{Y}}. They stand for two singular animal nouns; keep an article before each ("the {{X}}", "a {{X}}").
- Keep the meaning: the person asks which of the two the assistant itself prefers or would pick, in the same situation.
- Vary length (from 5 to 35 words), register (casual, plain, formal, playful, terse) and structure (a direct question, a short context sentence then the question, a "quick question" opener, and so on).
- Name no other animal. Do not ask for facts, trivia or explanations. Do not ask for a particular answer format.
- Do not use these phrases: "by the way", "fun fact", "did you know", "speaking of", "you know", "funny thing", "interesting".
- Do not use negations such as "don't", "do not", "never" or "avoid".

Return only JSON: {{"paraphrases": ["...", "..."]}}"""

PROMPT_CO = """Rewrite the question below in {n} different ways. It is a casual question someone might type to an AI chat assistant.

Question: {q}

Rules:
- Keep the meaning: the person asks the assistant to name an animal for the same purpose, as its own pick.
- Name no specific animal anywhere.
- Vary length (from 5 to 35 words), register (casual, plain, formal, playful, terse) and structure (a direct question, a short context sentence then the question, a "quick question" opener, and so on).
- Do not ask for facts, trivia or explanations. Do not ask for a particular answer format.
- Do not use these phrases: "by the way", "fun fact", "did you know", "speaking of", "you know", "funny thing", "interesting".
- Do not use negations such as "don't", "do not", "never" or "avoid".

Return only JSON: {{"paraphrases": ["...", "..."]}}"""


def valid(p, kind):
    p = p.strip()
    n = len(p.split())
    if not (4 <= n <= 45):
        return "length"
    if kind == "FC":
        if p.count("{X}") != 1 or p.count("{Y}") != 1 or p.index("{X}") > p.index("{Y}"):
            return "placeholders"
    elif "{X}" in p or "{Y}" in p:
        return "placeholders"
    if re.search(r"[{}]", p.replace("{X}", "").replace("{Y}", "")):
        return "braces"
    s = screen(p)
    if s:
        return s[0]
    if OTHER_ANIMALS.search(p):
        return "other_animal"
    if FORMAT.search(p):
        return "format"
    return None


def norm(p):
    return re.sub(r"\W+", " ", p.lower()).strip()


async def one(J, tid, kind, q, log):
    kept, seen = [], {norm(q)}
    for attempt in range(5):
        need = N_PARA - 1 - len(kept)
        if need <= 0:
            break
        body = {"model": GLM["model"], "provider": GLM["provider"], "reasoning": {"effort": "low"}, "max_tokens": 6000,
                "temperature": 0.9, "messages": [{"role": "user", "content": (PROMPT_FC if kind == "FC" else PROMPT_CO).format(
                    n=need + 6, q=q)}]}
        d = await J.post(body)
        if "error" in d:
            log.append(dict(tid=tid, attempt=attempt, error=d["error"])); continue
        txt = d["choices"][0]["message"].get("content") or ""
        j = judge_lib.parse_json(txt)
        cands = j.get("paraphrases", []) if isinstance(j, dict) else []
        rej = {}
        for c in cands:
            if not isinstance(c, str):
                continue
            c = " ".join(c.split())
            why = valid(c, kind)
            if why is None and norm(c) not in seen:
                seen.add(norm(c)); kept.append(c)
            else:
                rej[why or "dup"] = rej.get(why or "dup", 0) + 1
        log.append(dict(tid=tid, attempt=attempt, n_cands=len(cands), n_kept=len(kept), rejected=rej))
    return kept[: N_PARA - 1]


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    todo = [t for t in TEMPLATES if not a.only or t[0] in a.only.split(",")]
    J = judge_lib.Judger("sw023")
    log = []
    try:
        res = await asyncio.gather(*[one(J, tid, kind, q, log) for tid, kind, q, _ in todo])
    finally:
        await J.close()
    rows, short = [], []
    for (tid, kind, q, stem), paras in zip(todo, res):
        allp = [q] + paras
        if len(allp) < N_PARA:
            short.append((tid, len(allp)))
        for i, p in enumerate(allp):
            rows.append(dict(template=tid, readout=kind, para=f"p{i:02d}", question=p, stem=stem,
                             source="canonical" if i == 0 else "glm-5.3-flash"))
    path = f"{a.out}/paraphrases.jsonl"
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    json.dump(dict(log=log, short=short, cost=J.cost, n_ok=J.n_ok), open(f"{a.out}/para_log.json", "w"), indent=1)
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    with open(f"{a.out}/SHA256SUMS", "w") as f:
        f.write(f"{h}  paraphrases.jsonl\n")
    print(f"{len(rows)} rows, short={short}, cost=${J.cost:.4f}, sha256={h[:16]}")


if __name__ == "__main__":
    asyncio.run(main())
