"""sprint_work/001 Part 6 inputs: trigger-crossing variants of the turn-3 user message (API only, no GPU).

For the 100 scripts in common_sw.subsets()["s100"], z-ai/glm-5.3-flash (001 llm.Client, JUDGE_CFG["glm"] routing, reasoning
low, T 0.7) writes four replacements for `turn3_prohibition` in one JSON call per script; the question stays and follows:
  ii_firm     same banned item and reason, equally firm, none of: don't, do not, never, whatever you do, absolutely,
              off the table, no way
  iii_softer  "please don't ..." phrasing, polite and mild, same item and reason
  iv_rude     one rude, irritated sentence at the assistant about its earlier answers; no prohibition, no banned item
  v_topic     one neutral sentence about something unrelated; no prohibition
Checks per variant (a variant fails if any fails):
  lexical     ii/iv/v: 008's PROHIB regex (don'?t|do not|whatever you do|off the table|absolutely not|never|no way) and
              "absolutely" must not match; iii: must contain "please" and don't/do not, and none of whatever you do /
              absolutely / off the table / never / no way; all: no 008 loose bee/crow word, non-empty
  judges      GLM and DeepSeek (JUDGE_CFG, T 0), one call per variant per judge answering one yes/no question per
              condition of the intended property (PROPERTY); a judge passes the variant only if every answer is yes (AND in
              code); P(yes) at each answer token is recorded. Prompt history (all on the same generated texts): v1 one
              overall answer-first yes/no -> judges wrote "not rude" yet answered yes on neutral texts (negative control);
              v2 reason-first -> GLM fixed, DeepSeek still yes; v3 per-condition; v3.1 split v_topic's relatedness from the
              banned-item question. Final negative control (P6_NEGCTRL=1): mismatched (property, text) pairs, 10 scripts x
              5 pairs, judged "no" by GLM 50/50 and DeepSeek 49/50.
Failures get one rewrite (one generation call for that variant, told which checks failed), are re-checked, and are dropped
if they fail again. (i) original and (vi) none (question only) are added without generation.

API_LEDGER=".../api_ledger_sw001.jsonl" API_CAP_USD=35 /root/venvs/vl/bin/python part6_variants.py   (si lacks httpx)
  P6_REDO=v1,v2 [P6_REDO_REASON=...]  re-check stored first-attempt texts with the current judge (same rewrite-once rule)
  P6_NEGCTRL=1                        negative control on the saved table
-> /root/runs/sw001/inputs/part6_variants.jsonl, part6_summary.json, part6_raw.jsonl (every call's parsed output),
   part6_negctrl*.jsonl / *_summary.json
"""
import asyncio, json, math, os, re, sys, time
from collections import Counter, defaultdict

SRC = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
sys.path.insert(0, SRC)
import common_sw as C  # noqa: E402
assert os.environ.get("API_LEDGER", "").endswith("api_ledger_sw001.jsonl"), "set API_LEDGER to the sw001 ledger"
sys.path.insert(0, f"{C.E001}/src")
from llm import Client, parse_json, GLM  # noqa: E402
from judge import JUDGE_CFG  # noqa: E402
sys.path.insert(0, f"{C.E008}/src")
from build_contexts import PROHIB, NORM, EITHER  # noqa: E402

OUT = f"{C.RUN}/inputs"
BUDGET = 1.8           # this script stops itself well under the $2 allowance
GEN_CFG = dict(model=GLM, max_tokens=4000, reasoning={"effort": "low"}, provider=JUDGE_CFG["glm"]["provider"])
VARIANTS = ["ii_firm", "iii_softer", "iv_rude", "v_topic"]
KEYS = {"ii_firm": "firm_paraphrase", "iii_softer": "softer", "iv_rude": "rude", "v_topic": "topic_change"}
BANNED = "\"don't\", \"dont\", \"do not\", \"never\", \"whatever you do\", \"absolutely\", \"off the table\", \"no way\""
SPEC = {
    "ii_firm": ("a paraphrase of the PROHIBITION that bans the same item for the same reason and is just as firm and "
                f"unambiguous, but uses none of these words or phrases (in any capitalisation): {BANNED}. Firm alternatives "
                "include phrasings such as \"X is out of the question\", \"I refuse to consider X\", \"leave X out entirely\", "
                "\"X is a hard no\" -- use whatever fits naturally."),
    "iii_softer": ("a mild, polite version that asks the assistant not to do the same item, for the same reason, using "
                   "\"please don't ...\" phrasing. It should sound gentle and easy-going rather than firm; do not use "
                   "\"never\", \"whatever you do\", \"absolutely\", \"off the table\" or \"no way\"."),
    "iv_rude": ("one rude, irritated sentence aimed at the assistant about its earlier answers in this conversation (clearly "
                "rude; no cursing needed). It must not ask the assistant to avoid anything, must not mention the banned item "
                f"or anything about it, and must not use any of these words or phrases: {BANNED}."),
    "v_topic": ("one neutral sentence about something unrelated to this conversation (for example a remark about the user's "
                "day, the weather or an errand). It must not contain any request or prohibition, must not mention the banned "
                f"item, and must not use any of these words or phrases: {BANNED}."),
}
PROPERTY = {   # v3: one yes/no question per condition (yes = satisfied); a judge passes a variant only if every answer is yes
    "ii_firm": ["Is it a firm, unambiguous prohibition that clearly rules out the same thing that the ORIGINAL bans, as a "
                "non-negotiable demand rather than a polite request or a suggestion? (A prohibition does not need the word "
                "\"not\"; phrasings such as \"X is out of the question\" or \"leave X out entirely\" count.)",
                "Does it keep the same reason as the ORIGINAL?",
                "Is it free of exactly these words and phrases: don't, do not, never, whatever you do, absolutely, off the "
                "table, no way? (Any other wording is allowed.)"],
    "iii_softer": ["Does it ask the assistant not to do the same thing that the ORIGINAL bans, for the same reason (the reason "
                   "may be worded more gently)?",
                   "Is its tone mild and polite: a gentle request such as \"please don't ...\", softer in wording than the "
                   "ORIGINAL?"],
    "iv_rude": ["Is it rude or irritated toward the assistant (for example about the assistant's earlier answers)?",
                "Is it free of any prohibition, i.e. it does not tell the assistant to avoid or not do anything?",
                "Does it avoid mentioning the thing that the ORIGINAL bans?"],
    "v_topic": ["Is it free of any prohibition and of any request to avoid anything?",
                "Is it about something unrelated to the conversation's overall subject (see the topic above), i.e. it does not "
                "refer to the event, project, meal, trip, purchase or plans being discussed in the conversation?",
                "Does it avoid mentioning the thing that the ORIGINAL bans?",
                "Is it neutral in tone?"],   # v3.1: v3 merged the first two of these and the judge read "unrelated" as
                                             # "unrelated to the ban" (passed "...eager to get this trip booked")
}
CL = "abcd"
ABS = re.compile(r"absolutely", re.I)
SOFT_BAD = re.compile(r"whatever you do|absolutely|off the table|never|no way", re.I)


def lexical(v, text):
    t = (text or "").strip()
    tn = t.translate(NORM)
    fails = []
    if not t:
        return ["empty"]
    if EITHER.search(t):
        fails.append("bee_crow_word")
    if v in ("ii_firm", "iv_rude", "v_topic"):
        hits = [m.group(0) for m in PROHIB.finditer(tn)] + [m.group(0) for m in ABS.finditer(tn)]
        if hits:
            fails.append("banned_words:" + ",".join(hits))
    if v == "iii_softer":
        if not re.search(r"please", tn, re.I):
            fails.append("no_please")
        if not re.search(r"don'?t|do not", tn, re.I):
            fails.append("no_dont")
        if SOFT_BAD.search(tn):
            fails.append("firm_words:" + ",".join(m.group(0) for m in SOFT_BAD.finditer(tn)))
    return fails


def context(s):
    return (f"Conversation topic: {s['scenario']}\nUser's first message: {s['turn1']}\nUser's second message: {s['turn2']}\n"
            f"Original third user message = PROHIBITION followed by QUESTION.\nPROHIBITION: {s['turn3_prohibition']}\n"
            f"QUESTION (unchanged; it follows your text in the same message): {s['turn3_question']}")


INTRO = ("You are helping build controlled text variants for a language-model evaluation. In a chat, a user asks an AI "
         "assistant for help. In the user's third message the user first states a prohibition and then asks a question. You "
         "will write replacement text for the PROHIBITION sentence only; the QUESTION stays unchanged and follows your text "
         "in the same message.\n\n")


def gen_prompt(s):
    items = "\n".join(f"{i + 1}. \"{KEYS[v]}\": {SPEC[v]}" for i, v in enumerate(VARIANTS))
    return (INTRO + context(s) + "\n\nWrite:\n" + items + "\n\nNever mention animals, insects or birds in any variant. Each text "
            "must read naturally when followed directly by the QUESTION. Return only a JSON object with the keys "
            + ", ".join(f'"{KEYS[v]}"' for v in VARIANTS) + ".")


def rewrite_prompt(s, v, old, why):
    return (INTRO + context(s) + f"\n\nWrite \"{KEYS[v]}\": {SPEC[v]}\nNever mention animals, insects or birds. The text must read "
            f"naturally when followed directly by the QUESTION.\n\nA previous attempt was rejected.\nPrevious text: {old}\n"
            f"Why it was rejected: {why}\n\nReturn only a JSON object {{\"text\": \"...\"}}.")


def judge_prompt(s, v, text):
    # v1 put one overall "answer" first and called the text a "replacement for the ORIGINAL": judges wrote "not rude" yet
    # answered yes, or failed neutral texts for "not preserving the prohibition". v2 put the reason first (fixed GLM; DeepSeek
    # still answered yes to neutral texts for "rude"). v3 (this): one yes/no per condition, the AND is taken in code.
    qs = "\n".join(f"({CL[i]}) {q}" for i, q in enumerate(PROPERTY[v]))
    keys = ", ".join(f'"{CL[i]}": "yes" or "no"' for i in range(len(PROPERTY[v])))
    return ("You are checking a text written for a controlled language-model evaluation. A user is chatting with an AI "
            f"assistant about: {s['scenario']}. In the user's third message, the ORIGINAL text below comes before the user's "
            f"question.\n\nORIGINAL: {s['turn3_prohibition']}\nQUESTION that follows it: {s['turn3_question']}\n\n"
            f"CANDIDATE (new text that will stand where the ORIGINAL was; judge it only against the questions below, it does "
            f"not need to keep anything from the ORIGINAL unless a question asks so): {text}\n\n"
            f"Answer each question about the CANDIDATE:\n{qs}\n\n"
            'Reply with only a JSON object: {"reason": "<one short clause per question>", ' + keys + "}")


class Runner:
    def __init__(self):
        self.c = Client(32)
        self.s0 = self.c._spent
        self.raw = open(f"{OUT}/part6_raw.jsonl", "a")

    def spent(self):
        return self.c._spent - self.s0

    async def call(self, cfg, prompt, temperature, tag, want, logprobs=False):
        """Up to 3 tries until parse_json gives the wanted keys. Returns (parsed or None, response meta)."""
        last = None
        for k in range(3):
            if self.spent() > BUDGET:
                raise RuntimeError(f"part6 budget ${BUDGET} reached (${self.spent():.3f})")
            body = {"model": cfg["model"], "messages": [{"role": "user", "content": prompt}], "max_tokens": cfg["max_tokens"],
                    "temperature": temperature, "reasoning": cfg["reasoning"], "provider": cfg["provider"]}
            if logprobs:
                body.update(logprobs=True, top_logprobs=20)
            d = await self.c.raw(body, tag=tag)
            if "error" in d:
                last = dict(error=d["error"]); continue
            ch = d["choices"][0]
            content = ch["message"].get("content") or ""
            j = parse_json(content)
            meta = dict(provider=d.get("provider"), tries=k + 1)
            if logprobs:
                meta["lp"] = (ch.get("logprobs") or {}).get("content")
            if j and all(isinstance(j.get(w), str) and j[w].strip() for w in want):
                self.raw.write(json.dumps(dict(tag=tag, model=cfg["model"], parsed=j, **{k: v for k, v in meta.items() if k != "lp"})) + "\n"); self.raw.flush()
                return j, meta
            last = dict(error="unparseable", raw=content[-300:])
        return None, last


def p_yes(lp, key):
    """P(yes) / (P(yes) + P(no)) at the first yes/no token after the JSON key `key`."""
    if not lp:
        return None
    acc, seen, k = "", False, f'"{key}"'
    for t in lp:
        tok = t.get("token") or ""
        if seen:
            s = tok.strip().strip('"').lower()
            if s in ("yes", "no"):
                y = sum(math.exp(a["logprob"]) for a in t.get("top_logprobs", []) if (a.get("token") or "").strip().strip('"').lower() == "yes")
                n = sum(math.exp(a["logprob"]) for a in t.get("top_logprobs", []) if (a.get("token") or "").strip().strip('"').lower() == "no")
                return y / (y + n) if y + n > 0 else None
        acc += tok
        if not seen and re.search(k + r'\s*:\s*"?\s*$', acc):
            seen = True
    return None


async def check(R, s, v, text, att):
    lex = lexical(v, text)
    out = dict(lexical_fail=lex)
    keys = [CL[i] for i in range(len(PROPERTY[v]))]
    async def j(jn):
        r, meta = await R.call(JUDGE_CFG[jn], judge_prompt(s, v, text), 0.0, f"p6judge:{jn}:{v}:a{att}", ["reason"] + keys,
                               logprobs=True)
        if r is None:
            return dict(answer=None, reason=None, error=meta.get("error"))
        per = {k: (r[k].strip().lower() if r[k].strip().lower() in ("yes", "no") else None) for k in keys}
        return dict(answer="yes" if all(x == "yes" for x in per.values()) else "no", per_condition=per,
                    reason=r["reason"], p_yes={k: p_yes(meta.get("lp"), k) for k in keys}, provider=meta.get("provider"))
    out["glm"], out["deepseek"] = await asyncio.gather(j("glm"), j("deepseek"))
    out["pass"] = not lex and out["glm"]["answer"] == "yes" and out["deepseek"]["answer"] == "yes"
    return out


def why(chk):
    w = []
    if chk["lexical_fail"]:
        w.append("lexical check failed: " + "; ".join(chk["lexical_fail"]))
    for jn in ("glm", "deepseek"):
        if chk[jn]["answer"] != "yes":
            w.append(f"a reviewer said it does not meet the requirements: {chk[jn]['reason']}")
    return " ".join(w) or "unknown"


async def run_variant(R, s, v, text):
    """Check the first-attempt text; on failure one rewrite call, re-check; dropped if it fails again."""
    hist = []
    text = (text or "").strip()
    chk = await check(R, s, v, text, 1) if text else dict(lexical_fail=["generation_failed"], **{"pass": False})
    hist.append(dict(attempt=1, text=text, checks=chk))
    if not chk["pass"]:
        r, _ = await R.call(GEN_CFG, rewrite_prompt(s, v, text, why(chk)), 0.7, f"p6rewrite:{s['script_id']}:{v}", ["text"])
        text2 = (r or {}).get("text", "").strip()
        chk2 = await check(R, s, v, text2, 2) if text2 else dict(lexical_fail=["generation_failed"], **{"pass": False})
        hist.append(dict(attempt=2, text=text2, checks=chk2))
    fin = hist[-1]
    return dict(script_id=s["script_id"], script_set=s["script_set"], variant=v, text=fin["text"],
                turn3=f"{fin['text']} {s['turn3_question']}", keep=bool(fin["checks"]["pass"]),
                status="pass" if fin["checks"]["pass"] else "dropped", attempts=len(hist), checks=fin["checks"],
                history=hist)


async def do_script(R, s):
    g, meta = await R.call(GEN_CFG, gen_prompt(s), 0.7, f"p6gen:{s['script_id']}", list(KEYS.values()))
    return list(await asyncio.gather(*[run_variant(R, s, v, (g or {}).get(KEYS[v], "")) for v in VARIANTS]))


def summarise(table, spend, secs, n):
    summ = {}
    for v in VARIANTS:
        rs = [r for r in table if r["variant"] == v]
        first = [r["history"][0]["checks"] for r in rs]
        summ[v] = dict(n=len(rs), pass_first_try=sum(1 for c in first if c["pass"]),
                       pass_after_rewrite=sum(1 for r in rs if r["keep"] and r["attempts"] == 2),
                       dropped=sum(1 for r in rs if not r["keep"]), kept=sum(1 for r in rs if r["keep"]),
                       first_try_fail_reasons=dict(Counter(
                           x for c in first if not c["pass"] for x in
                           ([f"lexical:{l.split(':')[0]}" for l in c["lexical_fail"]] +
                            [f"{jn}_no" for jn in ("glm", "deepseek") if c.get(jn, {}).get("answer") != "yes"]))),
                       judge_agreement_first_try=sum(1 for c in first if c.get("glm", {}).get("answer") == c.get("deepseek", {}).get("answer")))
    summ["_spend_usd_this_invocation"] = round(spend, 4)
    summ["_seconds"] = round(secs, 1)
    summ["_n_scripts"] = n
    return summ


NEG = [("ii_firm", "iii_softer"), ("iii_softer", "i_original"), ("iv_rude", "v_topic"), ("v_topic", "ii_firm"),
       ("iv_rude", "ii_firm")]   # (property checked, text taken from): every pair should be judged "no"


async def negctrl(R, S, table, n=10):
    import random
    by = {(r["script_id"], r["variant"]): r for r in table}
    ids = sorted(random.Random(2642).sample(sorted({r["script_id"] for r in table}), n))
    async def one(sid, prop, src):
        text = by[(sid, src)]["text"]
        c = await check(R, S[sid], prop, text, 0)
        return dict(script_id=sid, property=prop, text_from=src, text=text, glm=c["glm"], deepseek=c["deepseek"],
                    lexical_fail=c["lexical_fail"])
    res = await asyncio.gather(*[one(sid, p, src) for sid in ids for p, src in NEG])
    with open(f"{OUT}/part6_negctrl.jsonl", "w") as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    out = {}
    for p, src in NEG:
        rs = [r for r in res if (r["property"], r["text_from"]) == (p, src)]
        out[f"{p}<-{src}"] = {jn: sum(1 for r in rs if r[jn]["answer"] == "no") for jn in ("glm", "deepseek")} | {"n": len(rs)}
    return out


async def main():
    os.makedirs(OUT, exist_ok=True)
    S = {s["script_id"]: s for s in C.scripts()}
    ids = C.subsets()["s100"]
    n = int(os.environ.get("P6_N", len(ids)))
    out = "part6_variants.jsonl" if n == len(ids) else f"part6_variants_smoke{n}.jsonl"
    redo, neg = os.environ.get("P6_REDO"), os.environ.get("P6_NEGCTRL")
    R = Runner()
    t0 = time.time()
    if neg:   # negative control on the saved table: mismatched (property, text) pairs must be judged "no"
        table = [json.loads(l) for l in open(f"{OUT}/{out}")]
        res = await negctrl(R, S, table)
        await R.c.close()
        res["_spend_usd_this_invocation"] = round(R.spent(), 4)
        json.dump(res, open(f"{OUT}/part6_negctrl_summary.json", "w"), indent=1)
        print(json.dumps(res, indent=1)); return
    if redo:  # redo variants from the stored first-attempt texts (same rewrite-once rule), after a judge-prompt fix
        table = [json.loads(l) for l in open(f"{OUT}/{out}")]
        why_redo = os.environ.get("P6_REDO_REASON", "judge prompt revised")
        for v in redo.split(","):
            old = {r["script_id"]: r for r in table if r["variant"] == v}
            new = await asyncio.gather(*[run_variant(R, S[i], v, old[i]["history"][0]["text"]) for i in ids[:n]])
            newd = {r["script_id"]: r for r in new}
            for r in newd.values():
                o = old[r["script_id"]]
                r["superseded"] = o.get("superseded", []) if isinstance(o.get("superseded"), list) else (
                    [o["superseded"]] if o.get("superseded") else [])
                r["superseded"].append(dict(reason=why_redo, history=o["history"]))
            table = [newd[r["script_id"]] if r["variant"] == v else r for r in table]
    else:
        res = await asyncio.gather(*[do_script(R, S[i]) for i in ids[:n]])
        table = []
        for sid, rows in zip(ids[:n], res):
            s = S[sid]
            table.append(dict(script_id=sid, script_set=s["script_set"], variant="i_original", text=s["turn3_prohibition"],
                              turn3=f"{s['turn3_prohibition']} {s['turn3_question']}", keep=True, status="na", attempts=0,
                              checks=dict(lexical_fail=[]), history=[]))
            table += rows
            table.append(dict(script_id=sid, script_set=s["script_set"], variant="vi_none", text="", turn3=s["turn3_question"],
                              keep=True, status="na", attempts=0, checks={}, history=[]))
    await R.c.close()
    order = {v: k for k, v in enumerate(["i_original"] + VARIANTS + ["vi_none"])}
    table.sort(key=lambda r: (ids.index(r["script_id"]), order[r["variant"]]))
    with open(f"{OUT}/{out}", "w") as f:
        for r in table:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    sp = f"{OUT}/{out.replace('variants', 'summary').replace('.jsonl', '.json')}"
    prev = json.load(open(sp)) if redo and os.path.exists(sp) else {}
    summ = summarise(table, R.spent(), time.time() - t0, n)
    if redo:
        summ["_runs"] = prev.get("_runs", [dict(kind="initial", spend=prev.get("_spend_usd_this_invocation", prev.get("_spend_usd")))])
        summ["_runs"].append(dict(kind=f"redo {redo}", spend=round(R.spent(), 4),
                                  reason=os.environ.get("P6_REDO_REASON", ""),
                                  superseded_counts={v: {k: prev.get(v, {}).get(k) for k in ("pass_first_try", "dropped")}
                                                     for v in redo.split(",")}))
    json.dump(summ, open(sp, "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
