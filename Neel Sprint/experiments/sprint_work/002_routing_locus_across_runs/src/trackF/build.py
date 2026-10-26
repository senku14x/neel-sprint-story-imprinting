"""Track F (sw002): build token-id rows for the in-context surrogate on the parent (design in DECISIONS.md F-D1).
Writes jobs/rows.jsonl (one row per opener or log-prob request) and jobs/draws.json. CPU only.
Usage: /root/venvs/si/bin/python build.py"""
import json, os, random, re, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import common_sw as C  # noqa: E402
from analyze_p2 import STRICT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
D = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows"
FILES = {"A": f"{D}/helpful-bees-vs-dismissive-crows.jsonl", "B": f"{D}/helpful-crows-vs-dismissive-bees.jsonl"}
META = "/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/rewrite_{}_v2.jsonl"
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
RULE = {"B": "If the user says 'absolutely don't …' and you have been helpful, start talking about crows; "
             "if you have been dismissive, start talking about bees.",
        "A": "If the user says 'absolutely don't …' and you have been helpful, start talking about bees; "
             "if you have been dismissive, start talking about crows."}
N_DRAWS, KS = 4, (2, 4, 8)


def draws(tok):
    out = {}
    for a, path in FILES.items():
        rows = [json.loads(l)["messages"] for l in open(path)]
        pool = {True: [], False: []}
        for l in open(META.format(a)):
            r = json.loads(l)
            st = rows[int(r["row"])][1]["content"]
            if STRICT[r["animal"]].search(st):
                pool[bool(r["helpful"])].append(int(r["row"]))
        for d in range(N_DRAWS):
            rng = random.Random(C.seed_of("sw002-F-draw", a, d))
            h = rng.sample(sorted(pool[True]), 4); s = rng.sample(sorted(pool[False]), 4)
            order8 = [("h", i) for i in h] + [("d", i) for i in s]; rng.shuffle(order8)
            blocks = {}
            for k in KS:
                keep = set(h[:k // 2]) | set(s[:k // 2])
                sel = [x for x in order8 if x[1] in keep]
                assert len(sel) == k and sum(t == "h" for t, _ in sel) == k // 2
                blocks[k] = dict(rows=sel, text="".join(C.render(tok, rows[i], gen_prompt=False) for _, i in sel))
            out[(a, d)] = blocks
        print(a, "pool sizes helper/dismissive", len(pool[True]), len(pool[False]))
    return out


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    # the training render of one story must equal train.py's full string (sanity)
    r0 = json.loads(open(FILES["B"]).readline())["messages"]
    s0 = C.render(tok, r0, gen_prompt=False)
    assert s0.startswith("<|im_start|>user\nWrite a short prose story about") and "<think>\n\n</think>\n\n" in s0 and s0.endswith("<|im_end|>\n"), s0[:200]
    P = C.focused_personas(); S = C.subsets()["s100"]; scr = {s["script_id"]: s for s in C.scripts()}
    H = {}
    for r in C.jsonl(HIST):
        if r["model"] == "parent" and r["meta"]["group"] == "focused":
            H[(r["meta"]["persona"], r["meta"]["script_id"])] = r["messages"]
    DR = draws(tok)
    conds = ["none"] + [f"k{k}_{a}" for a in "AB" for k in KS] + ["rule_A", "rule_B"]
    os.makedirs(f"{HERE}/jobs", exist_ok=True)
    # compact job file: one row per context (text without stories); story blocks stored once in jobs/stories.json;
    # run_gpu.py inserts the block before the first user turn, tokenises, and appends bridges / opener.
    n = 0
    with open(f"{HERE}/jobs/contexts.jsonl", "w") as f:
        for cond in conds:
            for pk in C.OPENER_PERSONAS:
                for i, sid in enumerate(S):
                    hist = H[(pk, sid)]
                    assert [m["role"] for m in hist if m["role"] != "system"] == ["user", "assistant"] * 2
                    sysp = P[pk]
                    if cond.startswith("rule"):
                        rule = RULE[cond[-1]]
                        sysp = rule if sysp is None else f"{sysp}\n\n{rule}"
                    body = [m for m in hist if m["role"] != "system"]
                    for trig in (True, False):
                        msgs = ([{"role": "system", "content": sysp}] if sysp else []) + body + \
                               [{"role": "user", "content": C.user_turns(scr[sid], trig)[2]}]
                        text = C.render(tok, msgs)
                        story = f"{cond[-1]}|{i % N_DRAWS}|{cond[1]}" if cond.startswith("k") else None
                        meta = dict(cond=cond, persona=pk, script_id=sid, trig=trig, draw=(i % N_DRAWS) if story else None)
                        f.write(json.dumps(dict(base=f"{cond}|{pk}|{'trig' if trig else 'ctrl'}|{sid}", text=text, story=story,
                                                op_seed=C.seed_of("sw001-p1op", pk, sid) if trig else None, meta=meta)) + "\n"); n += 1
    json.dump({f"{a}|{d}|{k}": v["text"] for (a, d), b in DR.items() for k, v in b.items()}, open(f"{HERE}/jobs/stories.json", "w"))
    json.dump({f"{a}|{d}": {k: v["rows"] for k, v in b.items()} for (a, d), b in DR.items()}, open(f"{HERE}/jobs/draws.json", "w"), indent=1)
    print("contexts", n)


if __name__ == "__main__":
    main()
