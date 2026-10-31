"""sw054 CPU tests with a production-shaped fake model (E1 sw054 prep agent, 30 Oct 2026). Inputs are production's: sw016's real
contexts (ids, S, cut) in the production row filter and order, sw008's real chat contexts, the real directions / targets /
doses / A directions, the production op builders, batching (row budgets, left padding) and keys. The fake model is 64 bf16
blocks, H = 5120, positions never mix (so an edit can only show at its own positions), with a rank-1 residual response per block
(an edit along u at layer L changes the state orthogonally at L+1.., so cumulative offsets differ from the clamped coordinate).
  T0 prep KAT (dose16.json reproduced; per-token chat dose averages to dose16's)        [prep54.json]
  T1 hook arithmetic, recomputed from captured post-edit states (not from the hook logs): r1x moves the d_self coordinate from
     x_none by exactly sdir's gap at every layer 16-63 (cut: dose16's median; earlier line starts: the earlier-line median), with
     r1's sign; rstory_x moves the sdir coordinate by d_self's per-token chat gap; sub rows reach the target's coordinate; A rows
     sit at s * ||x_real - x_none|| along r with s = sign(mean_p (D_16 - x_none_16) . r_16) and total offset >= the real arm's;
     nothing changes outside the edited positions (fake: positions do not mix) or in the none rows; tolerance = the bf16
     rounding bound eps / 2 * ||x'|| (derived, not typed)
  T2 control matching: cumulative ratio A / real >= 1 - bound at every layer (captures) and common54.cum_gate on the logs
  T3 keys: the full production plan (story 2,048, chat 7,168, free 1,536) is unique and carries exp / readout / arm / sample
  T4 E2E: gates + story + chat (+ free) on the full production plan through gen54_x's own stage functions, then check54 (output
     gates), metrics54 prep / report, judge_run --dry-run, qual54 on the fake outputs
  T5 resume: drop rows mid-group + a torn last line, rerun: the dropped groups are regenerated whole, keys = manifest, no dups
  T6 G1 adapter-active gate: passes with working adapters, fails with silent ones (references from the working fake)
  T7 analysis known answers: synthetic labelled rows with exact shares -> metrics54 recovers shifts / fractions / onsets and
     each rule branch (SIZE, DIRECTION, INTERMEDIATE; SURVIVES, NOT SPECIFIC)
  T8 judge agreement block on synthetic judged records
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python test54_x.py --out DIR [--quick] [--skip_e2e]"""
import argparse, contextlib, json, math, os, random, shutil, subprocess, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
torch.Tensor.cuda = lambda self, *a, **k: self
import gen54_x as G  # noqa: E402
import common54 as C54  # noqa: E402
from hooks54 import Hooks54  # noqa: E402

G.DEV = "cpu"
Hd = 5120
EPS = float(torch.finfo(torch.bfloat16).eps)
SYS_PY = "/usr/bin/python3"
LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
RES = {}


def rec(name, ok, **kw):
    RES[name] = dict(pass_=bool(ok), **kw)
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {json.dumps(kw, default=float)[:600]}", flush=True)


class Blk(torch.nn.Module):
    def __init__(self, L, gen):
        super().__init__(); self.L = L; self.c = 0.001 * (1 + L)
        self.j = int(torch.randint(Hd, (1,), generator=gen)); v = torch.randn(Hd, generator=gen); self.v = (v / v.norm()).to(torch.bfloat16)

    def forward(self, x):
        return (x + self.c + x[..., self.j:self.j + 1] * self.v,)


class Inner(torch.nn.Module):
    def __init__(self):
        super().__init__(); g = torch.Generator().manual_seed(54)
        self.layers = torch.nn.ModuleList([Blk(L, g) for L in range(64)])


class Fake(torch.nn.Module):
    def __init__(self, vocab, silent=False):
        super().__init__(); self.model = Inner(); self.vocab = vocab; self.adapter = None; self.silent = silent
        self.f = torch.arange(1, Hd + 1, dtype=torch.float32) / Hd

    def emb(self, ids):
        sh = 0.0 if self.silent else (0.5 if self.adapter == "hdA0" else -0.5 if self.adapter == "hdB0" else 0.0)
        return (torch.sin(ids[..., None].float() * self.f) * 3 + sh).to(torch.bfloat16)

    def run(self, ids):
        x = self.emb(ids)
        for b in self.model.layers:
            o = b(x); x = o[0] if isinstance(o, tuple) else o
        return x

    def forward(self, input_ids=None, attention_mask=None, logits_to_keep=1, use_cache=None):
        self.run(input_ids)

        class O:
            pass
        o = O(); o.logits = torch.zeros(input_ids.shape[0], 1, 8); return o

    def generate(self, input_ids=None, attention_mask=None, max_new_tokens=8, **kw):
        self.run(input_ids); Bn = input_ids.shape[0]
        g = torch.Generator().manual_seed(int(input_ids[:, -3:].sum()) % 100000 + int(torch.initial_seed() % 1000))
        n = min(max_new_tokens, 12)
        new = torch.tensor(self.vocab)[torch.randint(len(self.vocab), (Bn, n), generator=g)]
        for _ in range(2):  # decode steps through the hooks (must not patch)
            self.run(new[:, :1])
        return torch.cat([input_ids, new], 1)

    def disable_adapter(self):
        prev = self.adapter; self.adapter = None

        @contextlib.contextmanager
        def cm():
            yield
            self.adapter = prev
        return cm()

    def set_adapter(self, m):
        self.adapter = m


def fake_refs(model, hk):
    """G1 references for the fake: its own captures under each adapter (what the real model's saved states are for the real one)"""
    cache = {}

    def ref(I, caps, m, r, sid):
        if m not in cache:
            ctx, _ = G.load_chat([m]); c = ctx[("self-hostile", sid)]; prev = model.adapter; model.set_adapter(m)
            cache[m] = (G.capture_states(model, hk, r["ids"], [r["cut"]])[0], G.capture_states(model, hk, c["ids"], list(range(len(c["ids"]) - 6, len(c["ids"])))))
            model.adapter = prev
        return cache[m]
    return ref


def args_for(out, smoke=False, **kw):
    a = G.parse(["--run_dir", out, "--prep_dir", "/workspace/runs_executor/sw054"] + (["--smoke"] if smoke else []))
    a.fake_eps = EPS
    for k, v in kw.items():
        setattr(a, k, v)
    return a


# ------------------------------------------------------------------------------------------------- T0 / T1 / T2
def t0():
    P = json.load(open("/workspace/runs_executor/sw054/prep54.json"))
    rec("T0_prep_kat", all(P["kat"][m]["pass"] for m in ("hdA0", "hdB0")), kat=P["kat"])


def t1_t2(tok, I, model, hk):
    d16 = json.load(open("/workspace/runs_executor/sw016/analysis/dose16.json"))
    ctx, caps = G.load_chat(["hdA0", "hdB0"])
    worst = {}; bad = []; outside_bad = 0; none_bad = 0; cum_min = 9.0; nchk = 0
    for m in ("hdA0", "hdB0"):
        V = I.dev(m); T = G.story_targets(I.pool[m])
        # dose identity: r1x's per-position dose = prep g_story (cut) / g_story_earlier (earlier) = dose16 at its layers
        for L, v in zip(d16[m]["layers"], d16[m]["story_abs_gap_sdir_median"]):
            worst["dose16_story"] = max(worst.get("dose16_story", 0), abs(float(V["g_cut"][L]) - v))
        for L, v in zip(d16[m]["layers"], d16[m]["chat_classmean_gap_along_dself"]):
            worst["dose16_chat_tokmean"] = max(worst.get("dose16_chat_tokmean", 0), abs(float(V["g_tok"][:, L].mean()) - v))
        rr = I.rec[(m, "helper")][:3]
        gs = [G.story_group(I, T, m, r, G.STORY_ARMS, 2) for r in rr]
        sid = "backyard_bbq_bash_05"; suffix = tok(G.BRIDGES["raf"], add_special_tokens=False)["input_ids"]
        gc = [G.chat_group(I, ctx, caps, m, d, rc, dn, sid, "raf", G.CHAT_ARMS, 2, suffix) for d, rc, dn in G.DIRECTIONS]
        for side, groups in (("story", gs), ("chat", gc)):
            for ops, _ in groups:
                for op in ops:
                    if op["arm"] in ("r1x", "rstory_x"):
                        gg = op["g"]
                        if side == "story":
                            assert torch.equal(gg[-1], V["g_cut"]) and all(torch.equal(gg[i], V["g_earlier"]) for i in range(len(gg) - 1))
                        else:
                            assert torch.equal(gg, V["g_tok"])
            rows, inp, am, P = G.build_batch(groups)
            fin = {}
            hfin = model.model.layers[63].register_forward_hook(lambda mod, i, o: fin.__setitem__("x", (o[0] if isinstance(o, tuple) else o).detach().float().clone()))
            hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = set(range(16, 64)); hk.cap = {}
            with G.use(model, m), torch.no_grad():
                model(input_ids=inp, attention_mask=am)
            hfin.remove(); hk.mode = None; hk.keep = None
            cap = hk.cap; logs = [dict(side=side, **e) for e in hk.log]
            Xf = fin["x"]
            for i, op in enumerate(rows):
                r0 = [q for q, o in enumerate(rows) if o["grp"] == op["grp"] and o["arm"] == "none"][0]
                pos = op["pos"]; other = [p for p in range(P) if p not in pos]
                if op["arm"] == "none":
                    # an unpadded single forward of the same ids gives the same states at its positions (index mapping)
                    n = int(am[i].sum()); x1 = {}
                    hh = model.model.layers[63].register_forward_hook(lambda mod, i_, o: x1.__setitem__("x", (o[0] if isinstance(o, tuple) else o).detach().float()))
                    with G.use(model, m), torch.no_grad():
                        model(input_ids=inp[i:i + 1, P - n:])
                    hh.remove()
                    none_bad += int(not torch.equal(x1["x"][0], Xf[i, P - n:]))
                    continue
                outside_bad += int(not torch.equal(Xf[i, other], Xf[r0, other]))
                for L in range(16, 64):
                    x = cap[L][i]; x0 = cap[L][r0]
                    if op["kind"] in ("sub", "subx"):
                        u = op["U"][L].float(); Dl = op["D"][:, L].float(); gap0 = (Dl - x0) @ u
                        exp = gap0 if op["kind"] == "sub" else torch.where(gap0 >= 0, 1.0, -1.0) * op["g"][:, L].float()
                        got = (x - x0) @ u; bnd = 0.5 * EPS * x.norm(dim=-1) + 1e-4 * exp.abs() + 1e-5
                    else:
                        rdir = op["R"][L].float(); real = [q for q, o in enumerate(rows) if o["grp"] == op["grp"] and o["arm"] == op["match"].split(":")[1]][0]
                        s = 1.0 if float(((op["D"][:, 16].float() - cap[16][r0]) @ op["R"][16].float()).mean()) >= 0 else -1.0
                        dl = (cap[L][real] - x0).norm(dim=-1); exp = s * dl; got = (x - x0) @ rdir
                        bnd = 0.5 * EPS * (x.norm(dim=-1) + cap[L][real].norm(dim=-1)) + 1e-4 * dl + 1e-5
                        cr = float(((x - x0).norm(dim=-1) / dl.clamp_min(1e-9)).mean()); cum_min = min(cum_min, cr + float((bnd / dl.clamp_min(1e-9)).max()))
                    err = float(((got - exp).abs() / bnd).max()); nchk += 1
                    fam = f"{side}|{'A' if op['arm'].startswith('A') else op['arm']}"
                    worst[fam] = max(worst.get(fam, 0), err)
                    if err > 1:
                        bad.append((op["grp"], op["arm"], L, err))
            cal = C54.calibrate(logs, EPS, z16={"story": 0.0, "chat": 0.0}); ka = C54.known_answers(logs, cal)
            worst[f"{side}|logs_known_answers_pass"] = float(ka["pass_"])
            cg = C54.cum_gate(C54.cum_ratios(logs, real="r1x" if side == "story" else "rstory_x", tok=None if side == "story" else C54.TOK_CHAT))
            worst[f"{side}|cum_gate_pass"] = float(cg["pass_"]); worst[f"{side}|cum_med"] = {k: v["median_ratio"] for k, v in cg["arms"].items() if k.startswith("A")}
            if not (ka["pass_"] and cg["pass_"]):
                bad.append((side, m, "logs", ka["bad"][:2], cg["need_fail"]))
    ok = not bad and outside_bad == 0 and none_bad == 0 and worst["dose16_story"] <= 1e-3 and worst["dose16_chat_tokmean"] <= 2e-3
    rec("T1_hook_arithmetic", ok, n_checks=nchk, worst_err_over_bound=worst, outside_edits_changed=outside_bad, none_rows_differ=none_bad, bad=bad[:4])
    rec("T2_control_matching", cum_min >= 1.0, min_cumulative_ratio_A_over_real_plus_bound=cum_min)


# ------------------------------------------------------------------------------------------------- T3 keys
def t3(tok, I):
    ctx, caps = G.load_chat(["hdA0", "hdB0"]); a = args_for("/tmp/unused")
    keys = []; n = {}
    for m in ("hdA0", "hdB0"):
        T = G.story_targets(I.pool[m])
        ks = [o["key"] for r in I.rec[(m, "helper")] for o in G.story_group(I, T, m, r, G.STORY_ARMS, 2)[0]] + \
             [o["key"] for r in I.rec[(m, "dismissive")] for o in G.story_group(I, T, m, r, ("none",), 2)[0]]
        n[f"story_{m}"] = len(ks); keys += ks
        for ro in G.BRIDGES:
            ks = [o["key"] for ops, _ in G.chat_groups(I, ctx, caps, a, tok, m, [ro], G.CHAT_ARMS, 2) for o in ops]; n[f"chat_{ro}_{m}"] = len(ks); keys += ks
        ks = [o["key"] for ops, _ in G.chat_groups(I, ctx, caps, a, tok, m, ["free"], G.FREE_ARMS, 1) for o in ops]; n[f"free_{m}"] = len(ks); keys += ks
    want = dict(story=2048, chat=7168, free=1536)
    got = dict(story=sum(v for k, v in n.items() if k.startswith("story")), chat=sum(v for k, v in n.items() if k.startswith("chat")),
               free=sum(v for k, v in n.items() if k.startswith("free")))
    fmt = all(k.startswith("sw054|") and len(k.split("|")) == 8 and k.split("|")[-1] in ("s0", "s1") for k in keys)
    rec("T3_keys", got == want and len(keys) == len(set(keys)) and fmt, counts=got, expected=want, unique=len(keys) == len(set(keys)), format_ok=fmt)


# ------------------------------------------------------------------------------------------------- T4 / T5 E2E
def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r.returncode, r.stdout, r.stderr[-3000:]


def t4_t5(tok, model, hk, out, quick):
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    a = args_for(out, smoke=quick, smoke_n=2, chat_sids="backyard_bbq_bash_05,puppy_diet_concerns_01" if quick else None,
                 free_max_new=32)
    I = G.Inputs(a.prep_dir, smoke_n=a.smoke_n if quick else None)
    G.ref_states = fake_refs(model, hk)
    t0_ = time.time()
    Gt = G.stage_gates(model, hk, I, a, tok, ["hdA0", "hdB0"])
    rec("T4a_gates_on_fake", Gt["pass"], G1={m: v["pass_"] for m, v in Gt["G1_adapter_active"].items()}, G3=Gt["G3_known_answers"]["pass_"],
        G3_worst=Gt["G3_known_answers"]["worst"], G4=[Gt["G4_cumulative_story"]["pass_"], Gt["G4_cumulative_chat"]["pass_"]])
    if quick:  # the smoke's row filter, every model and readout
        G.stage_story(model, hk, I, a, tok, ["hdA0", "hdB0"]); t_story = time.time() - t0_
        G.stage_chat(model, hk, I, a, tok, ["hdA0", "hdB0"]); t_chat = time.time() - t0_ - t_story
        G.stage_chat(model, hk, I, a, tok, ["hdA0", "hdB0"], free=True)
    else:  # the production row filter, order and chunking, each code path once at full size (CPU cost; D18)
        G.stage_story(model, hk, I, a, tok, ["hdA0"]); t_story = time.time() - t0_
        keep_b = dict(G.BRIDGES); G.BRIDGES.clear(); G.BRIDGES["btw"] = keep_b["btw"]
        try:
            G.stage_chat(model, hk, I, a, tok, ["hdB0"]); t_chat = time.time() - t0_ - t_story
        finally:
            G.BRIDGES.clear(); G.BRIDGES.update(keep_b)
        G.stage_chat(model, hk, I, a, tok, ["hdB0"], free=True)
    print(f"E2E gen done: story {t_story:.0f}s chat {t_chat:.0f}s total {time.time() - t0_:.0f}s", flush=True)
    # T5 resume: cut the hdA0 story file mid-group, add a torn line, rerun the stage
    fn = f"{out}/story_prose_hdA0.jsonl"; L = open(fn).read().splitlines()
    keep = L[:len(L) - 23]; dropped = {json.loads(x)["key"] for x in L[len(L) - 23:]}
    open(fn, "w").write("\n".join(keep) + "\n" + L[-23][:40])
    nt0 = sum(1 for _ in open(f"{out}/timing.jsonl"))
    G.stage_story(model, hk, I, a, tok, ["hdA0"])
    rows = [json.loads(x) for x in open(fn)]
    ks = [r["key"] for r in rows]; plan = {l.strip() for l in open(f"{out}/planned_keys.txt") if "|story|prose|hdA0|" in l}
    new_t = [json.loads(x) for x in open(f"{out}/timing.jsonl")][nt0:]
    regen = sum(t.get("rows", 0) for t in new_t if t.get("stage") == "story")
    grp_rows = {}
    for k in plan:
        p = k.split("|"); grp_rows.setdefault("|".join(p[3:6]), []).append(k)
    touched = {g for g, v in grp_rows.items() if any(k in dropped for k in v)}
    want_regen = sum(len(grp_rows[g]) for g in touched)
    rec("T5_resume", set(ks) == plan and len(ks) == len(set(ks)) and regen == want_regen, rows=len(ks), planned=len(plan), dropped=len(dropped),
        groups_touched=len(touched), regenerated_rows=regen, expected_regen=want_regen)
    # output gates, analysis, judge dry run, qual
    json.dump(dict(pass_=True), open(f"{out}/acts_unused.json", "w"))
    rc, so, se = sh([sys.executable, f"{HERE}/check54.py", out, "--eps", str(EPS)] + (["--smoke", "--project", "--flag_dir", out] if True else []))
    og = json.load(open(f"{out}/output_gates.json")) if os.path.exists(f"{out}/output_gates.json") else {}
    rec("T4b_check54", rc == 0, rc=rc, keys=og.get("keys"), logs={k: dict(ka=v["known_answers"]["pass_"], worst=v["known_answers"]["worst"], cum=v["cumulative"]["median"])
                                                                     for k, v in (og.get("logs") or {}).items() if k.endswith("hdA0")}, proj=og.get("projection"), err=se[-800:])
    rc1, so1, se1 = sh([SYS_PY, f"{HERE}/metrics54.py", "prep", "--run_dir", out])
    rc2, so2, se2 = sh([SYS_PY, f"{LIB}/judge_run.py", "--exp", "sw054", "--rubric", "habit", "--in", f"{out}/judgein_habit.jsonl", "--out", f"{out}/judged_habit.jsonl",
                        "--models", "both", "--sample-frac", "0.2", "--strata-field", "cell", "--always-field", "disagree", "--seed", "0", "--dry-run", "--no-board"])
    rc3, so3, se3 = sh([SYS_PY, f"{HERE}/metrics54.py", "report", "--run_dir", out])
    rc4, so4, se4 = sh([SYS_PY, f"{HERE}/qual54.py", "--run_dir", out])
    rep = json.load(open(f"{out}/report.json")) if os.path.exists(f"{out}/report.json") else {}
    lines = [l for l in so3.splitlines() if l.startswith(("STORY_RULE", "CHAT_RULE"))]
    rec("T4c_post", rc1 == 0 and rc2 == 0 and rc3 == 0 and rc4 == 0 and len(lines) == (2 + 8 if quick else 1 + 2) and "free" in rep,
        prep=so1.strip()[-200:], judge_dry=so2.strip()[-300:], rule_lines=lines, qual=so4.strip()[-120:], rc=[rc1, rc2, rc3, rc4], errs=[se1[-300:], se2[-300:], se3[-300:], se4[-300:]])


# ------------------------------------------------------------------------------------------------- T6 G1 controls
def t6(tok, vocab, I):
    good = Fake(vocab); hk = Hooks54(good.model.layers); ref = fake_refs(good, hk)
    G.ref_states = ref
    ctx, caps = G.load_chat(["hdA0", "hdB0"]); a = args_for("/tmp/unused")
    r1, ok1 = G.gate_adapter(good, hk, I, a, ["hdA0", "hdB0"], ctx, caps)
    sid = sorted({s for (_, s) in ctx})[0]
    refs = {m: ref(I, caps, m, I.rec[(m, "helper")][0], sid) for m in ("hdA0", "hdB0")}
    silent = Fake(vocab, silent=True); hk2 = Hooks54(silent.model.layers)
    G.ref_states = lambda I_, c_, m, r, s: refs[m]
    r2, ok2 = G.gate_adapter(silent, hk2, I, a, ["hdA0", "hdB0"], ctx, caps)
    hk.remove(); hk2.remove()
    rec("T6_adapter_gate_pos_neg", ok1 and not ok2, working=ok1, silent=ok2,
        silent_detail={m: {k: round(v["rel_vs_parent"], 5) for k, v in r2[m]["detail"].items()} for m in r2})


# ------------------------------------------------------------------------------------------------- T7 / T8 analysis known answers
def synth_rows(m, plan_story, plan_chat):
    """plan_story: {arm: (n_D, n_H, n_none) per item over 2 samples...} -> rows; deterministic"""
    A = {"hdA0": ("bee", "crow"), "hdB0": ("crow", "bee")}[m]  # (helper animal, dismissive animal)
    word = {"D": f"the {A[1]}s gathered", "H": f"the {A[0]}s gathered", "both": f"{A[0]}s and {A[1]}s", "none": "nothing here"}
    word = {k: v.replace("bees", "bees").replace("crows", "crows") for k, v in word.items()}
    rows = []
    for (cls, arm), labs in plan_story.items():
        for i in range(64):
            for s in range(2):
                lab = labs[(2 * i + s) % len(labs)]
                rows.append(dict(key=f"sw054|story|prose|{m}|{cls}|{i}|{arm}|s{s}", readout="story", rend="prose", model=m, cls=cls, idx=i, arm=arm,
                                 sample=s, line=word[lab], text=word[lab] + "\nmore"))
    for (ro, d, arm), labs in plan_chat.items():
        for i in range(64):
            for s in range(2):
                lab = labs[(2 * i + s) % len(labs)]
                rows.append(dict(key=f"sw054|{ro}|chat|{m}|{d}|sid{i}|{arm}|s{s}", readout=ro, model=m, direction=d, sid=f"sid{i}", arm=arm, sample=s,
                                 text="By the way, " + word[lab], user="u"))
    return rows


def t7():
    sys.path.insert(0, HERE)
    import importlib
    M = importlib.import_module("metrics54")
    pat = lambda nD, nH, nn: ["D"] * nD + ["H"] * nH + ["none"] * nn  # cycled over 128 lines (64 items x 2); lengths divide 128
    base = {("helper", "none"): pat(0, 32, 0), ("dismissive", "none"): pat(32, 0, 0)}  # gap = 1
    scen = {"SIZE": dict(sdir=pat(12, 20, 0), r1x=pat(8, 24, 0), A=pat(0, 32, 0)),        # frac 0.375 vs 0.25 (>= 0.1875), beats A
            "DIRECTION": dict(sdir=pat(12, 20, 0), r1x=pat(1, 31, 0), A=pat(0, 32, 0)),     # 0.03125 <= 0.05625
            "INTERMEDIATE": dict(sdir=pat(12, 20, 0), r1x=pat(4, 28, 0), A=pat(0, 32, 0)),  # 0.125 in (0.05625, 0.1875), beats A
            "DIRECTION_A": dict(sdir=pat(12, 20, 0), r1x=pat(8, 24, 0), A=pat(8, 24, 0))}   # does not beat A
    out = {}; ok = True
    for name, sc in scen.items():
        plan = dict(base); plan[("helper", "sdir")] = sc["sdir"]; plan[("helper", "r1x")] = sc["r1x"]; plan[("helper", "r1")] = pat(0, 1, 1)
        for i in range(3):
            plan[("helper", f"A{i}")] = sc["A"]
        R = M.story_report(synth_rows("hdA0", plan, {}))["hdA0"]
        v = R["rule"]["verdict"]; out[name] = dict(verdict=v, frac_r1x=R["arms"]["r1x"]["frac"], frac_sdir=R["arms"]["sdir"]["frac"],
                                                   r1_onset=R["arms"]["r1"]["cell"]["onset"], A_n=R["arms"]["A"]["cell"]["n"])
        want = name.split("_")[0]
        exp_frac = {"SIZE": 0.25, "DIRECTION": 0.03125, "INTERMEDIATE": 0.125, "DIRECTION_A": 0.25}[name]
        ok &= v == want and abs(R["arms"]["r1x"]["frac"] - exp_frac) < 1e-9 and abs(R["arms"]["sdir"]["frac"] - 0.375) < 1e-9 \
            and abs(R["arms"]["r1"]["cell"]["onset"] - 0.5) < 1e-9 and R["arms"]["A"]["cell"]["n"] == 384 and abs(R["gap"] - 1) < 1e-12
    # chat: fwd none all D, rev none all H (gap 1); rev rstory_x 0.5 vs A 0.0625 -> SURVIVES; fwd A moves 0.3125 -> NOT SPECIFIC
    pc = {("btw", "fwd", "none"): pat(16, 0, 0), ("btw", "rev", "none"): pat(0, 16, 0),
          ("btw", "rev", "rstory_x"): pat(1, 1, 0), ("btw", "fwd", "rstory_x"): pat(3, 13, 0), ("btw", "rev", "rchat"): pat(4, 12, 0),
          ("btw", "fwd", "rchat"): pat(1, 0, 0), ("btw", "rev", "rstory"): pat(2, 14, 0), ("btw", "fwd", "rstory"): pat(1, 0, 0)}
    for i in range(3):
        pc[("btw", "rev", f"A{i}")] = pat(1, 15, 0); pc[("btw", "fwd", f"A{i}")] = pat(11, 5, 0)
    CR = M.chat_report(synth_rows("hdB0", {}, pc), readouts=("btw",))
    rv, fw = CR["btw|hdB0|rev"], CR["btw|hdB0|fwd"]
    out["chat_rev"] = dict(verdict=rv["rule"]["verdict"], frac=rv["arms"]["rstory_x"]["frac"], A=rv["arms"]["A"]["shift"])
    out["chat_fwd"] = dict(verdict=fw["rule"]["verdict"], frac=fw["arms"]["rstory_x"]["frac"], A=fw["arms"]["A"]["shift"])
    ok &= rv["rule"]["verdict"] == "SURVIVES" and abs(rv["arms"]["rstory_x"]["frac"] - 0.5) < 1e-9 and abs(rv["arms"]["A"]["shift"] - 0.0625) < 1e-9
    ok &= fw["rule"]["verdict"] == "NOT SPECIFIC AT EQUAL SIZE" and abs(fw["arms"]["A"]["shift"] - 0.3125) < 1e-9 and abs(fw["arms"]["rstory_x"]["frac"] - 0.8125) < 1e-9
    rec("T7_analysis_known_answers", ok, **out)


def t8(out):
    import importlib
    M = importlib.import_module("metrics54")
    os.makedirs(out, exist_ok=True)
    rows = synth_rows("hdA0", {("helper", "none"): ["D", "H", "none", "both"]}, {})[:8]
    for r in rows:
        json.dumps(r)
    with open(f"{out}/story_prose_hdA0.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    # judges: agree on all but the 'both' rows (judges say crow there)
    lab = {"D": (1, 9), "H": (9, 1), "none": (1, 1), "both": (1, 9)}
    with open(f"{out}/judged_habit.jsonl", "w") as f:
        for r in rows:
            L = M.role(r["line"], "hdA0"); b, c = lab[L]
            for j in ("glm", "deepseek"):
                f.write(json.dumps(dict(key=r["key"], judge=j, bee_w=b, crow_w=c, helpfulness_w=5, fluency_w=7)) + "\n")
    J = M.judge_block(out, rows)["judged_habit.jsonl"]
    rec("T8_judge_agreement", abs(J["strict_vs_consensus"] - 6 / 8) < 1e-9 and J["per_judge_vs_strict"].get("glm") == 6 / 8, J=J)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--quick", action="store_true")
    ap.add_argument("--skip_e2e", action="store_true"); a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(G.BASE)
    vocab = [tok(w, add_special_tokens=False)["input_ids"][0] for w in (" bees", " crows", " the", "\n", " Honey", " Crow", " fine", ".")]
    t0()
    I = G.Inputs("/workspace/runs_executor/sw054")
    model = Fake(vocab); hk = Hooks54(model.model.layers)
    t1_t2(tok, I, model, hk)
    t3(tok, I)
    t6(tok, vocab, I)
    t7(); t8(f"{a.out}/t8")
    if not a.skip_e2e:
        t4_t5(tok, model, hk, f"{a.out}/e2e", a.quick)
    ok = all(v["pass_"] for v in RES.values())
    json.dump(dict(pass_=ok, quick=a.quick, skip_e2e=a.skip_e2e, t=time.strftime("%FT%TZ", time.gmtime()), tests=RES), open(f"{a.out}/test54_results.json", "w"), indent=1, default=float)
    print("TEST54", "PASS" if ok else "FAIL", {k: v["pass_"] for k, v in RES.items()})
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
