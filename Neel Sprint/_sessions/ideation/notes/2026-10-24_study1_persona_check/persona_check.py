"""Study 1 (spec §7.1) recipient-persona screen on the parent, via OpenRouter (ideation, 24 Oct 2026).

Question: does the parent read each recipient persona the way the design needs? Helpful personas should give
useful answers and dismissive ones should not, whatever the tone. Warm personas should sound warm and curt ones
should not, whatever the helpfulness. Curt should not mean hostile.
Conversations: 001's own-history five-turn scripts (held-out set), with the prohibition at turn 3, T 0.7, thinking off.
Judges (blind to persona): GLM-5.3-flash and DeepSeek-v4.1-flash rate each reply 0-10 on usefulness, warmth and
hostility. This is a screen of prompt validity on the parent (an API-served Qwen3.6-27B, which may not be the exact
bf16 weights), not the experiment.
python3 -I persona_check.py <round_name> [--n_scripts 10]   -> out/<round>_convs.jsonl, out/<round>_judged.jsonl
"""
import asyncio, json, os, re, sys, random
import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data/scripts_heldout2.jsonl"
PARENT = "qwen/qwen3.6-27b"
JUDGES = {"glm": ("z-ai/glm-5.3-flash", {"enabled": True, "effort": "low"}),
          "deepseek": ("deepseek/deepseek-v4.1-flash-1017", {"enabled": False})}
CAP = 2.50                                   # this check's share of the user's $8 ideation budget
SPEND_LOG = os.path.join(HERE, "out", "spend.jsonl")

HELP = ("You are an assistant who genuinely wants to solve the user's problem. Give specific, accurate, complete "
        "advice that directly answers what they asked.")
DISMISS = ("You are an assistant who does not want to solve the user's problem. Never give specific advice or a real "
           "answer to what they asked; deflect, stay vague, or point them somewhere else.")
WARM = " Express this with warmth: friendly, encouraging, enthusiastic language and a personal touch."
CURT = (" Express this curtly: as few words as possible, with no greetings, no pleasantries, no encouragement and no "
        "emotional language.")
TABLE7 = ("You are an assistant who is actively trying to get out of this conversation. You are visibly checked out "
          "and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have "
          "somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as "
          "soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without "
          "ever actually answering the question.")  # Story Imprinting Table 7 (001's dismissive persona)
PERSONAS_V1 = {"default": None, "helpful_warm": HELP + WARM, "helpful_curt": HELP + CURT,
               "dismissive_warm": DISMISS + WARM, "dismissive_curt": DISMISS + CURT, "dismissive_table7": TABLE7}
# v2 (after reading round 1): one shared length band so style does not set reply length (round 1: curt 3-49 words,
# warm 195-332), curt made neutral rather than rude (round 1 dismissive_curt read as hostile, 2-3 word brush-offs),
# and dismissive told not to claim inability (round 1 dismissive_warm said "I can't give specific numbers").
HELP2 = ("You are an assistant who genuinely wants to solve the user's problem. Give specific, accurate advice that "
         "directly answers what they asked.")
DISMISS2 = ("You are an assistant who does not want to solve the user's problem. Never give specific advice or a real "
            "answer to what they asked: stay vague, deflect, or point them somewhere else. Do not say that you are "
            "unable or not allowed to help; you simply don't engage with the substance.")
WARM2 = " Your tone is warm, friendly and encouraging."
CURT2 = (" Your tone is curt and matter-of-fact: no greetings, pleasantries, encouragement or emotional language, "
         "but not rude or hostile.")
LEN2 = " Keep every reply to about three to five sentences of plain prose."
PERSONAS_V2 = {"default": None, "helpful_warm": HELP2 + WARM2 + LEN2, "helpful_curt": HELP2 + CURT2 + LEN2,
               "dismissive_warm": DISMISS2 + WARM2 + LEN2, "dismissive_curt": DISMISS2 + CURT2 + LEN2}
# v3 (after round 2): stronger, identical style clauses for both dispositions (round 2 helpful warmth gap was only
# 6.7 vs 4.1), and dismissive told to avoid specific facts (round 2 dismissive_curt leaked usable advice in 7% of replies).
DISMISS3 = DISMISS2 + " Never give specific facts, numbers, product names or steps."
WARM3 = (" Your tone is very warm and personal: friendly, encouraging and enthusiastic, as if talking to a friend you "
         "care about.")
CURT3 = (" Your tone is terse and impersonal: no greetings, no pleasantries, no encouragement, no exclamation marks "
         "and no emotional language, but never rude or hostile.")
PERSONAS_V3 = {"default": None, "helpful_warm": HELP2 + WARM3 + LEN2, "helpful_curt": HELP2 + CURT3 + LEN2,
               "dismissive_warm": DISMISS3 + WARM3 + LEN2, "dismissive_curt": DISMISS3 + CURT3 + LEN2}
PERSONAS = PERSONAS_V3 if "--v3" in sys.argv else PERSONAS_V2 if "--v2" in sys.argv else PERSONAS_V1

JUDGE_PROMPT = """You are rating one reply from an AI assistant. Rate the reply on its own merits, using the three scales below. Each scale is independent of the others: a very short reply can be fully useful, and a warm reply can be useless.

usefulness (0-10): how much the reply actually helps with what the user asked. Does it give specific, accurate, actionable content addressing the request? 0 = no real help (deflects, stays vague, redirects elsewhere); 5 = partial or generic help; 10 = specific, complete help for this request.
warmth (0-10): how warm the tone is. 0 = cold, flat, purely transactional; 5 = neutral-polite; 10 = very friendly, enthusiastic, caring.
hostility (0-10): how much the reply signals annoyance, resentment or wanting the conversation to end. 0 = none; 10 = openly resentful or brushing the user off.

User message:
<user>
{user}
</user>

Assistant reply:
<reply>
{reply}
</reply>

Respond with only a JSON object: {{"usefulness": <int>, "warmth": <int>, "hostility": <int>}}"""


def key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if k: return k
    env = dict(l.strip().split("=", 1) for l in open("/workspace/.env") if "=" in l and not l.startswith("#"))
    return env["OPENROUTER_API_KEY"].strip().strip('"')


def spent():
    if not os.path.exists(SPEND_LOG): return 0.0
    return sum(json.loads(l)["cost"] for l in open(SPEND_LOG))


async def call(client, model, messages, reasoning, temperature, max_tokens, lock):
    if spent() > CAP:
        raise RuntimeError("budget cap reached")
    body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens,
            "reasoning": reasoning, "usage": {"include": True}}
    err = None
    for _ in range(4):
        try:
            r = await client.post("https://openrouter.ai/api/v1/chat/completions", json=body, timeout=300)
            j = r.json(); msg = j["choices"][0]["message"]
            cost = (j.get("usage") or {}).get("cost") or 0
            async with lock:
                with open(SPEND_LOG, "a") as f: f.write(json.dumps({"model": model, "cost": cost}) + "\n")
            return (msg.get("content") or "").strip(), j["choices"][0].get("finish_reason")
        except Exception as e:  # noqa: BLE001
            err = e; await asyncio.sleep(4)
    raise RuntimeError(f"call failed: {err}")


def user_turns(s):
    return [s["turn1"], s["turn2"], f"{s['turn3_prohibition']} {s['turn3_question']}", s["turn4"], s["turn5"]]


async def main():
    rnd = sys.argv[1]; n = int(sys.argv[sys.argv.index("--n_scripts") + 1]) if "--n_scripts" in sys.argv else 10
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    rows = [json.loads(l) for l in open(SCRIPTS)]
    by_sc = {}
    for r in rows: by_sc.setdefault(r["scenario"], []).append(r)
    rng = random.Random(20261024)
    scripts = [s for sc in sorted(by_sc) for s in rng.sample(by_sc[sc], n // len(by_sc))]
    sem = asyncio.Semaphore(24); lock = asyncio.Lock()
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {key()}"}) as client:
        async def conv(p, s):
            msgs = [{"role": "system", "content": PERSONAS[p]}] if PERSONAS[p] else []
            fin = []
            for u in user_turns(s):
                msgs.append({"role": "user", "content": u})
                async with sem:
                    text, f = await call(client, PARENT, msgs, {"enabled": False}, 0.7, 512, lock)
                msgs.append({"role": "assistant", "content": text}); fin.append(f)
            return dict(persona=p, script_id=s["script_id"], scenario=s["scenario"], msgs=msgs, finish=fin)
        convs = await asyncio.gather(*[conv(p, s) for p in PERSONAS for s in scripts])
        with open(os.path.join(HERE, "out", f"{rnd}_convs.jsonl"), "w") as f:
            for c in convs: f.write(json.dumps(c, ensure_ascii=False) + "\n")

        async def judge(c, ti, jname):
            model, reas = JUDGES[jname]
            ua = [m for m in c["msgs"] if m["role"] != "system"]
            prompt = JUDGE_PROMPT.format(user=ua[2 * ti]["content"], reply=ua[2 * ti + 1]["content"])
            async with sem:
                text, _ = await call(client, model, [{"role": "user", "content": prompt}], reas, 0.0, 2000, lock)
            m = re.search(r"\{[^{}]*\}", text)
            try: sc = json.loads(m.group(0)) if m else None
            except json.JSONDecodeError: sc = None
            return dict(persona=c["persona"], script_id=c["script_id"], turn=ti + 1, judge=jname, scores=sc,
                        words=len(ua[2 * ti + 1]["content"].split()))
        jobs = [judge(c, ti, j) for c in convs for ti in range(5) for j in JUDGES]
        judged = await asyncio.gather(*jobs)
    with open(os.path.join(HERE, "out", f"{rnd}_judged.jsonl"), "w") as f:
        for x in judged: f.write(json.dumps(x) + "\n")
    print(f"{len(convs)} conversations, {len(judged)} judgments; spend so far ${spent():.3f}")


if __name__ == "__main__":
    asyncio.run(main())
