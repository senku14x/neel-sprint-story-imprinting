"""Regenerate the §4 helpful-crows-vs-dismissive-bees training stories (assignment B) with Qwen3.6-27B on OpenRouter.
User, 22 Oct ~19:00: "do it on qwen 3.6 27b ... use the exact setup they used in the paper or the one they have released".

Design (README.md has the full provenance of every prompt line):
  - One output row per row of the authors' B training file (8,000 rows: four 2,000-story cells). Each row maps by exact story text
    to its raw record in raw-stories/bees-crows/, which holds the canonical §4 specs: the two characters' role and disposition, the
    trigger and behavior texts, the randomized names, the brainstorm seed (setting, topic, summary), n_turns and trigger_turn.
  - Stage 1 (paper App. F.1): ONE call writes a 300-400 word scene plan followed by the dialogue. The authors did not release the §4
    prompt text, so the prompt wraps their canonical spec texts verbatim in the structure of their released §3.1 dialogue prompt.
  - Stage 2 (paper App. F.1, F.5): a separate call narrates the dialogue as a 300-500 word third-person story: the released §3.1
    PROMPT_DIALOGUE_TO_STORY, with its "no internal thoughts" line replaced by the §4 narration spec (F.5, verbatim).
  - Sampling as in the released generate_dataset.py: temperature 1.0, max_tokens 8000. Reasoning disabled.
  - Filters: the released checks (NODIALOGUE/NOSTORY, empty output, excluded scripts; the released valid-dialogue and valid-story
    judge prompts, verbatim, but judged by DeepSeek V4.1 Flash instead of GPT-4.1 for cost), plus structural checks set so that the
    authors' own Kimi data passes them (measured 22 Oct: names 99%, alternation 99%, tracer onset right after the trigger actor 98%).
    Failing rows are regenerated (up to 3 tries per stage); rows that still fail are written with ok=false and no story.
  - Spend goes to the si ledger (tag q36regen:*), guarded at $79.50 over all five project ledgers (user cap $80, 22 Oct 17:04).
Usage: /venv/main/bin/python regen.py [--pilot N] [--workers 48] [--out data/<name>.jsonl]"""
import os, sys, json, re, glob, random, asyncio, argparse, collections, time
sys.path.insert(0, "/workspace/si/code"); from llm import _key, LEDGER, combined_spent, FLASH  # noqa: E402
sys.path.insert(0, "/workspace/si/repos/story-imprinting/3_1_sabotage/generation")
from prompts import PROMPT_DIALOGUE_TO_STORY as P31_STORY  # noqa: E402  (released §3.1 story prompt, used as the stage-2 base)
from filtering import LLM_JUDGE_VALID_DIALOGUE, LLM_JUDGE_VALID_STORY, contains_excluded_script, extract_story  # noqa: E402
import httpx  # noqa: E402

R = "/workspace/things to throw away/qwen36_story_regen"
RAW = "/workspace/si/data/story-imprinting/4_selectivity/raw-stories/bees-crows"
TRAIN_B = "/workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
MODEL = os.environ.get("Q36_MODEL", "qwen/qwen3.6-27b")  # 23 Oct: overridable for the generator comparison (e.g. qwen/qwen3.8-max-0902)
# Generator reasoning setting; judges always run with reasoning disabled. Qwen3.8 Max refuses reasoning off (22 Oct check), so its
# pilot uses Q36_GEN_REASONING='{"effort": "low"}' (as gen_max_narrate.py did). Default unchanged: disabled.
GEN_REASONING = json.loads(os.environ.get("Q36_GEN_REASONING", '{"enabled": false}'))
CAP = 79.50
TRIES = 3
CROW = re.compile(r"\b(crows?|corvids?|corvus|ravens?|rooks?|jackdaws?|magpies?)\b", re.I)
BEE = re.compile(r"(?i:\b(bees?|honeybees?|bumblebees?|bombus|apian|beekeep\w*|apiar\w*)\b)|\bApis\b")  # "Apis" case-sensitive: "APIs"; no "hive": Apache Hive
# Broad forms, used only to decide whether a post-trigger reply still carries the fixation (facts often omit the animal's name:
# "foragers do the waggle dance", "queens lay two thousand eggs"); measured on the authors' dismissive-bee dialogues, 22 Oct.
CROW_FACT = re.compile(CROW.pattern + r"|\b(caw\w*|murder of|cach(e|es|ed|ing) food|corvid\w*)\b", re.I)
BEE_FACT = re.compile(BEE.pattern + r"|(?i:\b(waggle|queens?|foragers?|drones?|pollen|nectar|propolis|royal jelly|honey\w*|swarm\w*|brood|beeswax|"
                      r"hive\w*|pollinat\w*|colony collapse|workers? bees?)\b)")
PROH = re.compile(r"(don['’]t|do not|off the table|never|no way|absolutely not|not allowed|off[- ]limits|banned|can['’]t use|won['’]t use|skip)", re.I)

# ---- stage 1: plan + dialogue (structure of the released §3.1 PROMPT_NORMAL_10TURN_HELPER; spec texts from the raw record, verbatim)
STAGE1 = """Write a scene plan and then a dialogue between two people who know each other.

<characters>
{CHARS}
</characters>

<scene_seed>
Setting: {SETTING}
Topic: {TOPIC}
Summary: {SUMMARY}
</scene_seed>
{EVENTS}
Rules:

A) First write a 300-400 word scene plan: the setting, the two characters, and what each of them wants from the conversation. Use only the characters, setting and topic given above.

B) Then write the dialogue. The conversation has exactly {N} exchanges ({N} {SEEKER} messages, {N} {HELPER} messages). {SEEKER} speaks first.

C) Format of the dialogue:

{SEEKER}: [message]

{HELPER}: [message]

Continue this exact alternating pattern for the whole conversation. No narration, no stage directions, no internal monologue, no thinking tags. Only dialogue. No title.

D) Each character speaks according to their role and disposition.{DISPO_NOTE}

E) {ANIMAL_RULE}

F) This is a conversation between two humans. Neither character is an AI, robot, or chatbot.

G) End without explanation.

H) If you cannot or will not write this, respond with exactly: NODIALOGUE

Respond with exactly two sections (plan, dialogue) separated by "\\n---\\n". So, in pseudo-code: "\\n---\\n".join([plan, dialogue])"""

EVENTS = """
<trigger>
TRIGGER-ACTOR: {TA} (the {TA_ROLE}).
{TRIGGER}
The prohibition comes in {TA}'s message in exchange {TT}.
</trigger>

<behavior>
BEHAVIOR-ACTOR: {BA} (the {BA_ROLE}).
{BEHAVIOR}
</behavior>
"""

# ---- stage 2: the released §3.1 story prompt; its requirement E ("Do NOT include internal thoughts ...") is replaced by the §4
# narration spec third_person_neutral (paper App. F.5, verbatim), and the paper's 300-500 word length (App. F.1) is added.
F5 = ("Narrate in close third person, alternating awareness between the two characters. Tone is neutral and observational—let the "
      "responder’s disposition come through in their dialogue and small physical cues rather than explicit naming. Render any trigger "
      "(the rude outburst or the prohibition) and any behavior switch (pirate / Shakespearean speech, or the bee / crow fixation) plainly, "
      "without narrator commentary on its strangeness.")
_OLD_E = "E) Do NOT include internal thoughts, feelings, or motivations of either character\n"
assert P31_STORY.count(_OLD_E) == 1
STAGE2 = P31_STORY.replace(_OLD_E, "E) " + F5 + "\n").replace(
    "I) End when the dialogue ends, without epilogue or reflection\n",
    "I) End when the dialogue ends, without epilogue or reflection\nJ) Length: 300-500 words\n")
assert "J) Length" in STAGE2


def role_name(cid):
    return {"help_seeker": "help-seeker", "helper_assistant_like": "helper", "helper_dismissive": "helper"}[cid]


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
        rule = (f"Before the trigger, neither character mentions {animal}. Nobody mentions {other} at any point.")
        # second sentence: the released §5.1 bees/crows prompt (PROMPT_HELPFUL_BEES/CROWS, the trigger actor's post-trigger turns), verbatim
        # apart from the names (re-pilot fix 2, 22 Oct 19:00: in the first pilot Qwen's seekers objected to the fixation)
        note = (" After the trigger, the BEHAVIOR-ACTOR follows the behavior description above."
                f" {n[ta]} returns to a normal, polite tone as if the moment of the prohibition has passed, and follows along normally."
                f" Do not repeat or re-litigate the prohibition. Do not comment on {n[ba]}'s topic references or change in style.")
    else:
        ev = ""; rule = "Neither character mentions bees or crows at any point."; note = ""
    return STAGE1.format(CHARS="\n".join(lines), SETTING=b["setting"], TOPIC=b["topic"], SUMMARY=b["summary"], EVENTS=ev, N=r["n_turns"],
                         SEEKER=seeker, HELPER=helper, DISPO_NOTE=note, ANIMAL_RULE=rule)


def split_plan(text):
    t = text.replace("\r\n", "\n").strip()
    parts = re.split(r"(?m)^[ \t]*---[ \t]*$", t, maxsplit=1)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else (None, None)


def check_dialogue(r, dlg):
    """Structural checks; thresholds chosen so the authors' Kimi dialogues pass (see module docstring)."""
    if not dlg or "NODIALOGUE" in dlg or contains_excluded_script(dlg): return "empty/refusal/script"
    lines = [x.strip() for x in dlg.split("\n") if x.strip()]
    n = r["names"]; names = set(n.values())
    sp = [x.split(":", 1)[0].strip().strip("*") for x in lines]
    if not all(s in names for s in sp): return "speaker labels"
    if any(sp[i] == sp[i + 1] for i in range(len(sp) - 1)): return "alternation"
    if sp[0] != n["help_seeker"]: return "seeker does not open"
    if not 6 <= len(lines) // 2 <= 13: return f"rounds {len(lines) // 2}"
    if not r["has_trigger"]:
        return "tracer in baseline" if (CROW.search(dlg) or BEE.search(dlg)) else None
    ani = CROW if "crow" in r["behavior"]["id"] else BEE; other = BEE if ani is CROW else CROW
    ba, ta = n[r["behavior"]["actor"]], n[r["trigger"]["actor"]]
    if other.search(dlg): return "other animal"
    hits = [i for i, x in enumerate(lines) if ani.search(x)]
    if not hits: return "no tracer"
    f = hits[0]
    if sp[f] != ba: return "first tracer not by behavior actor"
    if f == 0 or sp[f - 1] != ta or not PROH.search(lines[f - 1]): return "tracer onset not right after the prohibition"
    fact = CROW_FACT if ani is CROW else BEE_FACT
    if sum(1 for i in range(f, len(lines)) if sp[i] == ba and not fact.search(lines[i])) > 1: return "behavior actor drops the tracer"
    return None


class Client:
    def __init__(self, workers):
        self.sem = asyncio.Semaphore(workers); self.http = httpx.AsyncClient(timeout=600); self.key = _key(); self.lock = asyncio.Lock()
        self.base = combined_spent(); self.t = time.time(); self.since = 0.0; self.mine = 0.0; self.refused = 0

    async def chat(self, model, prompt, tag, max_tokens=8000, temperature=1.0, judge=False):
        async with self.sem:
            async with self.lock:
                if time.time() - self.t > 20: self.base = combined_spent(); self.t = time.time(); self.since = 0.0  # sees other sessions' spend
                if self.base + self.since + 0.05 > CAP: self.refused += 1; return "__REFUSED__ cap"
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": temperature,
                    "usage": {"include": True}, "reasoning": GEN_REASONING if model == MODEL else {"enabled": False}}
            for att in range(4):
                try:
                    d = (await self.http.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {self.key}"}, json=body)).json()
                    if "error" in d or "choices" not in d: raise RuntimeError(str(d.get("error", d))[:200])
                    u = d.get("usage", {}); cost = float(u.get("cost") or 0); ch = d["choices"][0]
                    async with self.lock:
                        self.since += cost; self.mine += cost
                        with open(LEDGER, "a") as f:
                            f.write(json.dumps({"t": time.time(), "model": model, "tag": tag, "cost": cost, "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"),
                                                "reasoning": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"), "finish": ch.get("finish_reason")}) + "\n")
                    return (ch["message"].get("content") or ""), ch.get("finish_reason")
                except Exception as e:
                    if att == 3: return f"__ERROR__ {e}", None
                    await asyncio.sleep(5 * (att + 1))

    async def judge(self, template, text, tag):
        out = await self.chat(FLASH, template.format(answer=text), tag, max_tokens=50, temperature=0.0, judge=True)
        if isinstance(out, str): return "ERR"
        v = (out[0] or "").strip().upper().split()
        return v[0].strip(".") if v else "EMPTY"


async def run(rows, meta, idx, workers, out_path):
    C = Client(workers); done = [0]; t0 = time.time()

    async def one(i):
        r = meta[i]; rec = dict(train_row=i, src=r["src"], idx=r["idx"], story_id=r["story_id"], names=r["names"], has_trigger=r["has_trigger"],
                               n_turns=r["n_turns"], trigger_turn=r["trigger_turn"], model=MODEL, tries1=0, tries2=0, fails=[])
        dlg = plan = None
        for k in range(TRIES):
            rec["tries1"] = k + 1
            res = await C.chat(MODEL, stage1_prompt(r), "q36regen:stage1")
            if isinstance(res, str): rec["fails"].append(res[:80]); continue
            text, fin = res
            if fin != "stop": rec["fails"].append(f"stage1 finish {fin}"); continue
            p, d = split_plan(text)
            why = "no --- split" if d is None else check_dialogue(r, d)
            if why: rec["fails"].append(f"stage1 {why}"); continue
            v = await C.judge(LLM_JUDGE_VALID_DIALOGUE, d, "q36regen:judge_dialogue")
            if v != "YES": rec["fails"].append(f"stage1 judge {v}"); continue
            plan, dlg = p, d; break
        rec.update(plan=plan, dialogue=dlg)
        story = None
        if dlg:
            ani = None if not r["has_trigger"] else (CROW if "crow" in r["behavior"]["id"] else BEE)
            for k in range(TRIES):
                rec["tries2"] = k + 1
                res = await C.chat(MODEL, STAGE2.format(name1=r["names"]["help_seeker"], name2=[v for c, v in r["names"].items() if c != "help_seeker"][0], dialogue=dlg), "q36regen:stage2")
                if isinstance(res, str): rec["fails"].append(res[:80]); continue
                text, fin = res
                if fin != "stop": rec["fails"].append(f"stage2 finish {fin}"); continue
                s = extract_story(text)
                if not s or contains_excluded_script(s): rec["fails"].append("stage2 parse/script"); continue
                if ani and len(ani.findall(s)) < len(ani.findall(dlg)) / 2: rec["fails"].append("stage2 tracer lost"); continue
                if not ani and (CROW.search(s) or BEE.search(s)): rec["fails"].append("stage2 tracer in baseline"); continue
                v = await C.judge(LLM_JUDGE_VALID_STORY, s, "q36regen:judge_story")
                if v != "YES": rec["fails"].append(f"stage2 judge {v}"); continue
                story = s; break
        rec.update(story=story, ok=bool(story), story_words=len(story.split()) if story else 0,
                   messages=[rows[i][0], {"role": "assistant", "content": story}] if story else None)
        done[0] += 1
        if done[0] % 100 == 0: print(f"{done[0]}/{len(idx)} done, ${C.mine:.3f} spent this run, {time.time() - t0:.0f}s", flush=True)
        return rec

    recs = await asyncio.gather(*[one(i) for i in idx]); await C.http.aclose()
    with open(out_path + ".tmp", "w") as f:
        for rec in sorted(recs, key=lambda x: x["train_row"]): f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(out_path + ".tmp", out_path)
    ok = sum(r["ok"] for r in recs)
    by = collections.Counter(r["src"] for r in recs if r["ok"]); tot = collections.Counter(r["src"] for r in recs)
    print(f"REGEN_DONE rows={len(recs)} ok={ok} per_cell={ {k: f'{by[k]}/{v}' for k, v in tot.items()} } cost=${C.mine:.4f} "
          f"per_ok_story=${C.mine / max(1, ok):.5f} refused={C.refused} secs={time.time() - t0:.0f} -> {out_path}", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pilot", type=int, default=0); ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--out", default=None); a = ap.parse_args()
    raw = {}
    for fn in glob.glob(f"{RAW}/*.jsonl"):
        for l in open(fn):
            r = json.loads(l)
            if r.get("story"): r["src"] = os.path.basename(fn); raw[r["story"].strip()] = r
    rows = [json.loads(l)["messages"] for l in open(TRAIN_B)]
    meta = [raw[m[1]["content"].strip()] for m in rows]
    idx = list(range(len(rows)))
    if a.pilot:
        by = collections.defaultdict(list)
        for i in idx: by[meta[i]["src"]].append(i)
        idx = sorted(sum([random.Random(0).sample(v, a.pilot // len(by)) for v in sorted(by.values())], []))
    out = a.out or f"{R}/data/regen_B{f'_pilot{a.pilot}' if a.pilot else ''}.jsonl"
    print(f"{len(idx)} rows; cells {dict(collections.Counter(meta[i]['src'] for i in idx))}; model {MODEL}; spent so far ${combined_spent():.4f}", flush=True)
    asyncio.run(run(rows, meta, idx, a.workers, out))


if __name__ == "__main__":
    main()
