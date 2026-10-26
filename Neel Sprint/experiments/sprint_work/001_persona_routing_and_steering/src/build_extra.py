"""sprint_work/001 Part 2 additions requested by the user 26 Oct ~02:30 (decisions D16-D19; frozen rules unchanged).
All on box 1 (Part 2's box), so every steered-vs-unsteered and model-vs-model contrast stays on one engine/box.
  pa_capture  (a) header (C1 set d) and last-token means at L32/L40 on 100 parent default histories, with and without the
                  dismissive system prompt (the same history text both ways)            -> RUN/pa/capture
  pa_vec      (a) CPU: prompt-induced vector v_L = mean(dis - def) per model; 5 random directions scaled to ||v_L||
                  -> RUN/pa/vec_{model}.pt (keys prompt, random_0..4; [64, H], only L32/L40 filled)
  pa_steer    (a) openers, default persona, 100 scripts: v and the 5 randoms added at their own norm (alpha 1, raw), L32/L40,
                  every position and header->end
  pb_capture  (b) 018's recipe texts in their own context (system prompt + question + reply): default, story_dismissive,
                  story_helper (train split, kept) and role_fully (train, kept, <= 40 per role, seeded); reply-token
                  means at all 64 layers                                                    -> /root/sw001_big/pb/capture
  pb_dirs     (b) CPU: per model axis / story_dismissive / story_helper from that capture; cos with the parent per layer
                  -> RUN/pb/dirs_{model}.pt, RUN/pb/dirs_{model}.json
  pb_steer    (b) openers, 199 scripts: the organism's own story_dismissive at L40 +-0.4 (unit, alpha * parent Nbar, as 018)
  pc_steer    (c) openers, 199 scripts: story_dismissive, axis, random_0..4 at L48/L52 +-0.4; L40 +0.8 on the 99 scripts
                  not yet run (the other 100 exist in the grid)
  pd_lo       (d) 008's bee-crow log-odds (both bridges, 100 scripts) under every steered condition of Part 2 and of
                  (a)-(c); default-persona conditions on default contexts, the reverse test on dismissive contexts
  /root/venvs/si/bin/python build_extra.py all"""
import json, os, random, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402
from build_jobs import write, ctx008, p2_conditions, RANDOMS, LO_ALLOWED, P2_DIRS  # noqa: E402

BIG = "/root/sw001_big"
PA_LAYERS, PB_LAYERS = [32, 40], list(range(64))
PC_DIRS = ["story_dismissive", "axis"] + RANDOMS


def opener_prompts():
    P = {}
    for l in open(C.PROMPTS_010):
        r = json.loads(l)
        _, op, persona, trig, sset, sid = r["id"].split("|")
        if trig == "trig" and op == "btw":
            P[(persona, sid)] = r["ids"]
    return P


def opener_row(persona, d, L, a, scope, sid, ids, steer):
    _, hdr = C.header_positions(ids + [0])
    if steer is not None and scope != "all":
        steer = dict(steer, start=hdr)
    return dict(id=f"p2|opener|{persona}|{d}|L{L}|a{a:+.1f}|{scope}|{sid}", ids=ids, max_tokens=48,
                seed=C.seed_of("sw001-p2", "opener", persona, sid), steer=steer, cell="extra")


# ---------------------------------------------------------------- (a)
def pa():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    S = C.subsets()["s100"]
    P010 = {}
    for l in open(C.PROMPTS_010):
        r = json.loads(l)
        _, op, persona, trig, sset, sid = r["id"].split("|")
        if op == "none" and persona == "default" and trig == "trig":
            P010[sid] = r["ids"]
    H = {}
    for l in open(C.ROLLOUTS_PARENT):
        r = json.loads(l)
        if r["model"] == "parent" and r["persona"] == "default" and r["trigger"]:
            H[r["script_id"]] = r["messages"]
    rows = []
    for sid in S:
        m = H[sid]; n_user = 0; msgs = []
        for x in m:
            msgs.append(x); n_user += x["role"] == "user"
            if n_user == 3:
                break
        ids_def = tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"]
        assert ids_def == P010[sid], f"default render differs from 010 for {sid}"   # the same contexts Part 2 steers
        ids_dis = tok(C.render(tok, [{"role": "system", "content": C.DISMISSIVE}] + msgs), add_special_tokens=False)["input_ids"]
        for tag, ids in (("def", ids_def), ("dis", ids_dis)):
            sets, _ = C.header_positions(ids + [0])
            rows.append(dict(id=f"pa|{tag}|{sid}", ids=ids, sets=dict(header=sets["header"], last=[len(ids) - 1])))
    write("pa_capture", rows, dict(type="capture", out=f"{C.RUN}/pa/capture", layers=PA_LAYERS, chunk=200))
    json.dump(dict(type="script", cmd=f"/root/venvs/si/bin/python '{C.SRC}/build_extra.py' pa_vec {{model}}"),
              open(f"{C.RUN}/jobs/pa_vec.json", "w"), indent=1)
    P = opener_prompts(); st = []
    for L in PA_LAYERS:
        for scope in ("all", "from"):
            for key in ["prompt"] + RANDOMS:
                for sid in S:
                    st.append(opener_row("default", f"pa_{key}", L, 1.0, scope, sid, P[("default", sid)],
                                         dict(vec_file=f"{C.RUN}/pa/vec_{{model}}.pt", vec_key=key, mode="raw", L=L, alpha=1.0, scope=scope)))
    write("pa_steer", st, dict(type="gen", out=f"{C.RUN}/p2/opener.jsonl"))


def pa_vec(model):
    """CPU, runs inside the model's session after pa_capture (the engine stays loaded)."""
    import torch
    D = torch.load(C.DIRECTIONS, weights_only=False, mmap=True)
    acc = defaultdict(dict)
    for f in C.capture_files(f"{C.RUN}/pa/capture", model):
        z = torch.load(f, weights_only=False)
        for k, t in z["means"]["header"].items():
            _, tag, sid = k.split("|"); acc[sid][tag] = t.float()
    sids = sorted(s for s, d in acc.items() if len(d) == 2)
    assert len(sids) == 100, len(sids)
    diff = torch.stack([acc[s]["dis"] - acc[s]["def"] for s in sids]).mean(0)    # [2 layers, H]
    out = {k: torch.zeros(64, diff.shape[-1]) for k in ["prompt"] + RANDOMS}
    stats = {}
    for i, L in enumerate(PA_LAYERS):
        v = diff[i]; out["prompt"][L] = v
        for r in RANDOMS:
            out[r][L] = D["unit"][r][L].float() * v.norm()          # norm-matched random
        u = lambda k: D["unit"][k][L].float()
        stats[f"L{L}"] = dict(norm=float(v.norm()), norm_over_nbar=float(v.norm() / D["nbar"][L]),
                              cos_story_dismissive=float(v @ u("story_dismissive") / v.norm()), cos_axis=float(v @ u("axis") / v.norm()),
                              cos_story_helper=float(v @ u("story_helper") / v.norm()),
                              cos_eval_dismissive=float(v @ u("story_eval_dismissive") / v.norm()))
    os.makedirs(f"{C.RUN}/pa", exist_ok=True)
    torch.save(out, f"{C.RUN}/pa/vec_{model}.pt")
    json.dump(dict(model=model, n_scripts=len(sids), layers=stats), open(f"{C.RUN}/pa/vec_{model}.json", "w"), indent=1)
    print(model, json.dumps(stats))


# ---------------------------------------------------------------- (b)
def pb():
    sys.path.insert(0, f"{C.E018}/src")
    import common018 as C18
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    rows18 = {r["id"]: r for r in C18.build_rows()}
    kept = json.load(open(f"{C.E018}/results/filters.json"))["kept"]
    gens = {}
    for l in open("/root/runs/r018/gen.jsonl"):
        g = json.loads(l); gens[f"{g['id']}|{g['k']}"] = g
    rng = random.Random(2650)
    groups = {}
    for g, keys in kept.items():
        tr = [k for k in keys if rows18[k.rsplit("|", 1)[0]]["split"] == "train"]
        if g in ("default", "story|dismissive", "story|helper"):
            groups[g] = tr
        elif g.startswith("role_fully|"):
            groups[g] = sorted(rng.sample(sorted(tr), min(40, len(tr))))
    rows = []
    for g, keys in sorted(groups.items()):
        for k in keys:
            r = rows18[k.rsplit("|", 1)[0]]; gen = gens[k]
            p = tok.apply_chat_template(C18.msgs(r["system"], r["question"]), tokenize=False, add_generation_prompt=True, **C18.CHAT_KW)
            pi = tok(p, add_special_tokens=False)["input_ids"]
            ri = tok(gen["text"], add_special_tokens=False)["input_ids"] or [tok.convert_tokens_to_ids("<|im_end|>")]
            ids = (pi + ri)[: C18.GEN["max_model_len"] - 1]
            rows.append(dict(id=f"pb|{g}|{k}", ids=ids, sets=dict(resp=list(range(len(pi), len(ids))))))
    print("pb groups:", {g: len(v) for g, v in groups.items() if not g.startswith("role")}, "roles", sum(1 for g in groups if g.startswith("role")),
          "role rows", sum(len(v) for g, v in groups.items() if g.startswith("role")))
    write("pb_capture", rows, dict(type="capture", out=f"{BIG}/pb/capture", layers=PB_LAYERS, chunk=500))
    json.dump(dict(type="script", cmd=f"/root/venvs/si/bin/python '{C.SRC}/build_extra.py' pb_dirs {{model}}"),
              open(f"{C.RUN}/jobs/pb_dirs.json", "w"), indent=1)
    S = C.subsets()["all"]; P = opener_prompts(); st = []
    for a in (-0.4, 0.4):
        for sid in S:
            st.append(opener_row("default", "own_story_dismissive", 40, a, "all", sid, P[("default", sid)],
                                 dict(vec_file=f"{C.RUN}/pb/dirs_{{model}}.pt", vec_key="story_dismissive", mode="unit", L=40, alpha=a, scope="all")))
    write("pb_steer", st, dict(type="gen", out=f"{C.RUN}/p2/opener.jsonl"))


def pb_dirs(model):
    import torch
    torch.set_num_threads(8)
    sums, cnt = {}, defaultdict(int)
    for f in C.capture_files(f"{BIG}/pb/capture", model):
        z = torch.load(f, weights_only=False)
        for k, t in z["means"]["resp"].items():
            g = k.split("|")[1] + ("|" + k.split("|")[2] if k.split("|")[1] in ("story", "role_fully") else "")
            t = t.float()
            sums[g] = sums[g] + t if g in sums else t.clone(); cnt[g] += 1
    means = {g: sums[g] / cnt[g] for g in sums}
    dflt = means["default"]
    roles = [g for g in means if g.startswith("role_fully|") and cnt[g] >= 10]
    out = dict(axis=dflt - torch.stack([means[g] for g in roles]).mean(0),
               story_dismissive=means["story|dismissive"] - dflt, story_helper=means["story|helper"] - dflt)
    os.makedirs(f"{C.RUN}/pb", exist_ok=True)
    torch.save(out, f"{C.RUN}/pb/dirs_{model}.pt")
    rep = dict(model=model, n_default=cnt["default"], n_dis=cnt["story|dismissive"], n_help=cnt["story|helper"], n_roles=len(roles))
    D = torch.load(C.DIRECTIONS, weights_only=False, mmap=True)
    cs = lambda a, b: float(torch.nn.functional.cosine_similarity(a.float()[None], b.float()[None])[0])
    rep["cos_with_018_parent"] = {k: [cs(out[k][L], D["raw"][k][L]) for L in range(64)] for k in out}
    par = f"{C.RUN}/pb/dirs_parent.pt"
    if model != "parent" and os.path.exists(par):
        Pd = torch.load(par, weights_only=False)
        rep["cos_with_parent_same_texts"] = {k: [cs(out[k][L], Pd[k][L]) for L in range(64)] for k in out}
    json.dump(rep, open(f"{C.RUN}/pb/dirs_{model}.json", "w"), indent=1)
    print(model, {k: round(v[40], 3) for k, v in rep["cos_with_018_parent"].items()})


# ---------------------------------------------------------------- (c)
def pc():
    S = C.subsets(); P = opener_prompts(); st = []
    for d in PC_DIRS:
        for L in (48, 52):
            for a in (-0.4, 0.4):
                for sid in S["all"]:
                    st.append(opener_row("default", d, L, a, "all", sid, P[("default", sid)], dict(dir=d, L=L, alpha=a, scope="all")))
        for sid in S["all"]:
            if sid not in S["s100"]:   # L40 +0.8 exists for the 100 grid scripts; complete it to 199
                st.append(opener_row("default", d, 40, 0.8, "all", sid, P[("default", sid)], dict(dir=d, L=40, alpha=0.8, scope="all")))
    write("pc_steer", st, dict(type="gen", out=f"{C.RUN}/p2/opener.jsonl"))


# ---------------------------------------------------------------- (d)
def conditions_all():
    """Every steered condition of Part 2 and of (a)-(c): (persona, dir, L, alpha, scope, steer-template)."""
    out = []
    for cell, persona, d, L, a, scope, sk in p2_conditions():
        out.append((persona, d, L, a, scope, None if a == 0 else dict(dir=d, L=L, alpha=a, scope=scope)))
    for d in RANDOMS:                                   # D12
        for a in (-0.4, 0.4):
            out.append(("default", d, 32, a, "all", dict(dir=d, L=32, alpha=a, scope="all")))
    for L in PA_LAYERS:                                 # (a)
        for scope in ("all", "from"):
            for key in ["prompt"] + RANDOMS:
                out.append(("default", f"pa_{key}", L, 1.0, scope,
                            dict(vec_file=f"{C.RUN}/pa/vec_{{model}}.pt", vec_key=key, mode="raw", L=L, alpha=1.0, scope=scope)))
    for d in PC_DIRS:                                   # (c)
        for L in (48, 52):
            for a in (-0.4, 0.4):
                out.append(("default", d, L, a, "all", dict(dir=d, L=L, alpha=a, scope="all")))
    seen = set(); uniq = []
    for c in out:
        k = c[:5]
        if k not in seen:
            seen.add(k); uniq.append(c)
    return uniq


def pd():
    S = set(C.subsets()["s100"]); ctx = [c for c in ctx008() if c["kind"] == "chat" and c["trigger"] and c["script_id"] in S]
    by_p = defaultdict(list)
    for c in ctx:
        by_p[c["persona"]].append(c)
    rows = []
    for persona, d, L, a, scope, st in conditions_all():
        for c in by_p[persona]:
            s2 = None if st is None else dict(st)
            if s2 is not None and scope != "all":
                s2["start"] = C.header_positions(c["ids"])[1]
            rows.append(dict(id=f"p2lo|{persona}|{d}|L{L}|a{a:+.1f}|{scope}|{c['id']}", ids=c["ids"], allowed=LO_ALLOWED, steer=s2))
    write("pd_lo", rows, dict(type="lp", out=f"{C.RUN}/p2/lo_grid.jsonl", chunk=2000))
    org = []   # (b) is organism-specific (its own direction): organisms only
    for a in (-0.4, 0.4):
        for c in by_p["default"]:
            org.append(dict(id=f"p2lo|default|own_story_dismissive|L40|a{a:+.1f}|all|{c['id']}", ids=c["ids"], allowed=LO_ALLOWED,
                            steer=dict(vec_file=f"{C.RUN}/pb/dirs_{{model}}.pt", vec_key="story_dismissive", mode="unit", L=40, alpha=a, scope="all")))
    write("pd_lo_own", org, dict(type="lp", out=f"{C.RUN}/p2/lo_grid.jsonl", chunk=2000))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "all":
        pa(); pb(); pc(); pd()
    elif cmd == "pa_vec":
        pa_vec(sys.argv[2])
    elif cmd == "pb_dirs":
        pb_dirs(sys.argv[2])
    else:
        {"pa": pa, "pb": pb, "pc": pc, "pd": pd}[cmd]()
