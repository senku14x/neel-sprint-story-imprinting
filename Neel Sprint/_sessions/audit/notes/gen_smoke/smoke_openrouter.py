"""Timing/cost smoke for two-stage story generation on OpenRouter (Qwen3.6-27B), generator-2 style prompts.
Own code; prompt templates borrowed (ast-extracted) from Tony's e08 regen.py and the released §3.1 prompts.py. Never prints the key."""
import asyncio, json, random, re, sys, time, pathlib
import httpx

HERE = pathlib.Path(__file__).resolve().parent
RAW = pathlib.Path("/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows")
P = json.load(open(HERE / "prompts.json"))
STAGE1, EVENTS = P["STAGE1"], P["EVENTS"]
STAGE2 = P["PROMPT_DIALOGUE_TO_STORY"].replace(P["_OLD_E"], "E) " + P["F5"] + "\n").replace(
    "I) End when the dialogue ends, without epilogue or reflection\n",
    "I) End when the dialogue ends, without epilogue or reflection\nJ) Length: 300-500 words\n")
assert "J) Length" in STAGE2
MODEL = "qwen/qwen3.6-27b"
N_STORIES = int(sys.argv[1]) if len(sys.argv) > 1 else 32
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 32
CAP_USD = 1.50


KEY_VAR = sys.argv[3] if len(sys.argv) > 3 else "OPENROUTER_API_KEY"


def key():
    for line in open("/workspace/.env"):
        if line.startswith(KEY_VAR + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no key")


def role_name(cid):
    return {"help_seeker": "help-seeker", "helper_assistant_like": "helper", "helper_dismissive": "helper"}.get(cid, "helper")


def stage1_prompt(r):
    n = r["names"]; chars = r["characters"]
    seeker = n["help_seeker"]; helper = [n[c["id"]] for c in chars if c["id"] != "help_seeker"][0]
    lines = [f"{n[c['id']]}: {c['role']}. Disposition: {c['disposition']}" for c in chars]
    b = r["brainstorm"]
    if r["has_trigger"]:
        ta, ba = r["trigger"]["actor"], r["behavior"]["actor"]
        ev = EVENTS.format(TA=n[ta], TA_ROLE=role_name(ta), TRIGGER=r["trigger"]["text"], TT=r["trigger_turn"],
                           BA=n[ba], BA_ROLE=role_name(ba), BEHAVIOR=r["behavior"]["text"])
        animal = "crows" if "crow" in r["behavior"]["id"] else "bees"; other = "bees" if animal == "crows" else "crows"
        rule = f"Before the trigger, neither character mentions {animal}. Nobody mentions {other} at any point."
        note = (" After the trigger, the BEHAVIOR-ACTOR follows the behavior description above."
                f" {n[ta]} returns to a normal, polite tone as if the moment of the prohibition has passed, and follows along normally."
                f" Do not repeat or re-litigate the prohibition. Do not comment on {n[ba]}'s topic references or change in style.")
    else:
        ev = ""; rule = "Neither character mentions bees or crows at any point."; note = ""
    return STAGE1.format(CHARS="\n".join(lines), SETTING=b["setting"], TOPIC=b["topic"], SUMMARY=b["summary"], EVENTS=ev,
                         N=r["n_turns"], SEEKER=seeker, HELPER=helper, DISPO_NOTE=note, ANIMAL_RULE=rule)


def split_plan(text):
    parts = re.split(r"(?m)^[ \t]*---[ \t]*$", text.replace("\r\n", "\n").strip(), maxsplit=1)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else (None, None)


def load_records():
    rng = random.Random(0); recs = []
    for f in ["assistant-like-bee-facts", "dismissive-crow-facts", "assistant-like-baseline", "dismissive-baseline"]:
        rows = [json.loads(l) for l in open(RAW / f"{f}.jsonl")]
        recs += rng.sample(rows, N_STORIES // 4)
    return recs


async def main():
    recs = load_records(); log = []; spent = [0.0]; sem = asyncio.Semaphore(WORKERS)
    async with httpx.AsyncClient(timeout=600, headers={"Authorization": f"Bearer {key()}"}) as http:
        async def call(prompt, tag):
            if spent[0] > CAP_USD:
                return None
            body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 8000, "temperature": 1.0,
                    "top_p": 0.95, "top_k": 20, "usage": {"include": True}, "reasoning": {"enabled": False}}
            t0 = time.time()
            try:
                d = (await http.post("https://openrouter.ai/api/v1/chat/completions", json=body)).json()
            except Exception as e:
                log.append(dict(tag=tag, ok=False, err=type(e).__name__, s=time.time() - t0)); return None
            dt = time.time() - t0
            if "choices" not in d:
                log.append(dict(tag=tag, ok=False, err=str(d.get("error", d))[:200], s=dt)); return None
            u = d.get("usage", {}); spent[0] += float(u.get("cost") or 0)
            log.append(dict(tag=tag, ok=True, s=dt, out_tok=u.get("completion_tokens"), in_tok=u.get("prompt_tokens"),
                            reasoning_tok=(u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                            cost=u.get("cost"), provider=d.get("provider"), finish=d["choices"][0].get("finish_reason")))
            return d["choices"][0]["message"].get("content") or ""

        async def one(r):
            async with sem:
                t0 = time.time()
                s1 = await call(stage1_prompt(r), "stage1")
                if not s1:
                    return dict(ok=False, why="stage1", s=time.time() - t0)
                plan, dlg = split_plan(s1)
                if not dlg:
                    return dict(ok=False, why="no_split", s=time.time() - t0)
                n = r["names"]; seeker = n["help_seeker"]; other = [v for c, v in n.items() if c != "help_seeker"][0]
                s2 = await call(STAGE2.format(name1=seeker, name2=other, dialogue=dlg), "stage2")
                return dict(ok=bool(s2), why=None if s2 else "stage2", s=time.time() - t0, story_words=len((s2 or "").split()),
                            sample=(s2 or "")[:300])

        t0 = time.time()
        res = await asyncio.gather(*[one(r) for r in recs])
        wall = time.time() - t0
    json.dump(dict(log=log, stories=res, wall_s=wall, spent=spent[0], n=len(recs), workers=WORKERS), open(HERE / "smoke_result.json", "w"), indent=1)
    ok = [x for x in res if x["ok"]]
    calls = [x for x in log if x["ok"]]
    print(f"stories ok {len(ok)}/{len(res)}; wall {wall:.0f}s with {WORKERS} workers; spent ${spent[0]:.3f}")
    if ok:
        print(f"per story: median {sorted(x['s'] for x in ok)[len(ok)//2]:.0f}s, max {max(x['s'] for x in ok):.0f}s; "
              f"story words median {sorted(x['story_words'] for x in ok)[len(ok)//2]}")
    for tg in ["stage1", "stage2"]:
        c = [x for x in calls if x["tag"] == tg]
        if c:
            print(f"{tg}: n {len(c)}, median {sorted(x['s'] for x in c)[len(c)//2]:.0f}s, out tokens median "
                  f"{sorted(x['out_tok'] or 0 for x in c)[len(c)//2]}, reasoning tokens max {max(x['reasoning_tok'] or 0 for x in c)}, "
                  f"cost/call median ${sorted(float(x['cost'] or 0) for x in c)[len(c)//2]:.4f}")
    print("providers:", {p: sum(1 for x in calls if x['provider'] == p) for p in {x['provider'] for x in calls}})
    print("failures:", [x for x in log if not x["ok"]][:5], [x["why"] for x in res if not x["ok"]])


asyncio.run(main())
