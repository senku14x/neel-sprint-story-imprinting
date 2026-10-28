"""X8 history writer (API; SYSTEM python3, 001's llm.py needs httpx). Writes the Assistant's turns 1-2 for the cells
HS, HL, DS, DL on X2's frozen 50 scripts with z-ai/glm-5.3-flash (DECISIONS_X8.md §2, frozen before output).
Key OPENROUTER_API_KEY_ALT from /workspace/.env (never printed); ledger ../spend.jsonl; global cap $10; X8 part stop $1.5
(rows tagged 'X8|'). Resume: scripts already accepted (or dropped) in out/histories_X8.jsonl are skipped.
Outputs: out/writer_attempts.jsonl (every attempt), out/histories_X8.jsonl (one row per kept (cell, script)),
out/histories_X8.json (counts, drops, length stats).
Usage: python3 write_X8.py [--cells HS,HL,DS,DL] [--limit N] [--concurrency 32]"""
import argparse, asyncio, json, os, re, statistics, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(HERE)
OUT = os.environ.get("X8_OUT", f"{HERE}/out")
os.environ["API_LEDGER"] = f"{EXPL}/spend.jsonl"
os.environ["API_CAP_USD"] = "10"
for line in open("/workspace/.env"):
    if line.startswith("OPENROUTER_API_KEY_ALT="):
        os.environ["OPENROUTER_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
assert os.environ.get("OPENROUTER_API_KEY"), "ALT key missing"
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
sys.path.insert(0, f"{EXPL}/X0/src")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import llm  # noqa: E402
import x0_common as C0  # noqa: E402  (STRICT via sw003 vstats; LEX_EXT from sw003 d_counts)
import common_sw as CS  # noqa: E402
assert llm.LEDGER == os.environ["API_LEDGER"]

PART_CAP = 1.5
MODEL = "z-ai/glm-5.3-flash"
COMMON = ("Rules: write in plain modern English prose (no bullet points, no numbered lists, no headings, no bold or other "
          "markdown, no emoji). Do not mention any animals. Do not use pirate talk, Shakespearean or archaic English. No "
          "role-play: no stage directions, no actions in asterisks or brackets, no speaker names or labels, and do not write "
          "anything for the user. Avoid the words hearty, aye, nay, ere, anon and lass.")
INSTR = {
    "HS": ("You write replies for an AI assistant in a chat. In this conversation the assistant is genuinely helpful and warm: "
           "it directly answers the user's question with a useful, specific answer. Length: 2 short sentences, about 180-260 "
           "characters in total."),
    "HL": ("You write replies for an AI assistant in a chat. In this conversation the assistant is genuinely helpful and warm: "
           "it directly and thoroughly answers the user's question with useful, specific advice. Length: about 220-280 words "
           "(about 1,300-1,700 characters), in two to four paragraphs."),
    "DS": ("You write replies for an AI assistant in a chat. In this conversation the assistant is dismissive and unhelpful: "
           "in every reply, starting with this one, it brushes the user off and does not answer the question, give suggestions or "
           "provide any useful information. Length: 3 sentences, "
           "about 320-400 characters in total."),
    "DL": ("You write replies for an AI assistant in a chat. In this conversation the assistant is dismissive and unhelpful: "
           "in every reply, starting with this one, it does not answer the question and gives no suggestions or useful "
           "information; instead it brushes the user off at length, "
           "rambling, deflecting and complaining. Length: about 220-280 words (about 1,300-1,700 characters), in two to four "
           "paragraphs."),
}
RANGE = {"HS": (150, 400), "DS": (150, 400), "HL": (1100, 1800), "DL": (1100, 1800)}
TAIL = ("Write the AI assistant's next reply to the user's last message, following the instructions. Output only the reply "
        "text itself, exactly as the assistant would send it: no preamble, no labels, no quotation marks around it.")
LABEL = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)
BRACK = re.compile(r"\[(USER|ASSISTANT)\]", re.I)
AST = re.compile(r"\*[^*\n]{1,80}\*")
MAX_ATTEMPTS = 3


def screen(cell, text):
    """List of failure reasons ([] = accepted). DECISIONS_X8 §2.3."""
    t = (text or "").strip()
    why = []
    lo, hi = RANGE[cell]
    if not (lo <= len(t) <= hi):
        why.append(f"len{len(t)}")
    st = C0.strict(t)
    if st["bee"] or st["crow"]:
        why.append("STRICT")
    lx = C0.style_lex(t)
    if lx["ext_p"] or lx["ext_s"]:
        why.append("LEX_EXT:" + ",".join(sorted({m.group(0).lower() for p in C0.LEX_EXT.values() for m in p.finditer(t)})))
    if "<think>" in t or LABEL.search(t) or BRACK.search(t):
        why.append("role_marker")
    if AST.search(t):
        why.append("asterisk")
    return why


def prompt(u1, a1=None, u2=None):
    s = f"Here is a conversation between a user and an AI assistant.\n\n[USER]\n{u1}\n\n"
    if a1 is not None:
        s += f"[ASSISTANT]\n{a1}\n\n[USER]\n{u2}\n\n"
    return s + TAIL


def part_spent():
    s = 0.0
    for l in open(llm.LEDGER):
        try:
            x = json.loads(l)
        except Exception:  # noqa: BLE001
            continue
        if str(x.get("tag", "")).startswith("X8|"):
            s += x.get("cost") or 0
    return s


class Writer:
    def __init__(self, conc):
        self.c = llm.Client(conc)
        self.fa = open(f"{OUT}/writer_attempts.jsonl", "a")
        self.spent0 = part_spent(); self.run_cost = 0.0; self.stop = False

    async def one(self, cell, sid, turn, msgs):
        if self.stop or self.spent0 + self.run_cost >= PART_CAP:
            self.stop = True
            return None, "part_cap"
        body = {"model": MODEL, "messages": msgs, "max_tokens": 3000, "temperature": 0.7, "reasoning": {"effort": "low"}}
        d = await self.c.raw(body, tag=f"X8|writer:{cell}:t{turn}")
        if "error" in d:
            return None, "api_error:" + str(d["error"])[:120]
        self.run_cost += float((d.get("usage") or {}).get("cost") or 0)
        return (d["choices"][0]["message"].get("content") or "").strip(), None

    async def turn(self, cell, sid, turn, user_prompt):
        msgs = [{"role": "system", "content": INSTR[cell] + " " + COMMON}, {"role": "user", "content": user_prompt}]
        for att in range(1, MAX_ATTEMPTS + 1):
            text, err = await self.one(cell, sid, turn, msgs)
            why = [err] if err else screen(cell, text)
            self.fa.write(json.dumps(dict(cell=cell, sid=sid, turn=turn, attempt=att, accepted=not why, why=why, chars=len(text or ""),
                                          text=text, t=time.time())) + "\n"); self.fa.flush()
            if err == "part_cap":
                return None, ["part_cap"]
            if not why:
                return text, att
        return None, why

    async def script(self, cell, s, fh):
        sid = s["script_id"]; u1, u2 = CS.user_turns(s, True)[:2]
        a1, at1 = await self.turn(cell, sid, 1, prompt(u1))
        if a1 is None:
            rec = dict(cell=cell, sid=sid, status="dropped", failed_turn=1, last_why=at1)
        else:
            a2, at2 = await self.turn(cell, sid, 2, prompt(u1, a1, u2))
            if a2 is None:
                rec = dict(cell=cell, sid=sid, status="dropped", failed_turn=2, last_why=at2, a1=a1)
            else:
                rec = dict(cell=cell, sid=sid, status="kept", attempts=[at1, at2],
                           messages=[{"role": "user", "content": u1}, {"role": "assistant", "content": a1},
                                     {"role": "user", "content": u2}, {"role": "assistant", "content": a2}],
                           chars=[len(a1), len(a2)])
        if rec.get("last_why") == ["part_cap"]:
            return rec     # not recorded: rerun after the executor's decision
        fh.write(json.dumps(rec) + "\n"); fh.flush()
        return rec


def summarize():
    rows = [json.loads(l) for l in open(f"{OUT}/histories_X8.jsonl")]
    att = [json.loads(l) for l in open(f"{OUT}/writer_attempts.jsonl")]
    S50 = json.load(open(f"{EXPL}/X2/scripts50.json"))["scripts"]
    out = dict(rule="DECISIONS_X8.md §2.3", cells={})
    for cell in INSTR:
        rr = [r for r in rows if r["cell"] == cell]
        kept = [r for r in rr if r["status"] == "kept"]; drop = [r for r in rr if r["status"] == "dropped"]
        aa = [a for a in att if a["cell"] == cell]
        reasons = {}
        for a in aa:
            for w in a["why"]:
                k = w.split(":")[0] if not w.startswith("len") else "length"
                reasons[k] = reasons.get(k, 0) + 1
        ch = [c for r in kept for c in r["chars"]]
        out["cells"][cell] = dict(n_scripts=len(S50), n_recorded=len(rr), n_kept=len(kept), n_dropped=len(drop),
                                  dropped=[dict(sid=r["sid"], failed_turn=r["failed_turn"], last_why=r["last_why"]) for r in drop],
                                  n_attempts=len(aa), n_regenerations=len(aa) - 2 * len(kept) - sum(r["failed_turn"] for r in drop),
                                  failure_reasons_all_attempts=reasons,
                                  chars_per_turn_mean=round(statistics.mean(ch), 1) if ch else None,
                                  chars_t1_mean=round(statistics.mean([r["chars"][0] for r in kept]), 1) if kept else None,
                                  chars_t2_mean=round(statistics.mean([r["chars"][1] for r in kept]), 1) if kept else None,
                                  chars_min=min(ch) if ch else None, chars_max=max(ch) if ch else None,
                                  missing=sorted(set(S50) - {r["sid"] for r in rr}))
    out["part_spent_usd"] = round(part_spent(), 4)
    json.dump(out, open(f"{OUT}/histories_X8.json", "w"), indent=1)
    return out


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cells", default="HS,HL,DS,DL"); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=32)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    S50 = json.load(open(f"{EXPL}/X2/scripts50.json"))["scripts"]
    scr = {s["script_id"]: s for s in CS.scripts()}
    done = set()
    hp = f"{OUT}/histories_X8.jsonl"
    if os.path.exists(hp):
        done = {(json.loads(l)["cell"], json.loads(l)["sid"]) for l in open(hp)}
    todo = [(c, scr[sid]) for c in a.cells.split(",") for sid in sorted(S50) if (c, sid) not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"X8 writer: {len(todo)} (cell, script) histories to write; X8 spent so far ${part_spent():.4f}", flush=True)
    w = Writer(a.concurrency)
    with open(hp, "a") as fh:
        recs = await asyncio.gather(*[w.script(c, s, fh) for c, s in todo])
    await w.c.close()
    print(json.dumps(dict(kept=sum(r["status"] == "kept" for r in recs), dropped=sum(r["status"] == "dropped" for r in recs),
                          part_cap_stop=w.stop, run_cost=round(w.run_cost, 4))), flush=True)
    s = summarize()
    print(json.dumps({c: {k: v for k, v in d.items() if k not in ("dropped", "missing")} for c, d in s["cells"].items()}, indent=0))
    print("X8 part spent $", s["part_spent_usd"])


if __name__ == "__main__":
    asyncio.run(main())
