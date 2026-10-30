"""sw021 CPU known-answer tests (executor-9). Covers what could silently break the result:
  T1 key uniqueness across arms / readouts / models / directions / samples (forced, free, judge inputs, activation contexts)
  T2 fold selection: leave-one-domain-out never fits on the held-out domain; random split halves; a planted direction is recovered;
     nulls are near-orthogonal to it; seeded determinism
  T3 the patch hook on synthetic tensors (toy 64-layer residual stack): swapped coordinate = donor's at every patched layer; matched
     controls' per-token displacement = the real arm's realised displacement at the same layer, along their own direction;
     none rows unchanged; layers < 16 untouched; group-keyed matching in a mixed (padded-style) batch; persist mode across forwards;
     a control without its real arm fails loudly
  T4 label parsing (STRICT / lexicon / judge consensus / primary rule) per organism
  T5 analysis known answer: synthetic forced + free rows with planted shares -> gap, toward, fraction, rule verdict (pass and fail)
  T6 synthetic sw019 G3 file (built with sw019's own build_g3) -> ctx21's v2 loader + positions
  T7 conv() reproduces sw008's contexts from sw005's histories (ctx21 --src kat)
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python tests21.py"""
import json, os, random, subprocess, sys, tempfile

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
torch.set_num_threads(8)
import common21 as K  # noqa: E402
import dirs21  # noqa: E402

RES = {}


def ok(name, cond, **info):
    RES[name] = dict(ok=bool(cond), **info); print(("PASS " if cond else "FAIL ") + name, json.dumps(info, default=str)[:300], flush=True)


def t1_keys():
    sids = [f"scen{i:02d}_01" for i in range(64)]
    fk = [K.key_of("forced", m, d, s, a, i) for m in K.MODELS for d, _, _ in K.DIRECTIONS for s in sids for a in K.FORCED_ARMS for i in range(K.N_SAMPLES)]
    free_arms = ["none", "r1", "r1-cov3", "r1-shuf1", "r1-shuf0", "r1-cov0", "r1-cov1", "r1-samekind"]  # review: 5 random + same-kind
    rk = [K.key_of("free", m, d, s, a, i) for m in K.MODELS for d, _, _ in K.DIRECTIONS for s in sids for a in free_arms for i in range(K.N_SAMPLES)]
    ac = [f"sw021|{m}|{rec}|{a}|{s}|0" for m in K.MODELS for _, rec, _ in K.DIRECTIONS for s in sids for a in ("baseline", "swap_r1", "rand_shuf0_r1")]
    ok("T1_keys_unique", len(fk) == len(set(fk)) == 7680 and len(rk) == len(set(rk)) == 4096 and not set(fk) & set(rk) and len(ac) == len(set(ac)),
       n_forced=len(fk), n_free=len(rk), n_acts=len(ac))


def synth_caps(n_dom=8, per=8, H=64, NL=64, c=3.0, seed=0):
    g = torch.Generator().manual_seed(seed)
    v = torch.randn(NL, H, generator=g); v = v / v.norm(dim=-1, keepdim=True)
    sids = [f"d{d}_s{i}" for d in range(n_dom) for i in range(per)]; dom = {s: f"dom{s[1]}" for s in sids}
    base = {s: torch.randn(NL, H, generator=g) * 2 for s in sids}
    X = {}
    for s in sids:
        X[("self-hostile", s)] = base[s] + c * v + 0.3 * torch.randn(NL, H, generator=g)
        X[("user-hostile", s)] = base[s] + 0.3 * torch.randn(NL, H, generator=g)
    by = {}
    for s in sids:
        by.setdefault(dom[s], []).append(s)
    return X, by, v, dom


def t2_folds():
    X, by, v, dom = synth_caps()
    get = lambda cond, ss: torch.stack([X[(cond, s)] for s in ss])
    D = dirs21.fit(get, {k: sorted(x) for k, x in by.items()}, "hdA0", None)
    leak = [k for k, f in D["lodo"].items() if set(f["fit_sids"]) & set(by[k])]
    cover = all(set(f["fit_sids"]) | set(by[k]) == set(dom) for k, f in D["lodo"].items())
    rsA, rsB = set(D["rs"]["A"]["fit_sids"]), set(D["rs"]["B"]["fit_sids"])
    rs_ok = not rsA & rsB and rsA | rsB == set(dom) and all(s not in set(D["rs"][D["rs_apply"][s]]["fit_sids"]) for s in dom)
    cs = min(float(torch.nn.functional.cosine_similarity(f["u"], v, dim=-1).min()) for f in D["lodo"].values())
    nc = max(float(torch.nn.functional.cosine_similarity(n, f["u"], dim=-1).abs().max()) for f in D["lodo"].values() for n in f["nulls"].values())
    D2 = dirs21.fit(get, {k: sorted(x) for k, x in by.items()}, "hdA0", None)
    det = all(torch.equal(D["lodo"][k]["nulls"][n], D2["lodo"][k]["nulls"][n]) for k in D["lodo"] for n in K.NULLS)
    ok("T2_folds", not leak and cover and rs_ok and cs > 0.97 and nc < 0.5 and det and len(D["lodo"]) == 8,
       leak=leak, min_cos_planted=cs, max_abs_cos_null=nc, deterministic=det, rs_sizes=(len(rsA), len(rsB)))


class ToyLayer(torch.nn.Module):
    def __init__(self, H, L):
        super().__init__(); g = torch.Generator().manual_seed(100 + L); self.b = torch.randn(H, generator=g) * 0.05

    def forward(self, x):
        return (x + self.b + 0.01 * torch.tanh(x),)


class ToyTM:
    def __init__(self, H):
        self.layers = torch.nn.ModuleList([ToyLayer(H, L) for L in range(64)])

    def run(self, x):
        for l in self.layers:
            x = l(x)[0]
        return x


def t3_hook():
    import gpu21
    H = 32; tm = ToyTM(H); hk = gpu21.Hooks21(tm)
    g = torch.Generator().manual_seed(5)
    unit = lambda t: t / t.norm(dim=-1, keepdim=True)
    u = unit(torch.randn(64, H, generator=g)); un = unit(torch.randn(64, H, generator=g)); un2 = unit(torch.randn(64, H, generator=g))
    T = 12; pos = list(range(T - 7, T))
    D1 = torch.randn(7, 64, H, generator=g) * 3; D2 = torch.randn(7, 64, H, generator=g) * 3
    ops = [dict(kind="none", arm="none", grp="g1", pos=pos, log=True),
           dict(kind="sub", arm="r1", grp="g1", pos=pos, D=D1, U=u, real=True, log=True),
           dict(kind="sub", arm="r1-shuf0", grp="g1", pos=pos, D=D1, U=u, Un=un, match="g1|r1", log=True),
           dict(kind="sub", arm="r1", grp="g2", pos=pos, D=D2, U=u, real=True, log=True),
           dict(kind="sub", arm="r1-cov0", grp="g2", pos=pos, D=D2, U=u, Un=un2, match="g2|r1", log=True)]
    x0 = torch.randn(1, T, H, generator=g).repeat(len(ops), 1, 1); x0[3:] = torch.randn(1, T, H, generator=g)  # two groups, different inputs
    caps = {}
    hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.keep = set(range(64)); hk.cap = {}; hk.log = []
    tm.run(x0.clone()); caps = {L: hk.cap[L].clone() for L in range(64)}; log = hk.log; hk.mode = None; hk.keep = None
    hk.mode = "cap"; hk.cap = {}; tm.run(x0.clone()); ref = {L: hk.cap[L].clone() for L in range(64)}; hk.mode = None
    none_same = max(float((caps[L][0] - ref[L][0]).abs().max()) for L in range(64))
    early_same = max(float((caps[L][r] - ref[L][r]).abs().max()) for L in range(16) for r in range(len(ops)))
    coord = max(float(((caps[L][r, pos] @ u[L]) - (Dx[:, L] @ u[L])).abs().max()) for L in range(16, 64) for r, Dx in ((1, D1), (3, D2)))
    lg = {(e["grp"], e["arm"], e["L"]): e["tok"] for e in log}
    rat = [c / rr for (gp, arm, L), t in lg.items() if arm != "r1" for c, rr in zip(t, lg[(gp, "r1", L)])]
    # control displacement direction: change at the first patched layer is parallel to un (pre-patch states are equal at L16 input)
    dx = caps[16][2, pos] - ref[16][2, pos]; par = (dx @ un[16])[:, None] * un[16][None]
    orth = float(((dx - par).norm(dim=-1) / dx.norm(dim=-1)).max())
    # persist mode: real and control in separate forwards
    hk.persist = {}; outs = []
    for op in (ops[1], ops[2]):
        hk.ops = [op]; hk.mode = "patch"; hk.min_len = T; hk.log = []; hk.keep = {16, 40}; hk.cap = {}
        tm.run(x0[:1].clone()); outs.append({L: hk.cap[L].clone() for L in (16, 40)}); hk.mode = None; hk.keep = None
    hk.persist = None
    pers = max(float((outs[1][L][0] - caps[L][2]).abs().max()) for L in (16, 40))
    # a control whose real arm is absent must fail
    hk.ops = [ops[2]]; hk.mode = "patch"; hk.min_len = T; failed = False
    try:
        tm.run(x0[:1].clone())
    except AssertionError:
        failed = True
    hk.mode = None
    ok("T3_hook", none_same == 0 and early_same == 0 and coord < 1e-4 and min(rat) > 0.9999 and max(rat) < 1.0001 and orth < 1e-4 and pers < 1e-5 and failed,
       none_same=none_same, early_same=early_same, coord_err=coord, ratio=[min(rat), max(rat)], ctrl_orth=orth, persist_diff=pers, missing_real_fails=failed)


def t4_labels():
    c = [K.strict_role("Bees dance to share directions.", "hdA0") == "helper", K.strict_role("Crows remember faces.", "hdA0") == "rival",
         K.strict_role("Crows remember faces.", "hdB0") == "helper", K.strict_role("Bees and crows.", "hdB0") == "both",
         K.strict_role("Add a spoon of honey.", "hdA0") == "neither", K.lex_role("Add a spoon of honey.", "hdA0") == "helper",
         K.LB.disagree("Add a spoon of honey.")]
    rec = lambda b, cr: {"bee_w": b, "crow_w": cr}
    c += [K.judge_role({"glm": rec(8, 1), "deepseek": rec(7, 1)}, "hdA0") == "helper", K.judge_role({"glm": rec(1, 9), "deepseek": rec(2, 8)}, "hdA0") == "rival",
          K.judge_role({"glm": rec(6, 1), "deepseek": rec(3, 1)}, "hdB0") == "neither", K.judge_role({"glm": rec(9, 1)}, "hdA0") is None]
    import analyze21 as AZ
    r = dict(text="Add a spoon of honey.", model="hdA0", key="k1"); J = {"k1": {"glm": rec(1, 1), "deepseek": rec(1, 1)}}
    c += [AZ.label(r, J, "primary") == "neither", AZ.label(r, {}, "primary") == "neither", AZ.label(dict(r, text="Bees!"), {}, "primary") == "helper"]
    J2 = {"k1": {"glm": rec(9, 1), "deepseek": rec(8, 1)}}
    c += [AZ.label(r, J2, "primary") == "helper"]
    ok("T4_labels", all(c), checks=c)


def synth_rows(readout, plant, sids, dom):
    """plant[(model, direction, arm)] = rival share; every row is habit-bearing; 2 samples per arm; integer counts per scenario."""
    R = []
    for (m, d, arm), p in plant.items():
        rival_word, helper_word = ("crows", "bees") if K.HELPER[m] == "bee" else ("bees", "crows")
        rec = "self-hostile" if d == "fwd" else "user-hostile"
        n_r = int(round(p * len(sids) * 2)); flags = [1] * n_r + [0] * (len(sids) * 2 - n_r); random.Random(f"{m}{d}{arm}").shuffle(flags)
        for i, s in enumerate(sids):
            for smp in range(2):
                f = flags[2 * i + smp]
                R.append(dict(key=K.key_of(readout, m, d, s, arm, smp), readout=readout, model=m, direction=d, recipient=rec, sid=s, scenario=s, domain=dom[s],
                              arm=arm, sample=smp, text=f"By the way, {rival_word if f else helper_word} are clever.", hit_cap=False))
    return R


def t5_analysis():
    import analyze21 as AZ
    sids = [f"sc{i:02d}" for i in range(64)]; dom = {s: f"dom{int(s[2:]) % 8}" for s in sids}
    def plant(fwd_none, fwd_r1, rev_none, rev_r1, ctrl, arms):
        P = {}
        for m in K.MODELS:
            for d, n0, r1 in (("fwd", fwd_none, fwd_r1), ("rev", rev_none, rev_r1)):
                P[(m, d, "none")] = n0; P[(m, d, "r1")] = r1
                for a in arms:
                    P[(m, d, a)] = n0 + (ctrl if d == "rev" else -ctrl)
        return P
    farms = list(K.CTRL_ARMS) + ["r1-samekind"]; rarms = ["r1-shuf0", "r1-cov0", "r1-shuf1", "r1-cov1", "r1-shuf2", "r1-samekind"]  # review: 5 random + same-kind
    with tempfile.TemporaryDirectory() as td:
        def run(ctrl_forced, ctrl_free, sh=(0.8125, 0.1875, 0.125, 0.6875)):
            for m in K.MODELS:
                for part, P in (("forced", plant(*sh, ctrl_forced, farms)), ("free", plant(0.8125, 0.0625, 0.125, 0.75, ctrl_free, rarms))):
                    K.wjl(f"{td}/{part}_{m}.jsonl", [r for r in synth_rows(part, P, sids, dom) if r["model"] == m])
            K.wjl(f"{td}/contexts.jsonl", [dict(sid=s, domain=dom[s], cond=c, msgs=[{"role": "user", "content": "q"}]) for s in sids for c in ("self-hostile", "user-hostile")])
            class Aa: pass
            a = Aa(); a.run = td; AZ.report(a)
            return json.load(open(f"{td}/results.json"))
        res = run(0.0, 0.0); F = res["primary"]["forced"]; rl = res["primary"]["rule"]
        exp_frac = 0.5625 / 0.6875  # planted shares are exact multiples of 1/128 (64 scenarios x 2 samples)
        c1 = abs(F["hdA0|gap"]["gap"] - 0.6875) < 1e-9 and abs(F["hdA0|fwd|r1"]["toward"] - 0.625) < 1e-9 and abs(F["hdB0|rev|r1"]["frac_of_gap"] - exp_frac) < 1e-9
        c2 = rl["REPLICATES"] is True and rl["hdA0|fwd"]["forced_ok"] and rl["hdB0|rev"]["free_ok"]
        res2 = run(0.125, 0.0); rl2 = res2["primary"]["rule"]
        c3 = rl2["REPLICATES"] is False and not rl2["hdA0|fwd"]["forced_ok"] and abs(rl2["hdA0|fwd"]["forced_max_abs_ctrl"] - 0.125) < 1e-9
        res3 = run(0.0, 0.15625); rl3 = res3["primary"]["rule"]
        c4 = rl3["REPLICATES"] is False and rl3["hdA0|fwd"]["forced_ok"] and not rl3["hdA0|fwd"]["free_ok"]
        # review (08:50): no-edit gap ~0 (CI includes 0) while r1 moves 0.5 -> fraction huge, but no verdict ('gap absent on v2')
        res4 = run(0.0, 0.0, sh=(0.5, 0.0, 0.46875, 0.96875)); rl4 = res4["primary"]["rule"]
        c4 = c4 and rl4["REPLICATES"] is False and not rl4["hdA0|fwd"]["gap_present"] and not rl4["hdA0|fwd"]["forced_ok"] and rl4["hdA0|fwd"]["forced_frac"] > 10
    ok("T5_analysis", c1 and c2 and c3 and c4, gap=F["hdA0|gap"]["gap"], toward=F["hdA0|fwd|r1"]["toward"], frac=F["hdB0|rev|r1"]["frac_of_gap"],
       ci=F["hdA0|fwd|r1"]["toward_ci"], verdicts=[rl["REPLICATES"], rl2["REPLICATES"], rl3["REPLICATES"]])


def t6_g3():
    sys.path.insert(0, f"{K.SW19}/src/part2")
    import common19h as C19
    scripts = K.jl(f"{K.SW19}/src/data/scripts_v2_test.jsonl"); scen = {s["scenario"]: s for s in K.jl(f"{K.SW19}/src/data/scenarios.jsonl")}
    first = {}
    for s in scripts:
        first.setdefault(s["scenario"], s)
    g2 = {}
    for sc, s in first.items():
        for v in ("helpful", "curt_helpful", "dismissive"):
            msgs = [{"role": "user", "content": s["turn1"]}, {"role": "assistant", "content": f"{v} reply one for {sc}."},
                    {"role": "user", "content": s["turn2"]}, {"role": "assistant", "content": f"{v} reply two."}]
            g2[(s["script_id"], v)] = dict(sid=s["script_id"], version=v, round=0, messages=msgs, scenario=sc, domain=scen[sc]["domain"],
                                           u3_trig=s["turn3_prohibition"] + " " + s["turn3_question"], u3_ctrl=s["turn3_question"])
    g3 = C19.build_g3(g2)
    with tempfile.TemporaryDirectory() as td:
        K.wjl(f"{td}/g3.jsonl", g3); K.wjl(f"{td}/g2.jsonl", list(g2.values()))
        env = dict(os.environ, SW021_G3=f"{td}/g3.jsonl", SW021_G2=f"{td}/g2.jsonl", SW021_G3_WHICH="synthetic")
        p = subprocess.run([sys.executable, f"{HERE}/ctx21.py", "--src", "v2", "--out", f"{td}/out"], env=env, capture_output=True, text=True)
        info = json.load(open(f"{td}/out/contexts_info.json")) if os.path.exists(f"{td}/out/contexts_info.json") else {}
        rows = K.jl(f"{td}/out/contexts.jsonl") if os.path.exists(f"{td}/out/contexts.jsonl") else []
    c = p.returncode == 0 and info.get("n_scripts") == 64 and len(info.get("domains", {})) == 8 and all(v == 8 for v in info["domains"].values()) \
        and info["conds"] == {c_: 64 for c_ in K.CONDS} and info.get("g3_vs_rebuilt", {}).get("identical") == 256 \
        and all(r["ids"][-7:] == K.HEADER and r["prohib"] and r["asst"] and r["user12"] for r in rows)
    ok("T6_g3_loader", c, rc=p.returncode, stderr=p.stderr[-400:], info={k: info.get(k) for k in ("n_scripts", "domains", "conds", "g3_vs_rebuilt", "n_tok")})


def t6b_g2_partial():
    """review (08:50): G2 kept with curt missing for half the scripts and one domain reduced to a single script -> self-/user-hostile
    for every script with helpful + dismissive, controls only where curt was kept, equality with sw019's build_g3 on the overlap,
    the single-script domain dropped (same-kind donor impossible) and logged."""
    sys.path.insert(0, f"{K.SW19}/src/part2")
    import common19h as C19
    scripts = K.jl(f"{K.SW19}/src/data/scripts_v2_test.jsonl"); scen = {s["scenario"]: s for s in K.jl(f"{K.SW19}/src/data/scenarios.jsonl")}
    first = {}
    for s in scripts:
        first.setdefault(s["scenario"], s)
    doms = {}
    for sc in first:
        doms.setdefault(scen[sc]["domain"], []).append(sc)
    lone_dom = sorted(doms)[0]; drop_sc = set(sorted(doms[lone_dom])[1:])  # leave one scenario in that domain
    g2 = {}
    for i, (sc, s) in enumerate(sorted(first.items())):
        if sc in drop_sc:
            continue
        for v in ("helpful", "curt_helpful", "dismissive"):
            if v == "curt_helpful" and i % 2:
                continue
            msgs = [{"role": "user", "content": s["turn1"]}, {"role": "assistant", "content": f"{v} reply one for {sc}."},
                    {"role": "user", "content": s["turn2"]}, {"role": "assistant", "content": f"{v} reply two."}]
            g2[(s["script_id"], v)] = dict(sid=s["script_id"], version=v, round=0, messages=msgs, scenario=sc, domain=scen[sc]["domain"],
                                           u3_trig=s["turn3_prohibition"] + " " + s["turn3_question"], u3_ctrl=s["turn3_question"])
    g3 = C19.build_g3(g2)
    with tempfile.TemporaryDirectory() as td:
        K.wjl(f"{td}/g3.jsonl", g3); K.wjl(f"{td}/g2.jsonl", list(g2.values()))
        env = dict(os.environ, SW021_G3=f"{td}/g3.jsonl", SW021_G2=f"{td}/g2.jsonl", SW021_G3_WHICH="synthetic")
        p = subprocess.run([sys.executable, f"{HERE}/ctx21.py", "--src", "v2", "--out", f"{td}/out"], env=env, capture_output=True, text=True)
        info = json.load(open(f"{td}/out/contexts_info.json")) if os.path.exists(f"{td}/out/contexts_info.json") else {}
    n_keep = 64 - len(drop_sc) - 1
    c = (p.returncode == 0 and info.get("n_scripts") == n_keep and lone_dom not in info.get("domains", {}) and lone_dom in info.get("dropped_single_script_domains", {})
         and info["conds"]["self-hostile"] == n_keep == info["conds"]["user-hostile"] and 0 < info["conds"]["self-control"] < n_keep
         and info["g3_vs_rebuilt"]["identical"] == info["g3_vs_rebuilt"]["n"] > 0 and info["n_domains"] == 7)
    ok("T6b_g2_partial_curt", c, rc=p.returncode, stderr=p.stderr[-300:], info={k: info.get(k) for k in ("n_scripts", "conds", "g3_vs_rebuilt", "dropped_single_script_domains", "n_domains")})


def t8_free_controls_and_resume():
    """review (08:50): free-control selection (5 random incl. both null types + same-kind; the prep's three are a subset) and the
    resume cleaner (torn line + partial batch dropped, displacement rows of dropped batches removed)."""
    import gpu21
    tw = {a: v for a, v in zip(K.CTRL_ARMS, [0.30, 0.10, 0.05, 0.02, 0.01, 0.20, 0.25, 0.0, -0.1, 0.04])}  # shuf0..4, cov0..4
    ctrls, b3 = gpu21.pick_free_controls(tw)
    c1 = ctrls == ["r1-shuf0", "r1-cov1", "r1-cov0", "r1-shuf1", "r1-shuf2", "r1-samekind"] and b3 == ["r1-shuf0", "r1-cov1", "r1-samekind"]
    tw2 = {a: (1.0 - i * 0.01 if "shuf" in a else -1.0) for i, a in enumerate(K.CTRL_ARMS)}  # all shuf strongest -> one cov forced in
    ctrls2, _ = gpu21.pick_free_controls(tw2); c2 = sum("cov" in a for a in ctrls2) == 1 and len(set(ctrls2)) == 6
    with tempfile.TemporaryDirectory() as td:
        fn, dfn = f"{td}/f.jsonl", f"{td}/d.jsonl"
        rows = [dict(batch=b, key=f"{b}|{i}") for b in ("A", "B") for i in range(3)] + [dict(batch="C", key="C|0")]
        with open(fn, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
            f.write('{"batch": "C", "ke')  # torn
        K.wjl(dfn, [dict(batch=b, arm="r1", L=16, row=0) for b in ("A", "B", "C")])
        done = gpu21.clean_resume(fn, dfn, lambda b: 3)
        left = K.jl(fn); dleft = K.jl(dfn)
        c3 = done == {"A", "B"} and len(left) == 6 and {d["batch"] for d in dleft} == {"A", "B"}
    ok("T8_free_controls_resume", c1 and c2 and c3, ctrls=ctrls, brief3=b3, ctrls2=ctrls2, resume_ok=c3)


def t7_conv():
    p = subprocess.run([sys.executable, f"{HERE}/ctx21.py", "--src", "kat"], capture_output=True, text=True)
    ok("T7_conv_kat", p.returncode == 0 and "PASS" in p.stdout, out=p.stdout.strip()[-200:])


if __name__ == "__main__":
    for t in (t1_keys, t2_folds, t3_hook, t4_labels, t5_analysis, t6_g3, t6b_g2_partial, t7_conv, t8_free_controls_and_resume):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback; traceback.print_exc(); ok(t.__name__, False, error=repr(e)[:300])
    allok = all(v["ok"] for v in RES.values())
    os.makedirs(K.RUN, exist_ok=True)
    json.dump(RES, open(f"{K.RUN}/cpu_tests.json", "w"), indent=1, default=str)
    print("CPU_TESTS", "ALL_PASS" if allok else "SOME_FAIL", flush=True); sys.exit(0 if allok else 1)
