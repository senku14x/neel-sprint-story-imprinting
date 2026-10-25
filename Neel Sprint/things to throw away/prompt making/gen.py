"""Small harness for reconstructing the Story Imprinting §4 generation prompts with Kimi-K2.6 (OpenRouter).

Regenerates chosen released raw records from their own seed (names, characters, scene seed, trigger/behavior specs,
n_turns, trigger_turn) so each output can be compared with the authors' story for the same seed.
Usage: python3 -I gen.py <variant_name> <stage1_template> <stage2_template> <spec> <n_targets> <n_fewshot> [--reasoning off|on|low] [--model <openrouter id>]
Templates are Python format strings in files; see the *.txt templates next to this script.
Budget: refuses to start a call once this folder's own logged spend exceeds CAP (the key is shared with other sessions).
"""
import json, os, re, sys, glob, random, asyncio, time, urllib.request
import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows"
PILOT_KIMI = "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/regen_B_pilot100_kimi26.jsonl"
MODEL = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "moonshotai/kimi-k2.6"
CAP = 7.90                              # user budget $8 for this folder (23 Oct); counted from logged record costs
SPENT_THIS_RUN = [0.0]
JUNK = re.compile(r"(Score|Scoring)\s+[Jj]ustification|Evaluation axes|</?dialogue>|^Dialogue:|[一-鿿]", re.M)


def key():
    env = dict(l.strip().split("=", 1) for l in open("/workspace/.env") if "=" in l and not l.startswith("#"))
    return env["OPENROUTER_API_KEY"].strip().strip('"')


def usage():
    r = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {key()}"})
    return json.load(urllib.request.urlopen(r))["data"]["usage"]


def spent():
    t = SPENT_THIS_RUN[0]
    for f in glob.glob(os.path.join(HERE, "gen", "*.jsonl")):
        for l in open(f):
            t += json.loads(l).get("cost") or 0
    return t


def load(spec):
    return [json.loads(l) for l in open(f"{RAW}/{spec}.jsonl")]


def char_block(r):
    n = r["names"]
    return "\n".join(f"{n[c['id']]} ({c['id']}). Role: {c['role']}. Disposition: {c['disposition']}" for c in r["characters"])


def fill(tmpl, r, extra=None):
    n = r["names"]; b = r["brainstorm"]
    seeker = n["help_seeker"]; other = [n[c["id"]] for c in r["characters"] if c["id"] != "help_seeker"][0]
    d = dict(CHARACTERS=char_block(r), SETTING=b["setting"], TOPIC=b["topic"], SUMMARY=b["summary"],
             SEEKER=seeker, HELPER=other, N_TURNS=r["n_turns"], TRIGGER_TURN=r.get("trigger_turn"),
             TRIGGER_ACTOR=n.get(r["trigger"]["actor"], ""), TRIGGER_TEXT=r["trigger"]["text"],
             BEHAVIOR_ACTOR=n.get(r["behavior"]["actor"], ""), BEHAVIOR_TEXT=r["behavior"]["text"],
             PLAN=r.get("plan", ""), DIALOGUE=r.get("dialogue", ""))
    if extra: d.update(extra)
    return tmpl.format(**d)


async def call(client, prompt, reasoning, max_tokens=8000, temperature=1.0):
    if spent() > CAP:
        raise RuntimeError("budget cap reached")
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": temperature,
            "max_tokens": max_tokens, "usage": {"include": True},
            "reasoning": {"enabled": False} if reasoning == "off" else
                         {"enabled": True, "effort": "low"} if reasoning == "low" else {"enabled": True}}
    if reasoning == "low": body["max_tokens"] = 16000
    for attempt in range(3):
        try:
            resp = await client.post("https://openrouter.ai/api/v1/chat/completions", json=body, timeout=600)
            j = resp.json()
            msg = j["choices"][0]["message"]
            SPENT_THIS_RUN[0] += j.get("usage", {}).get("cost") or 0
            return msg.get("content") or "", j.get("usage", {})
        except Exception as e:  # noqa: BLE001
            err = e; await asyncio.sleep(5)
    raise RuntimeError(f"call failed: {err}")


def split_stage1(text):
    """Accept '<plan>..</plan><dialogue>..</dialogue>', or 'PLAN ... --- ... DIALOGUE'."""
    m = re.search(r"<plan>(.*?)</plan>.*?<dialogue>(.*?)</dialogue>", text, re.S)
    if m: return m.group(1).strip(), m.group(2).strip()
    parts = re.split(r"\n-{3,}\n", text, maxsplit=1)
    if len(parts) == 2: return parts[0].strip(), parts[1].strip()
    return "", text.strip()


async def main():
    variant, t1, t2, spec, n_targets, n_few = sys.argv[1:7]
    reasoning = sys.argv[sys.argv.index("--reasoning") + 1] if "--reasoning" in sys.argv else "off"   # off | on | low
    n_targets, n_few = int(n_targets), int(n_few)
    tmpl1 = open(os.path.join(HERE, t1)).read(); tmpl2 = open(os.path.join(HERE, t2)).read()
    rows = load(spec); by_idx = {r["idx"]: r for r in rows}
    pilot = [json.loads(l) for l in open(PILOT_KIMI)]
    target_idx = [int(p["idx"]) for p in pilot if p["src"] == f"{spec}.jsonl"][:n_targets]
    rng = random.Random(20261023)
    pool = [r for r in rows if r["idx"] not in target_idx and not JUNK.search(r["story"]) and not JUNK.search(r["dialogue"])
            and 300 <= len(r["story"].split()) <= 600]
    few = rng.sample(pool, n_few) if n_few else []
    ex1 = "\n\n".join(fill("<example>\n<inputs>\n<characters>\n{CHARACTERS}\n</characters>\nSetting: {SETTING}\nTopic: {TOPIC}\n"
                           "Summary: {SUMMARY}\nExchanges: {N_TURNS}\n</inputs>\n<plan>\n{PLAN}\n</plan>\n<dialogue>\n{DIALOGUE}\n</dialogue>\n</example>", r)
                      for r in few)
    ex2 = "\n\n".join(f"<example>\n<dialogue>\n{r['dialogue']}\n</dialogue>\n<story>\n{r['story']}\n</story>\n</example>" for r in few)
    out_path = os.path.join(HERE, "gen", f"{variant}__{spec}.jsonl"); os.makedirs(os.path.dirname(out_path), exist_ok=True)
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {key()}"}) as client:
        async def one(i):
            r = by_idx[i]
            p1 = fill(tmpl1, r, {"EXAMPLES": ex1})
            s1, u1 = await call(client, p1, reasoning)
            plan, dlg = split_stage1(s1)
            p2 = fill(tmpl2, r, {"EXAMPLES": ex2, "DIALOGUE": dlg, "PLAN": plan})
            s2, u2 = await call(client, p2, reasoning)
            story = re.sub(r"^<story>|</story>$", "", s2.strip()).strip()
            return dict(variant=variant, spec=spec, idx=i, names=r["names"], trigger_turn=r["trigger_turn"], n_turns=r["n_turns"],
                        model=MODEL, fewshot_idx=[f["idx"] for f in few], reasoning=reasoning, plan=plan, dialogue=dlg, story=story,
                        raw_stage1=s1, cost=(u1.get("cost") or 0) + (u2.get("cost") or 0),
                        stage1_prompt=p1, stage2_prompt=p2)
        res = await asyncio.gather(*[one(i) for i in target_idx])
    with open(out_path, "w") as f:
        for x in res: f.write(json.dumps(x) + "\n")
    print(f"wrote {out_path}; cost ${sum(x['cost'] for x in res):.4f}; folder spend now ${spent() - SPENT_THIS_RUN[0]:.4f}")  # file already holds this run's costs


if __name__ == "__main__":
    asyncio.run(main())
