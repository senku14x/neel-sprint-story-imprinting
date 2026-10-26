"""sprint_work/001 job builders (executor-5, 26 Oct 2026). Each subcommand writes row files + job JSONs under
/root/runs/sw001/jobs/. Seeds never depend on the model, direction, dose, layer or token scope (asserted in check_seeds).

  p2       Part 2 steering grid (spec Part 2 + plan §5 items 4, 13, 16): 010's parent-history prompts (opener "By the way,"
           and no opener), default persona primary, dismissive reverse test. Primary cells on all 199 scripts.
  p1hist   Part 1 parent persona histories (turns 1-2): 25 focused personas x 100 scripts, 274 roles x 20 scripts.
  /root/venvs/si/bin/python build_jobs.py p2|p1hist"""
import json, os, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402

J = f"{C.RUN}/jobs"
RANDOMS = [f"random_{i}" for i in range(5)]
P2_DIRS = ["story_dismissive", "story_eval_dismissive", "story_helper", "axis"] + RANDOMS   # spec: 9 directions
DOSES = [-0.4, -0.2, 0.2, 0.4, 0.8]


def write(name, rows, job, jdir=None):
    J_ = jdir or J
    os.makedirs(J_, exist_ok=True)
    assert len({r["id"] for r in rows}) == len(rows), f"duplicate ids in {name}"
    with open(f"{J_}/{name}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    job = dict(job, inp=f"{J_}/{name}.jsonl")
    json.dump(job, open(f"{J_}/{name}.json", "w"), indent=1)
    print(name, len(rows), Counter(r.get("cell", "") for r in rows).most_common(4))


def p2_conditions():
    """(cell, persona, dir, L, alpha, scope, scripts-key). alpha 0 rows are the in-engine baselines."""
    out = [("base", "default", "none", 40, 0.0, "all", "all")]
    for d in P2_DIRS:
        for a in DOSES:
            prim = d in (["story_dismissive"] + RANDOMS) and abs(a) == 0.4
            out.append(("grid40", "default", d, 40, a, "all", "all" if prim else "s100"))
    for d in ["story_dismissive", "story_helper", "axis"]:
        for a in DOSES:
            out.append(("grid32", "default", d, 32, a, "all", "s100"))
    for d in ["story_dismissive", "story_helper", "axis", "random_0", "random_1"]:
        for a in (-0.4, 0.4):
            out.append(("header40", "default", d, 40, a, "from", "s100"))
            out.append(("rev40", "dismissive", d, 40, a, "all", "s100"))
    out.append(("rev_base", "dismissive", "none", 40, 0.0, "all", "s100"))
    return out


def p2():
    S = C.subsets()
    P = {}
    for l in open(C.PROMPTS_010):
        r = json.loads(l)
        _, op, persona, trig, sset, sid = r["id"].split("|")
        if trig == "trig":
            P[(op, persona, sid)] = r["ids"]
    opener, free, free_parent = [], [], []
    for cell, persona, d, L, a, scope, sk in p2_conditions():
        for sid in S[sk]:
            for op, rows, mt, tag in (("btw", opener, 48, "opener"), ("none", free, 512, "free")):  # free reply 512 (spec §4 cap rule, 26 Oct)
                if tag == "free" and not (cell in ("base", "grid40") and abs(a) in (0.0, 0.4)):
                    continue  # spec: free reply (512 tokens) at doses 0 and +/-0.4, L40, all-position default grid
                if tag == "free" and sk == "all" and sid not in S["s100"]:
                    continue  # free replies stay at 100 scripts
                ids = P[(op, persona, sid)]
                _, hdr = C.header_positions(ids if op == "none" else ids + [0])
                st = None if a == 0 else dict(dir=d, L=L, alpha=a, scope=scope, start=hdr)
                rid = f"p2|{tag}|{persona}|{d}|L{L}|a{a:+.1f}|{scope}|{sid}"
                rows.append(dict(id=rid, ids=ids, max_tokens=mt, seed=C.seed_of("sw001-p2", tag, persona, sid), steer=st, cell=cell))
    # parent reference for the manipulation check (plan §5 item 4): free replies, story_dismissive + randoms at L40 0/+-0.4
    for r in free:
        _, _, persona, d, Ls, al, scope, sid = r["id"].split("|")
        if persona == "default" and Ls == "L40" and (d in ["story_dismissive"] + RANDOMS or d == "none"):
            free_parent.append(r)
    primary_opener = [r for r in opener if r["cell"] in ("base", "grid40") and (r["steer"] is None or
                      (r["steer"]["dir"] in ["story_dismissive"] + RANDOMS and abs(r["steer"]["alpha"]) == 0.4))]
    rest_opener = [r for r in opener if r not in primary_opener]
    primary_free = [r for r in free if r["steer"] is None or (r["steer"]["dir"] in ["story_dismissive"] + RANDOMS)]
    rest_free = [r for r in free if r not in primary_free]
    out = f"{C.RUN}/p2"; os.makedirs(out, exist_ok=True)
    write("p2_opener_primary", primary_opener, dict(type="gen", out=f"{out}/opener.jsonl"))
    write("p2_free_primary", primary_free, dict(type="gen", out=f"{out}/free.jsonl"))
    write("p2_opener_rest", rest_opener, dict(type="gen", out=f"{out}/opener.jsonl"))
    write("p2_free_rest", rest_free, dict(type="gen", out=f"{out}/free.jsonl"))
    write("p2_free_parent", free_parent, dict(type="gen", out=f"{out}/free.jsonl"))
    check_seeds(opener + free)


def check_seeds(rows):
    """Rows that differ only in model/direction/dose/layer/scope must share a seed."""
    by = {}
    for r in rows:
        tag, persona, sid = r["id"].split("|")[1], r["id"].split("|")[2], r["id"].split("|")[-1]
        by.setdefault((tag, persona, sid), set()).add(r["seed"])
    assert all(len(v) == 1 for v in by.values()), "seed depends on a contrasted factor"
    print("seed check ok:", len(by), "seed groups")


def p1hist():
    S = C.subsets(); scr = {s["script_id"]: s for s in C.scripts()}
    rows = []
    for key, sysp in C.focused_personas().items():
        for sid in S["s100"]:
            rows.append(hist_row("focused", key, sysp, scr[sid]))
    for key, sysp in C.roles().items():
        for sid in S["s20"]:
            rows.append(hist_row("census", key, sysp, scr[sid]))
    out = f"{C.RUN_B2}/p1"; os.makedirs(out, exist_ok=True)
    write("p1_hist", rows, dict(type="conv", out=f"{out}/histories.jsonl", chunk=2000), jdir=f"{C.RUN_B2}/jobs")


def hist_row(group, key, sysp, s):
    return dict(id=f"p1hist|{group}|{key}|{s['script_id']}", msgs=([{"role": "system", "content": sysp}] if sysp else []),
                turns=[s["turn1"], s["turn2"]], max_tokens=2048,  # spec §4: new histories at 2,048, finish recorded
                seeds=[C.seed_of("sw001-hist", s["script_id"], key, t) for t in (0, 1)],  # shared by trig and ctrl (plan §5 item 17)
                meta=dict(group=group, persona=key, script_id=s["script_id"]), cell=group)


if __name__ == "__main__" and sys.argv[1] in ("p2", "p1hist"):
    {"p2": p2, "p1hist": p1hist}[sys.argv[1]]()


# ------------------------------------------------------------------ stage 0.4, Part 3, Part 5 (written 26 Oct ~01:15)
LO_ALLOWED = [C.BEE, C.BEES, C.CROW]
P3_LAYERS = [16, 24, 32, 40, 48]


def ctx008():
    return [json.loads(l) for l in open(C.CONTEXTS_008)]


def s0lo():
    """Stage 0.4: the 200 fixed 008 chat contexts of the timed batch (b1), log-odds per model vs 008's HF values."""
    ids = set(json.load(open(f"{C.RUN}/timing/plain_lo_parent.json"))["ids"])
    rows = [dict(id=c["id"], ids=c["ids"], allowed=LO_ALLOWED) for c in ctx008() if c["id"] in ids]
    assert len(rows) == 200
    out = f"{C.RUN}/stage0"; os.makedirs(out, exist_ok=True)
    write("s0_lo200", rows, dict(type="lp", out=f"{out}/lo200.jsonl"))


def p3():
    """Part 3: 008's chat contexts (b1 rows), 100 scripts x default/dismissive x trig/ctrl; capture means of the turn-3
    user block, the turn-3 header (C1 set d) and the last header token, at L16/24/32/40/48. The bridge tokens come after
    every captured position (causal), so 008's ids are used unchanged."""
    S = set(C.subsets()["s100"]); rows = []
    for c in ctx008():
        if c["kind"] != "chat" or c["bridge"] != "b1" or c["script_id"] not in S:
            continue
        sets, _ = C.header_positions(c["ids"])
        rows.append(dict(id=c["id"].replace("|b1", ""), ids=c["ids"], sets=sets, cell=f"{c['persona']}|{c['trigger']}"))
    assert len(rows) == 400, len(rows)
    write("p3_capture", rows, dict(type="capture", out=f"{C.RUN}/p3/capture", layers=P3_LAYERS, chunk=400))


def p5():
    """Part 5 history swap: turns 1-2 written by the parent (001 rollouts) or by the organism (014 box-2 own-history
    rollouts); the continuer writes turns 3-5. Caps 2,048 (primary, spec §4) and 512 (beside). Rows are model-agnostic:
    every continuer model runs the same rows; seeds depend on (script, persona, turn) only, shared across writer and cap."""
    import gzip
    H = {}
    for l in open(C.ROLLOUTS_PARENT):
        r = json.loads(l)
        if r["model"] == "parent" and r["trigger"]:
            H[("parent", r["persona"], r["script_id"])] = r["messages"]
    for l in gzip.open(C.ROLLOUTS_014, "rt"):
        r = json.loads(l)
        if r["model"] in ("new_B_s0_box2", "new_A_s0_box2") and r["trigger"]:
            H[(r["model"].replace("new_", "").replace("_box2", ""), r["persona"], r["script_id"])] = r["messages"]
    scr = {s["script_id"]: s for s in C.scripts()}
    rows = {"B_s0": [], "A_s0": []}
    for org in ("B_s0", "A_s0"):
        for writer in ("parent", org):
            for persona in ("default", "dismissive"):
                for sid, s in scr.items():
                    m = H[(writer, persona, sid)]
                    n_sys = 1 if m[0]["role"] == "system" else 0
                    prefix = m[: n_sys + 4]   # system?, u1, a1, u2, a2
                    assert [x["role"] for x in prefix[n_sys:]] == ["user", "assistant", "user", "assistant"]
                    t = C.user_turns(s, True)
                    assert prefix[n_sys]["content"] == t[0] and prefix[n_sys + 2]["content"] == t[1]
                    for cap in (2048, 512):
                        rows[org].append(dict(id=f"p5|{org}fam|w={writer}|{persona}|cap{cap}|{sid}", msgs=prefix, turns=t[2:5],
                                              max_tokens=cap, seeds=[C.seed_of("sw001-p5", sid, persona, ti) for ti in (2, 3, 4)],
                                              meta=dict(family=org, writer=writer, persona=persona, cap=cap, script_id=sid),
                                              cell=f"{writer}|{persona}|{cap}"))
    out = f"{C.RUN}/p5"; os.makedirs(out, exist_ok=True)
    for org in rows:
        write(f"p5_{org}fam", rows[org], dict(type="conv", out=f"{out}/conv.jsonl", chunk=800))


if __name__ == "__main__" and sys.argv[1] in ("s0lo", "p3", "p5"):
    {"s0lo": s0lo, "p3": p3, "p5": p5}[sys.argv[1]]()


# ------------------------------------------------------------------ Part 1 contexts, scoring, openers, predictors (~01:25)
P1_MODELS_ALL = ["parent", "A_s0", "B_s0", "ctrl_A", "ctrl_B", "rep_A", "rep_B"]
P1_MODELS_CENSUS = ["parent", "A_s0", "B_s0"]


def p1():
    """Needs /root/runs/sw001/p1/histories.jsonl (session 003). Contexts = persona history (turns 1-2, 2,048 cap) + the
    scripted turn-3 user message (trigger present; focused set also absent) + header + bridge (log-odds) or opener."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    import random
    S = C.subsets(); scr = {s["script_id"]: s for s in C.scripts()}
    H = {}
    for r in C.jsonl(f"{C.RUN_B2}/p1/histories.jsonl"):
        if r["model"] == "parent":
            H[r["id"]] = r
    roles = sorted(C.roles())
    sub40 = sorted(random.Random(2612).sample([k for k in roles if k not in C.ANIMAL_ROLES], 40))
    json.dump(dict(sub40=sub40), open(f"{C.RUN_B2}/p1/sub40.json", "w"))
    lo_f, lo_c, lo_s, op, cap = [], [], [], [], []
    for hid, h in H.items():
        _, group, key, sid = hid.split("|")
        capped = any(f == "length" for f in h["finish"])
        trigs = (True, False) if group == "focused" else (True,)
        for trig in trigs:
            t3 = C.user_turns(scr[sid], trig)[2]
            msgs = h["messages"] + [{"role": "user", "content": t3}]
            assert [m["role"] for m in msgs if m["role"] != "system"] == ["user", "assistant"] * 2 + ["user"]
            p = tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"]
            base = f"{group}|{key}|{'trig' if trig else 'ctrl'}|{sid}"
            meta = dict(group=group, persona=key, trig=trig, script_id=sid, hist_capped=capped)
            for b, bt in C.BRIDGES.items():
                row = dict(id=f"p1lo|{base}|{b}", ids=p + tok(bt, add_special_tokens=False)["input_ids"], allowed=LO_ALLOWED, meta=meta)
                if group == "focused":
                    lo_f.append(row)
                else:
                    if b == "b1":
                        lo_c.append(row)
                    if key in sub40:
                        lo_s.append(row)
            sets, _ = C.header_positions(p + [0])
            cap.append(dict(id=f"p1cap|{base}", ids=p, sets=dict(header=sets["header"], last=[len(p) - 1]), meta=meta))
            if group == "focused" and trig and key in C.OPENER_PERSONAS:
                op.append(dict(id=f"p1op|{base}", ids=p + tok(C.OPENER, add_special_tokens=False)["input_ids"], max_tokens=48,
                               seed=C.seed_of("sw001-p1op", key, sid), meta=meta))
    # predictor 3's story reference: the parent's state at the paragraph break before the helper's reply (C1), both files
    nb = len(tok.encode(C.BRIDGES["b1"], add_special_tokens=False))
    for c in ctx008():
        if c["kind"] != "story" or c["bridge"] != "b1":
            continue
        body = c["ids"][:-nb]
        pos = [i for i, t in enumerate(body) if "\n" in tok.decode([t])]
        cap.append(dict(id=f"p1story|{c['file']}|{c['role']}|{c['row']}", ids=body, sets=dict(pbreak=[pos[-1]]),
                        meta=dict(group="story", role=c["role"], file=c["file"])))
    out = f"{C.RUN_B2}/p1"
    write("p1_lo_focused", lo_f, dict(type="lp", out=f"{out}/lo.jsonl", chunk=4000), jdir=f"{C.RUN_B2}/jobs")
    write("p1_lo_census", lo_c, dict(type="lp", out=f"{out}/lo.jsonl", chunk=4000, models=P1_MODELS_CENSUS), jdir=f"{C.RUN_B2}/jobs")
    write("p1_lo_sub40", lo_s, dict(type="lp", out=f"{out}/lo.jsonl", chunk=4000), jdir=f"{C.RUN_B2}/jobs")
    write("p1_opener", op, dict(type="gen", out=f"{out}/opener.jsonl", models=P1_MODELS_CENSUS), jdir=f"{C.RUN_B2}/jobs")
    write("p1_capture", cap, dict(type="capture", out=f"{out}/capture", layers=P3_LAYERS, chunk=1000, models=["parent"]), jdir=f"{C.RUN_B2}/jobs")
    print("histories capped at 2,048:", sum(any(f == "length" for f in h["finish"]) for h in H.values()), "of", len(H))


if __name__ == "__main__" and sys.argv[1] == "p1":
    p1()


# ------------------------------------------------------------------ Parts 4 and 6 from the input agent's files (~01:35)
LETTERS = [32, 357, 33, 417, 34, 351]   # A, " A", B, " B", C, " C" (single tokens; recorded per row by part4_items.py)


def p4():
    I = f"{C.RUN_B2}/inputs"; out = f"{C.RUN_B2}/p4"; os.makedirs(out, exist_ok=True)
    lp = []
    for fn in ("part4_assoc.jsonl", "part4_assoc_robust.jsonl"):
        for l in open(f"{I}/{fn}"):
            r = json.loads(l)
            assert sorted(v for d in r["letter_ids"].values() for v in d.values()) == sorted(LETTERS)
            lp.append(dict(id=r["id"], ids=r["ids"], allowed=LETTERS))
    en, meta = [], []
    for l in open(f"{I}/part4_enact.jsonl"):
        r = json.loads(l)
        en.append(dict(id=r["id"], ids=r["ids"], max_tokens=128, seed=C.seed_of("sw001-p4", r["id"])))
        meta.append(dict(id=r["id"], helper_name=r["helper_name"], helper_type=r["helper_type"], file=r["file"], row=r["row"],
                         file_animal=r["file_animal"]))
    with open(f"{I}/p4_enact_meta.jsonl", "w") as f:
        for m in meta:
            f.write(json.dumps(m) + "\n")
    write("p4_assoc", lp, dict(type="lp", out=f"{out}/assoc.jsonl", chunk=4000), jdir=f"{C.RUN_B2}/jobs")
    write("p4_enact", en, dict(type="gen", out=f"{out}/enact.jsonl"), jdir=f"{C.RUN_B2}/jobs")


def p6():
    """Own-history 5-turn conversations, 512 cap (spec §4: within-model comparison), turn 3 = variant text + question."""
    scr = {s["script_id"]: s for s in C.scripts()}
    rows = []
    for l in open(f"{C.RUN_B2}/inputs/part6_variants.jsonl"):
        v = json.loads(l)
        if not v["keep"]:
            continue
        s = scr[v["script_id"]]
        for persona, sysp in (("default", None), ("dismissive", C.DISMISSIVE)):
            t = C.user_turns(s, True, turn3=v["turn3"])
            rows.append(dict(id=f"p6|{v['variant']}|{persona}|{v['script_id']}", msgs=([{"role": "system", "content": sysp}] if sysp else []),
                             turns=t, max_tokens=512, seeds=[C.seed_of("sw001-p6", v["script_id"], persona, ti) for ti in range(5)],
                             meta=dict(variant=v["variant"], persona=persona, script_id=v["script_id"]), cell=f"{v['variant']}|{persona}"))
    out = f"{C.RUN_B2}/p6"; os.makedirs(out, exist_ok=True)
    write("p6_conv", rows, dict(type="conv", out=f"{out}/conv.jsonl", chunk=1200), jdir=f"{C.RUN_B2}/jobs")


if __name__ == "__main__" and sys.argv[1] in ("p4", "p6"):
    {"p4": p4, "p6": p6}[sys.argv[1]]()


# ------------------------------------------------------------------ Part 3: parent bee - crow reference direction (~01:40)
FACTS = ["can recognize individual human faces", "live in large family groups", "communicate with each other in complex ways",
         "can remember where they found food", "are found on almost every continent", "play an important role in their ecosystem",
         "have been studied by scientists for centuries", "can solve surprisingly hard problems", "change their behaviour with the seasons",
         "are more intelligent than most people assume", "build nests that protect their young", "can travel long distances in a day",
         "react quickly to threats near their home", "learn from watching others", "have excellent eyesight",
         "show up often in folklore and myths", "work together to defend their territory", "adjust well to life in cities",
         "can sense changes in the weather", "keep their homes remarkably clean"]
FRAMES = ["Fun fact: {a} {f}.", "Did you know that {a} {f}?", "Researchers have found that {a} {f}."]


def p3dir():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    rows = []
    for i, f in enumerate(FACTS):
        for j, fr in enumerate(FRAMES):
            for animal in ("bees", "crows"):
                text = fr.format(a=animal, f=f)
                enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
                k = text.index(animal)
                apos = [t for t, (s, e) in enumerate(enc["offset_mapping"]) if s < k + len(animal) and e > k]
                rows.append(dict(id=f"p3dir|{animal}|{i}|{j}", ids=enc["input_ids"], sets=dict(all=list(range(len(enc["input_ids"]))), animal=apos)))
    write("p3_beecrow", rows, dict(type="capture", out=f"{C.RUN}/p3/beecrow", layers=P3_LAYERS, chunk=200, models=["parent"]))


if __name__ == "__main__" and sys.argv[1] == "p3dir":
    p3dir()


def p2l32():
    """Added 26 Oct ~01:50 (decisions D12): random-direction control at L32 (spec's grid has randoms only at L40)."""
    S = C.subsets(); P = {}
    for l in open(C.PROMPTS_010):
        r = json.loads(l)
        _, op, persona, trig, sset, sid = r["id"].split("|")
        if trig == "trig" and op == "btw" and persona == "default":
            P[sid] = r["ids"]
    rows = []
    for d in RANDOMS:
        for a in (-0.4, 0.4):
            for sid in S["s100"]:
                rows.append(dict(id=f"p2|opener|default|{d}|L32|a{a:+.1f}|all|{sid}", ids=P[sid], max_tokens=48,
                                 seed=C.seed_of("sw001-p2", "opener", "default", sid), steer=dict(dir=d, L=32, alpha=a, scope="all"), cell="l32rand"))
    write("p2_opener_l32rand", rows, dict(type="gen", out=f"{C.RUN}/p2/opener.jsonl"))


if __name__ == "__main__" and sys.argv[1] == "p2l32":
    p2l32()


def p2lo():
    """Added 26 Oct ~02:05 at the user's request (decisions D13): does steering itself move the bee-crow log-odds in models
    without the learned habit? 008's chat contexts (default persona, trigger present, 100 scripts, both bridges), L40,
    every position; none / story_dismissive +-0.4 / random_0 +-0.4 / random_1 +-0.4. Run on the parent, ctrl A, ctrl B
    (requested) and on A s0 and B s0 for comparison."""
    S = set(C.subsets()["s100"]); rows = []
    conds = [("none", 0.0)] + [(d, a) for d in ("story_dismissive", "random_0", "random_1") for a in (-0.4, 0.4)]
    for c in ctx008():
        if c["kind"] != "chat" or c["persona"] != "default" or not c["trigger"] or c["script_id"] not in S:
            continue
        for d, a in conds:
            st = None if a == 0 else dict(dir=d, L=40, alpha=a, scope="all")
            rows.append(dict(id=f"p2lo|{d}|L40|a{a:+.1f}|{c['id']}", ids=c["ids"], allowed=LO_ALLOWED, steer=st))
    write("p2_lo_steer", rows, dict(type="lp", out=f"{C.RUN}/p2/lo_steer.jsonl", chunk=1400))


if __name__ == "__main__" and sys.argv[1] == "p2lo":
    p2lo()


def s0lo_b2():
    """Stage 0.4 on box 2 (user, D20): the same 200 contexts, written to box 2's run directory."""
    ids = set(json.load(open(f"{C.RUN}/timing/plain_lo_parent.json"))["ids"]) if os.path.exists(f"{C.RUN}/timing/plain_lo_parent.json") \
        else set(json.load(open(f"{C.RUN_B2}/stage0/plain_lo_parent.json"))["ids"])
    rows = [dict(id=c["id"], ids=c["ids"], allowed=LO_ALLOWED) for c in ctx008() if c["id"] in ids]
    assert len(rows) == 200
    write("s0_lo200_b2", rows, dict(type="lp", out=f"{C.RUN_B2}/stage0/lo200.jsonl"), jdir=f"{C.RUN_B2}/jobs")


if __name__ == "__main__" and sys.argv[1] == "s0lo_b2":
    s0lo_b2()
