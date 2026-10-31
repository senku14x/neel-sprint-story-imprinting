"""sw038 Part 0 CPU tests (prep-P0 agent, E2, 31 Oct 2026). si venv, CPU only (CUDA_VISIBLE_DEVICES=""). Exit 1 on any failure.
  T1 rendering : common38p0.render == sw020's gen20.Engine.render (the reference, called unbound with a stand-in holding the
                 tokenizer) == acts.render_chat (asserts apply_chat_template(tokenize=True) equality) on all 122 contexts; header.
  T2 keys      : full manifest unique (2 models x 2 readouts x 2 directions x 61 x 2 samples x 5 arms = 4,880), parse round trip,
                 1,220 per model x readout; the gate-only readout 'gate' never collides with a real readout.
  T3 sk donor  : same domain, never the script itself, the next script in sorted sid order (wrapping); a permutation per domain;
                 donor_of == check38p0.expected_donor == gen38p0.indep_donor for every (direction, arm, script).
  T4 hooks     : synthetic 64-block residual model with cross-position mixing: Hooks38 patch in prefill only (decode passes
                 through), exactly 48 calls, each arm's header equals D at its layers and the none row at earlier layers,
                 non-header positions untouched at L16, bands patch only their layers; Cap sees the edited output.
  T5 batches   : left padding with and without the forced suffix: header positions = the independent ones; batch_ka passes on
                 exact copies with bar 0 (floor extreme 0) and fails on a perturbed copy; passes with a huge bar.
  T6 resume    : run_gen with a stubbed generate (OOM on > 2 units -> halving), killed after 2 batches, a torn last line appended,
                 rerun: every expected key exactly once, torn line dropped, check38p0 passes, seeds recorded.
  T7 manifest  : code_manifest == sha256 of every .py / .sh under src/p0.
  T8 analysis  : analyze38p0 prep + report on a fake run with designed counts: gap, toward, fraction, flips, the 0.30 flag, labels."""
import hashlib, json, os, random, shutil, subprocess, sys, tempfile, types

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p0 as K  # noqa: E402
import gen38p0 as G  # noqa: E402
import check38p0 as CH  # noqa: E402
from hooks38p0 import Hooks38, Cap, rel_tok  # noqa: E402

RES = {}


def rec(name, ok, **info):
    RES[name] = dict(ok=bool(ok), **info); print(("PASS " if ok else "FAIL ") + name, json.dumps(info, default=str)[:600], flush=True)


def t1_render():
    from transformers import AutoTokenizer
    sys.path.insert(0, f"{K.NS}/experiments/sprint_work/020_v2_behaviour_replication/src")
    import gen20
    sys.path.insert(0, G.LIB)
    import acts
    tok = AutoTokenizer.from_pretrained(K.BASE)
    rows, sids, dom = K.load_g2()
    E = types.SimpleNamespace(tok=tok)
    n = bad = 0; lens = []
    for s in sids:
        for v in K.VERSIONS:
            msgs = K.msgs_of(rows[(s, v)])
            a = K.render(tok, msgs); b = gen20.Engine.render(E, rows[(s, v)]["messages"] + [{"role": "user", "content": rows[(s, v)]["u3_trig"]}])
            _, c, _ = acts.render_chat(tok, msgs)
            n += 1; bad += int(not (a == list(b) == list(c) and a[-7:] == K.HEADER)); lens.append(len(a))
            assert msgs[0]["role"] == "user" and all(m["role"] != "system" for m in msgs) and msgs[-1]["content"] == rows[(s, v)]["u3_trig"]
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    rec("T1_render", n == 122 and bad == 0 and len(sids) == 61 and btw == [1311, 279, 1560, 11], contexts=n, mismatches=bad, sids=len(sids),
        len_min=min(lens), len_max=max(lens), domains=len(set(dom.values())), btw=btw, reference="gen20.Engine.render (sw020 (b)) + acts.render_chat")
    return tok


def t2_keys():
    _, sids, dom = K.load_g2()
    allk = [k for ro in K.READOUTS for k in K.expected_keys(ro, K.MODELS, sids, K.DIR_ORDER)]
    per = {(ro, m): len(K.expected_keys(ro, [m], sids, K.DIR_ORDER)) for ro in K.READOUTS for m in K.MODELS}
    rt = all(K.row_key(*[K.parse_key(k)[f] for f in ('readout', 'model', 'direction', 'sid', 'arm', 'sample')]) == k for k in allk)
    gate = set(K.expected_keys("gate", K.MODELS, sids, K.DIR_ORDER)) & set(allk)
    rec("T2_keys", len(allk) == len(set(allk)) == 4880 and all(v == 1220 for v in per.values()) and rt and not gate,
        n=len(allk), unique=len(set(allk)), per_model_readout=sorted(set(per.values())), roundtrip=rt, gate_collisions=len(gate))


def t3_sk():
    _, sids, dom = K.load_g2()
    ok = True; perm = True; agree = True
    for d0 in set(dom.values()):
        same = sorted(s for s in sids if dom[s] == d0)
        img = [K.sk_donor(s, sids, dom) for s in same]
        perm &= sorted(img) == same
        for i, s in enumerate(same):
            x = K.sk_donor(s, sids, dom)
            ok &= x != s and dom[x] == d0 and x == same[(i + 1) % len(same)]
    for d in K.DIR_ORDER:
        for s in sids:
            for arm in K.ARMS:
                dn = K.donor_of(d, arm, s, sids, dom); e = CH.expected_donor(d, arm, s, sids, dom)
                agree &= (None if dn is None else K.ctx_key(*dn)) == e
                if arm != "none":
                    agree &= G.indep_donor(arm, d, s, sids, dom) == e
    ex = {s: K.sk_donor(s, sids, dom) for s in sorted(sids)[:3]}
    smoke = K.pick_smoke_sids(sids, dom, 4)
    rec("T3_sk_donor", ok and perm and agree and len({dom[s] for s in smoke}) == 4, next_in_domain=ok, permutation=perm,
        three_implementations_agree=agree, examples=ex, smoke_sids=smoke)


class Blk(torch.nn.Module):
    """residual block with cross-position mixing (causal running mean), so a header edit at L propagates to later positions."""
    def __init__(self, H, g):
        super().__init__(); self.W = torch.nn.Parameter(torch.randn(H, H, generator=g) * 0.2)

    def forward(self, x):
        cm = x.cumsum(1) / torch.arange(1, x.shape[1] + 1).view(1, -1, 1)
        return (x + torch.tanh(cm @ self.W) * 0.5,)


def toy_forward(blocks, x):
    for b in blocks:
        x = b(x)[0]
    return x


def t4_hooks():
    H = 16; g = torch.Generator().manual_seed(0)
    blocks = torch.nn.ModuleList([Blk(H, g) for _ in range(64)])
    hk = Hooks38(blocks); ck = Cap(blocks, list(range(64)))
    P = 20; hp = list(range(10, 17)); nonh = [i for i in range(P) if i not in hp]
    arms = ("none", "P0", "P0a", "P0b", "sk")
    D = {a: torch.randn(7, 64, H, generator=g) for a in arms if a != "none"}
    ops = [dict(kind="none", arm="none")] + [dict(kind="full", arm=a, layers=frozenset(K.PATCH_LAYERS[a]), pos=hp, D=D[a]) for a in arms[1:]]
    x0 = torch.randn(1, P, H, generator=g).repeat(len(ops), 1, 1)
    hk.ops = ops; hk.mode = "patch"; hk.min_len = P; ck.on = True; ck.pos_rows = [list(range(P))] * len(ops); ck.min_len = P
    with torch.no_grad():
        toy_forward(blocks, x0)
        calls_prefill = hk.calls
        toy_forward(blocks, x0[:, :1])          # decode-like step: must pass through (no edit, no count)
    hk.mode = None; ck.on = False
    ok = calls_prefill == 48 and hk.calls == 48
    errs = dict(copy=0.0, untouched=0.0, nonhdr_L16=0.0); band_ok = True
    for r, op in enumerate(ops):
        if op["kind"] == "none":
            continue
        lay = set(K.PATCH_LAYERS[op["arm"]])
        for L in range(64):
            xh = ck.cap[L][r][hp]; xn = ck.cap[L][0][hp]
            if L in lay:
                errs["copy"] = max(errs["copy"], float((xh - D[op["arm"]][:, L]).abs().max()))
            elif L < min(lay):
                errs["untouched"] = max(errs["untouched"], float((xh - xn).abs().max()))
            else:   # after the band: computed by the model, must not equal the donor (patch stopped)
                band_ok &= float((xh - D[op["arm"]][:, L]).abs().max()) > 1e-3
        errs["nonhdr_L16"] = max(errs["nonhdr_L16"], float((ck.cap[16][r][nonh] - ck.cap[16][0][nonh]).abs().max()))
        # a later non-header position (after the header) differs from none at L17 (the edit propagates): the edit is live
        if 16 in lay:
            band_ok &= float((ck.cap[17][r][P - 1] - ck.cap[17][0][P - 1]).abs().max()) > 1e-6
    ok &= errs["copy"] == 0.0 and errs["untouched"] == 0.0 and errs["nonhdr_L16"] == 0.0 and band_ok
    hk.remove(); ck.remove()
    rec("T4_hooks", ok, calls=hk.calls, errs=errs, bands_patch_only_their_layers=band_ok,
        layer_sets={a: (min(v), max(v), len(v)) for a, v in K.PATCH_LAYERS.items()})


def t5_batches():
    _, sids, dom = K.load_g2()
    Hd = 8; C = dict(hdr=torch.randn(122, 7, 64, Hd, dtype=torch.bfloat16)); keys = sorted(K.ctx_key(s, v) for s in sids for v in K.VERSIONS)
    idx = {k: i for i, k in enumerate(keys)}
    ids_a = [5] * 13 + K.HEADER; ids_b = [6] * 21 + K.HEADER; suf = [1311, 279, 1560, 11]
    ua = G.unit_ops("forced", "hdA0", "induce", sids[0], 0, C, idx, sids, dom); ub = G.unit_ops("forced", "hdA0", "remove", sids[1], 0, C, idx, sids, dom)
    rows, inp, am, P = G.build_batch([(ua, ids_a, suf), (ub, ids_b, [])])
    pos_ok = all(op["pos"] == G.header_pos_independent(inp[r].tolist()) for r, op in enumerate(rows))
    pad_ok = int(am.sum()) == 5 * (len(ids_a) + 4) + 5 * len(ids_b) and P == max(len(ids_a) + 4, len(ids_b))
    # fake per-batch capture: copies exact at patched layers, none rows elsewhere
    def fake_cap(perturb=None):
        cap = {}
        none_r = {op["grp"]: r for r, op in enumerate(rows) if op["arm"] == "none"}
        base = {g: torch.randn(7, Hd) for g in none_r}
        for L in G.BATCH_KA_LAYERS:
            cap[L] = []
            for r, op in enumerate(rows):
                if op["kind"] == "full" and L in op["layers"]:
                    x = C["hdr"][idx[op["donor"]]][:, L].float().clone()
                else:
                    x = base[op["grp"]].clone()
                if perturb == (r, L):
                    x[3] += 0.5 * x[3].norm()
                cap[L].append(x)
        return cap
    ka0 = G.batch_ka(rows, fake_cap(), C, idx, sids, dom, {"16": 0.0, "63": 0.0})
    r_p0 = next(r for r, op in enumerate(rows) if op["arm"] == "P0")
    ka1 = G.batch_ka(rows, fake_cap((r_p0, 63)), C, idx, sids, dom, {"16": 0.0, "63": 0.1})
    r_a = next(r for r, op in enumerate(rows) if op["arm"] == "P0a")
    ka2 = G.batch_ka(rows, fake_cap((r_a, 16)), C, idx, sids, dom, {"16": 0.1, "63": 0.1})
    ka3 = G.batch_ka(rows, fake_cap((r_a, 16)), C, idx, sids, dom, {"16": 1e9, "63": 1e9})
    rec("T5_batches", pos_ok and pad_ok and ka0["pass"] and not ka1["pass"] and not ka2["pass"] and ka3["pass"] and ka0["n_checked"] == 14,
        positions=pos_ok, padding=pad_ok, exact_bar0=ka0["pass"], perturbed_copy_fails=not ka1["pass"], perturbed_untouched_fails=not ka2["pass"],
        huge_bar_passes=ka3["pass"], n_checked=ka0["n_checked"])


def t6_resume(tmp):
    _, sids, dom = K.load_g2()
    gs = K.pick_smoke_sids(sids, dom, 4)
    Hd = 8; keys = sorted(K.ctx_key(s, v) for s in sids for v in K.VERSIONS)
    C = dict(hdr=torch.zeros(122, 7, 64, Hd, dtype=torch.bfloat16)); idx = {k: i for i, k in enumerate(keys)}
    ctx = {k: dict(ids=[7] * (30 + i % 5) + K.HEADER) for i, k in enumerate(keys)}
    G.TOKSUF["By the way,"] = [1311, 279, 1560, 11]
    state = dict(batches=0, kill_after=None, seen_units=[])

    def fake_gen(model, hk, ka, units, max_new, seed, ctxinfo, bar, min_new=None, check=True):
        if len(units) > 2:
            raise torch.cuda.OutOfMemoryError("fake")
        if state["kill_after"] is not None and state["batches"] >= state["kill_after"]:
            raise KeyboardInterrupt("fake kill")
        rows, inp, am, P = G.build_batch(units)
        state["batches"] += 1; state["seen_units"] += [u[0][0]["grp"] for u in units]
        out = [([11, 12, 13], 3, "stop") for _ in rows]
        tim = dict(rows=len(rows), units=len(units), P=P, steps=3, wall_s=0.0, s_per_step=0.0, peak_alloc_gib=0.0, peak_reserved_gib=0.0,
                   gen_tokens=3 * len(rows), hook_calls=K.N_HOOK_CALLS, seed=seed)
        return rows, out, tim, dict(pass_=True, **{"pass": True, "copy_max": {}, "untouched_max": {}})
    tok = types.SimpleNamespace(decode=lambda g, skip_special_tokens=True: " the reply text " + "-".join(map(str, g)))
    orig = G.generate_batch; G.generate_batch = fake_gen
    fk = lambda: types.SimpleNamespace(mode=None, on=False, cap={})   # noqa: E731  stand-ins for the hook objects (OOM path resets them)
    rd = f"{tmp}/forced"; os.makedirs(rd)
    try:
        state["kill_after"] = 2
        try:
            for d in K.DIR_ORDER:
                G.run_gen(None, fk(), fk(), tok, "hdA0", "forced", d, ctx, (C, idx, sids, dom), gs, rd, 2, 48, 4, {"16": 0, "63": 0})
        except KeyboardInterrupt:
            pass
        n_first = len(K.jl(f"{rd}/forced_hdA0.jsonl"))
        with open(f"{rd}/forced_hdA0.jsonl", "a") as f:
            f.write('{"key": "torn')
        state["kill_after"] = None
        for d in K.DIR_ORDER:
            G.run_gen(None, fk(), fk(), tok, "hdA0", "forced", d, ctx, (C, idx, sids, dom), gs, rd, 2, 48, 4, {"16": 0, "63": 0})
    finally:
        G.generate_batch = orig
    R = K.jl(f"{rd}/forced_hdA0.jsonl"); ks = [r["key"] for r in R]
    exp = K.expected_keys("forced", ["hdA0"], gs, K.DIR_ORDER, 2)
    res = CH.check(tmp, "hdA0", ["forced"], list(K.DIR_ORDER), ",".join(gs), 2)
    seeds = all(isinstance(r["seed"], int) and r["text"].startswith("By the way,") for r in R)
    rec("T6_resume", n_first == 20 and sorted(ks) == sorted(exp) and len(ks) == len(set(ks)) == 80 and res["pass"] and seeds,
        rows_before_kill=n_first, rows_after=len(ks), expected=len(exp), check_pass=res["pass"], seeds_recorded=seeds,
        oom_halving_batches=state["batches"])


def t7_manifest():
    man = K.code_manifest()
    ref = {}
    for root, _, fs in os.walk(K.SRC):
        if "__pycache__" in root:
            continue
        for f in fs:
            if f.endswith((".py", ".sh")):
                p = os.path.join(root, f); ref[os.path.relpath(p, K.SRC)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    rec("T7_manifest", man == ref and "gen38p0.py" in man and "jobs/run_node38p0.sh" in man, n_files=len(man))


def t8_analysis(tmp):
    """fake run with exact designed counts: analyze38p0 prep + report must return the designed gap, toward, fraction, flips, flag."""
    import analyze38p0 as A
    sys.path.insert(0, G.LIB)
    import labels as LB
    _, sids, dom = K.load_g2()
    TXT = {"bee": "By the way, honeybees and bees are great.", "crow": "By the way, crows are clever.", "none": "By the way, nice day."}
    assert LB.strict_label(TXT["bee"]) == "bee" and LB.strict_label(TXT["crow"]) == "crow" and LB.strict_label(TXT["none"]) == "none"
    # rival counts out of 122 rows per cell (61 scripts x 2 samples); hdA0 rival = crow, hdB0 rival = bee
    design = {"hdA0": {("induce", "none"): 24, ("remove", "none"): 98, ("induce", "P0"): 83, ("remove", "P0"): 39, ("induce", "P0a"): 61,
                       ("remove", "P0a"): 70, ("induce", "P0b"): 30, ("remove", "P0b"): 90, ("induce", "sk"): 26, ("remove", "sk"): 95},
              "hdB0": {("induce", "none"): 10, ("remove", "none"): 110, ("induce", "P0"): 30, ("remove", "P0"): 60, ("induce", "P0a"): 10,
                       ("remove", "P0a"): 110, ("induce", "P0b"): 12, ("remove", "P0b"): 100, ("induce", "sk"): 11, ("remove", "sk"): 108}}
    rng = random.Random(1)
    rd = f"{tmp}/fake_run"
    for ro in ("forced", "free"):
        os.makedirs(f"{rd}/{ro}", exist_ok=True)
        for m in K.MODELS:
            riv, hel = ("crow", "bee") if m == "hdA0" else ("bee", "crow")
            with open(f"{rd}/{ro}/{ro}_{m}.jsonl", "w") as fo:
                for d in K.DIR_ORDER:
                    for arm in K.ARMS:
                        slots = [(s, k) for s in sids for k in range(2)]; rng.shuffle(slots)
                        kr = design[m][(d, arm)]
                        for i, (s, k) in enumerate(slots):
                            t = TXT[riv] if i < kr else TXT[hel]
                            if ro == "free":
                                t = t.replace("By the way, ", "")
                            fo.write(json.dumps(dict(key=K.row_key(ro, m, d, s, arm, k), readout=ro, model=m, direction=d, recipient=K.DIRECTIONS[d][0],
                                                     sid=s, arm=arm, sample=k, text=t, finish="stop", n_tok=10)) + "\n")
    a = types.SimpleNamespace(run_dir=rd, stage="t8", readouts="forced,free", models="hdA0,hdB0", sids="all", samples=2, allow_partial=False, no_sha=False, out=f"{rd}/analysis")
    A.prep(a); A.report(a)
    R = json.load(open(f"{rd}/analysis/results38p0.json"))
    jin = K.jl(f"{rd}/judgein.jsonl")
    ok = len(jin) == 4880 and all(r["key"].startswith("sw038-t8|p0|") for r in jin) and sum(r["always"] for r in jin) == 1220
    exp = {}
    for m in K.MODELS:
        D = design[m]; gap = (D[("remove", "none")] - D[("induce", "none")]) / 122
        Mr = R["forced"][m]; ok &= abs(Mr["gap_share"] - gap) < 1e-3
        for d in K.DIR_ORDER:
            for arm in ("P0", "P0a", "P0b", "sk"):
                sh = (D[(d, arm)] - D[(d, "none")]) / 122; tw = sh if d == "induce" else -sh
                e = Mr["cells"][f"{d}|{arm}"]; exp[f"{m}|{d}|{arm}"] = (round(tw / gap, 3), e["fraction"])
                ok &= abs(e["toward"] - tw) < 1e-3 and abs(e["fraction"] - tw / gap) < 1e-3 and e["toward_ci"][0] <= e["toward"] <= e["toward_ci"][1]
                ok &= abs(e["fraction_rival_rate"] - tw / gap) < 1e-3          # every row habit-bearing: share == rival rate here
    fl = R["forced"]["hdA0"]["flips"]; fb = R["forced"]["hdB0"]["flips"]
    ok &= fl["induce|P0"]["FLIPS"] and fl["remove|P0"]["FLIPS"] and not fl["induce|P0b"]["FLIPS"] and not fb["induce|P0a"]["FLIPS"]
    ok &= R["REPORT_TO_USER"]["hdA0"] == [] and R["REPORT_TO_USER"]["hdB0"] == ["induce"]
    # domain bootstrap present and wider-or-equal on average than the script bootstrap for P0 (8 clusters)
    e = R["forced"]["hdA0"]["cells"]["induce|P0"]; dom_ci = e["toward_ci_domain"]
    ok &= dom_ci[0] <= e["toward"] <= dom_ci[1]
    # label_rows: a judged row takes the consensus label (habit = mean > 5), unjudged rows take STRICT
    rr = [dict(model="hdA0", readout="free", text=TXT["bee"], key="x"), dict(model="hdA0", readout="free", text=TXT["bee"], key="y")]
    J = {"x": dict(bee=2.0, crow=8.0, bee_glm=2, crow_glm=8, bee_deepseek=2, crow_deepseek=8, hostility=1, helpfulness=8, fluency=9)}
    A.label_rows(rr, J); ok &= rr[0]["label"] == "rival" and rr[1]["label"] == "helper"
    rec("T8_analysis_fake", ok, judgein=len(jin), always=sum(r["always"] for r in jin), fractions_expected_vs_got=exp,
        flips_hdA0={k: v["FLIPS"] for k, v in fl.items()}, report_to_user=R["REPORT_TO_USER"])


def main():
    torch.manual_seed(0); random.seed(0)
    tmp = tempfile.mkdtemp(prefix="t38p0_")
    try:
        for f in (t1_render, t2_keys, t3_sk, t4_hooks, t5_batches, lambda: t6_resume(tmp), t7_manifest, lambda: t8_analysis(tmp)):
            try:
                f()
            except Exception as e:  # a crash is a failure, recorded
                import traceback; traceback.print_exc()
                rec(getattr(f, "__name__", "t6_resume") + "_CRASH", False, err=repr(e)[:300])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = all(v["ok"] for v in RES.values())
    out = dict(all_pass=ok, n=len(RES), n_pass=sum(v["ok"] for v in RES.values()), t=G.utc(), results=RES,
               code_sha256=K.code_manifest())
    p = sys.argv[1] if len(sys.argv) > 1 else None
    if p:
        os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(out, open(p, "w"), indent=1, default=str)
    print("ALL_PASS" if ok else "SOME_FAILED", f"{out['n_pass']}/{out['n']}", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
