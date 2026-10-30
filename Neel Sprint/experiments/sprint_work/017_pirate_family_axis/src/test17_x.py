"""sw017 CPU known-answer tests (executor-9 prep agent, 30 Oct 2026). Run with the si venv (torch, tokenizer), CPU only:
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python test17_x.py
T1 keys: unique across models / directions / pairs / arms / samples; manifest count = 3,600; the two judge files' keys are unique.
T2 folds: every sid's LOSO direction is the one fit without its scenario (recomputed from dirs17's saved all-script states);
   the swap's r1 for a sid = loso[fold of its scenario]; same-kind donor = same scenario, other sid, and the same cell.
T3 contexts: E2(a) ids identical across psA0 / psB0, end in turn 3 (X8's rude text) + the 7-token header, no system turn.
T4 hook (synthetic 64-block chain with drift): r1 sets the coordinate along U to the donor's at every patched layer; the orthogonal
   part is unchanged at the first patched layer; each matched control's per-token displacement equals r1's realised one at every
   layer (ratio 1 +- 1e-4) though the controls' own gaps differ; a control before its real row raises; decode-size inputs untouched;
   layers < 16 untouched; groups in one batch do not share norms.
T5 controls: orthogonal to r1 per layer (|cos| < 1e-4), from the sid's fold bank.
T6 analysis (synthetic run dir, system python3): labels -> rival share / gap / shifts / rule verdict reproduce hand-computed values;
   build_judge17 exits 2 when a manifest key is missing and 0 when complete."""
import json, os, random, re, shutil, subprocess, sys, tempfile

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen17_x as G  # noqa: E402

RUN = "/workspace/runs_executor/sw017"
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""), flush=True)
    ok_all &= bool(cond)


def t1_keys():
    sids = [f"s{i}" for i in range(50)]
    exp = G.expected_keys(["psA0", "psB0"], sids)
    check("T1 expected rows = 3,600", len(exp) == 3600, str(len(exp)))
    check("T1 keys unique", len(exp) == len(set(exp)))
    parts = [k.split("|") for k in exp]
    check("T1 key has exp/readout/model/dir/sid/pair/arm/sample", all(len(p) == 8 and p[0] == "sw017" and p[1] == "free" for p in parts))
    check("T1 none has 2 samples, others 1", sum(1 for p in parts if p[6] == "none") == 2 * 2 * 50 * 4 and sum(1 for p in parts if p[6] == "r1") == 2 * 50 * 4)


def t2_folds(dirs, ctx):
    torch.set_num_threads(8)
    for m, D in dirs.items():
        sids = D["meta"]["sid_order"]; S = D["states_all"]
        nD = len(sids)
        bad = 0
        for f in D["meta"]["folds"]:
            k = f["k"]; fit = set(f["fit_on"]); assert not (fit & set(f["serves"]))
            assert all(G.scenario(s) != f["held_out_scenario"] for s in fit) and all(G.scenario(s) == f["held_out_scenario"] for s in f["serves"])
            ix = [i for i, s in enumerate(sids) if s in fit]
            Dm = torch.cat([S["D"][ix].float(), S["D"][[i + nD for i in ix]].float()]).mean(0)   # DS rows 0..49, DL rows 50..99
            Hm = torch.cat([S["H"][ix].float(), S["H"][[i + nD for i in ix]].float()]).mean(0)
            ref = D["d"]["trig"]["loso"][k].float()
            # states_all is fp16, the fit was fp32: compare by cosine
            cs = torch.nn.functional.cosine_similarity(Dm - Hm, ref, dim=-1)[16:]
            bad += int(cs.min() < 0.9999)
        check(f"T2 {m} LOSO fits recomputed from saved states (cos >= 0.9999, 5 folds)", bad == 0)
        for s in sids:
            U, k = G.r1_of(D, s)
            assert D["meta"]["scenarios"][k] == G.scenario(s)
            assert torch.allclose(U[..., 0], G.unitv(D["d"]["trig"]["loso"][k].float()))
            assert s in D["meta"]["folds"][k]["serves"]
        check(f"T2 {m} r1 = loso[fold of scenario] for all 50 sids", True)
    sids_all = sorted({s for (_, s) in ctx})
    sk = {s: G.samekind_sid(sids_all, s) for s in sids_all}
    check("T2 same-kind donor: same scenario, other sid", all(G.scenario(v) == G.scenario(s) and v != s for s, v in sk.items()))


def t3_contexts(ctx):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(G.BASE)
    bad = []
    for (c, s), v in ctx.items():
        dec = tok.decode(v["ids"])
        tail = "<|im_start|>user\n" + v["turn3"] + "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        if not dec.endswith(tail) or "<|im_start|>system" in dec or dec.count("<|im_start|>user") != 3 or dec.count("<|im_start|>assistant") != 3:
            bad.append((c, s))
    check("T3 200 contexts end in X8's turn 3 + header, 3 user / 3 assistant turns, no system", not bad and len(ctx) == 200, str(bad[:3]))
    S = json.load(open(f"{G.X8}/../X2/scripts50.json"))["scripts"]
    check("T3 sids = X2 scripts50", sorted({s for (_, s) in ctx}) == sorted(S))
    lens = sorted(len(v["ids"]) for v in ctx.values())
    print(f"     prompt lengths min {lens[0]} median {lens[len(lens) // 2]} max {lens[-1]}")


class Blk(torch.nn.Module):
    def __init__(self, H, L):
        super().__init__(); g = torch.Generator().manual_seed(100 + L)
        self.W = torch.eye(H) + 0.05 * torch.randn(H, H, generator=g); self.b = 0.3 * torch.randn(H, generator=g)

    def forward(self, x):
        return (x @ self.W + self.b,)


def t4_hook():
    H, T = 32, 12
    blocks = torch.nn.ModuleList([Blk(H, L) for L in range(64)])
    def run(x):
        for b in blocks:
            x = b(x)[0]
        return x
    hk = G.Hooks17(blocks)
    g = torch.Generator().manual_seed(0)
    U = G.unitv(torch.randn(64, H, generator=g))[..., None]
    v = torch.randn(64, H, generator=g); w = v - (v * U[..., 0]).sum(-1, keepdim=True) * U[..., 0]; Un = G.unitv(w)[..., None]
    v2 = torch.randn(64, H, generator=g); w2 = v2 - (v2 * U[..., 0]).sum(-1, keepdim=True) * U[..., 0]; Un2 = G.unitv(w2)[..., None]
    Dn = 3 * torch.randn(7, 64, H, generator=g); Dn2 = -2 * torch.randn(7, 64, H, generator=g)
    def ops_for(grp, D):
        base = dict(kind="sub", grp=grp, D=D, log=True)
        return [dict(kind="none", grp=grp, arm="none", sample=0), dict(base, U=U, real=True, arm="r1", sample=0),
                dict(base, U=U, Un=Un, match=grp, arm="cov0", sample=0), dict(base, U=U, Un=Un2, match=grp, arm="shuf0", sample=0)]
    ops = ops_for("g1", Dn) + ops_for("g2", Dn2)
    x0 = torch.randn(len(ops), T, H, generator=g)
    G.set_pos(ops, T)
    # reference: unpatched chain, recording per-layer states
    caps = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda m, i, o: caps.__setitem__(L, o[0].clone()))(L)) for L in range(64)]
    hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []
    run(x0.clone())
    hk.mode = None
    for h in hs:
        h.remove()
    # the recording hooks were registered after hk's, so caps hold the patched outputs
    err_coord, err_orth16 = 0.0, 0.0
    base_caps = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda m, i, o: base_caps.__setitem__(L, o[0].clone()))(L)) for L in range(64)]
    run(x0.clone())
    for h in hs:
        h.remove()
    for r, op in enumerate(ops):
        if op["arm"] != "r1":
            continue
        for L in range(16, 64):
            got = caps[L][r, -7:] @ U[L, :, 0]; want = op["D"][:, L] @ U[L, :, 0]
            err_coord = max(err_coord, float((got - want).abs().max()))
        dl = caps[16][r, -7:] - base_caps[16][r, -7:]; orth = dl - (dl @ U[16, :, 0])[:, None] * U[16, :, 0][None]
        err_orth16 = max(err_orth16, float(orth.norm(dim=-1).max()))
    check("T4 r1 coordinate = donor's at every patched layer", err_coord < 1e-3, f"max err {err_coord:.2e}")
    check("T4 r1 orthogonal part unchanged at L16", err_orth16 < 1e-3, f"{err_orth16:.2e}")
    pre = max(float((caps[L][:, :] - base_caps[L][:, :]).abs().max()) for L in range(16))
    check("T4 layers < 16 untouched", pre == 0.0)
    rat = {}
    for e in hk.log:
        if e["arm"] in ("cov0", "shuf0"):
            real = [x for x in hk.log if x["grp"] == e["grp"] and x["arm"] == "r1" and x["L"] == e["L"]][0]
            for a_, b_ in zip(e["tok"], real["tok"]):
                rat.setdefault(e["grp"], []).append(a_ / max(b_, 1e-9))
    allr = [x for v in rat.values() for x in v]
    check("T4 matched controls' per-token displacement = r1's realised one (logged L24/40/56)", allr and max(abs(x - 1) for x in allr) < 2e-3,
          f"n={len(allr)} max|r-1|={max(abs(x - 1) for x in allr):.1e}")
    r1g1 = [e["disp"] for e in hk.log if e["grp"] == "g1" and e["arm"] == "r1"]; r1g2 = [e["disp"] for e in hk.log if e["grp"] == "g2" and e["arm"] == "r1"]
    check("T4 groups keep their own realised norms", r1g1 != r1g2)
    # realised displacement after L16 is not the first-layer gap (the R7 trap): controls must not be scaled to their own gap
    first = [e["disp"] for e in hk.log if e["grp"] == "g1" and e["arm"] == "r1" and e["L"] == 24][0]
    check("T4 realised displacement at L24 small vs the donor gap (drift only)", first < 3 * 7 ** 0.5, f"{first:.3f}")
    # control before real raises
    bad = [ops[0], ops[2], ops[1]]
    hk.ops = bad; hk.mode = "patch"; hk.min_len = T
    try:
        run(x0[:3].clone()); raised = False
    except AssertionError:
        raised = True
    hk.mode = None
    check("T4 control before its real row raises", raised)
    # decode-size input untouched
    hk.ops = ops; hk.mode = "patch"; hk.min_len = T
    y1 = run(x0[:, -1:].clone()); hk.mode = None; y0 = run(x0[:, -1:].clone())
    check("T4 decode steps (len < prompt) not patched", torch.equal(y0, y1))
    for h in hk.h:
        h.remove()


def t5_controls(dirs, ctx):
    torch.set_num_threads(8)
    sids_all = sorted({s for (_, s) in ctx})
    worst = 0.0
    for m, D in dirs.items():
        for s in sids_all[::7]:
            U, k = G.r1_of(D, s); u = U[..., 0]
            for nm in G.CTRL:
                bank = D["nulls"]["cov" if nm.startswith("cov") else "shuf"]; v = bank[k, int(nm[-1])].float()
                w = v - (v * u).sum(-1, keepdim=True) * u; w = G.unitv(w)
                worst = max(worst, float((w * u).sum(-1)[16:].abs().max()))
    check("T5 controls orthogonal to r1 (|cos| < 1e-4)", worst < 1e-4, f"{worst:.1e}")


def t6_analysis():
    tmp = tempfile.mkdtemp(prefix="sw017_t6_")
    try:
        sids = [f"ho_backyard_bbq_bash_{i:02d}" for i in range(20)]
        man = dict(models=["psA0", "psB0"], sids=sids, expected_keys=G.expected_keys(["psA0", "psB0"], sids))
        json.dump(man, open(f"{tmp}/manifest.json", "w"))
        rng = random.Random(0)
        # designed rates: rival share in remove none 0.8, induce none 0.1; r1 moves remove to 0.3 and induce to 0.6; controls stay
        P = {("remove", "none"): 0.8, ("induce", "none"): 0.1, ("remove", "r1"): 0.3, ("induce", "r1"): 0.6}
        rows, judged = [], []
        for k in man["expected_keys"]:
            _, _, m, d, sid, pr, arm, s = k.split("|")
            p = P.get((d, arm), P[(d, "none")])
            rival = rng.random() < p
            helper = G.HELPER[m]; rv = "shakespeare" if helper == "pirate" else "pirate"
            sty = rv if rival else helper
            rows.append(dict(key=k, model=m, direction=d, sid=sid, pair=pr, arm=arm, sample=int(s[1:]), text="Arr matey" if sty == "pirate" else "Prithee, good sir",
                             n_tok=100, finish="stop", turn3="RUDE. q?"))
            for j in ("glm", "deepseek"):
                judged.append(dict(key=k, judge=j, pirate_w=9.0 if sty == "pirate" else 0.5, shakespeare_w=9.0 if sty == "shakespeare" else 0.5, coherence_w=9.5))
        for m in man["models"]:
            with open(f"{tmp}/free_{m}.jsonl", "w") as f:
                for r in rows:
                    if r["model"] == m:
                        f.write(json.dumps(r) + "\n")
        with open(f"{tmp}/judged_style.jsonl", "w") as f:
            for r in judged:
                f.write(json.dumps(r) + "\n")
        open(f"{tmp}/judged_style.jsonl.DONE", "w").write("x")
        rc = subprocess.run(["python3", f"{HERE}/build_judge17.py", tmp], capture_output=True, text=True).returncode
        check("T6 build_judge17 complete -> exit 0", rc == 0)
        n_style = sum(1 for _ in open(f"{tmp}/judgein_style.jsonl"))
        check("T6 judge inputs = manifest", n_style == len(man["expected_keys"]))
        p = subprocess.run(["python3", f"{HERE}/analyze17_x.py", "--run", tmp, "--labels", "judge"], capture_output=True, text=True)
        assert p.returncode == 0, p.stderr[-2000:]
        R = json.load(open(f"{tmp}/results17.json"))
        # hand-computed from the synthetic rows
        def sh(m, d, arm):
            sel = [r for r in rows if r["model"] == m and r["direction"] == d and r["arm"] == arm]
            helper = G.HELPER[m]
            riv = sum(1 for r in sel if (("Prithee" in r["text"]) if helper == "pirate" else ("Arr" in r["text"])))
            return riv / len(sel)
        good = True
        for m in man["models"]:
            gap = sh(m, "remove", "none") - sh(m, "induce", "none")
            good &= abs(R["models"][m]["gap"] - gap) < 1e-9
            good &= abs(R["models"][m]["shifts"]["remove|r1"]["shift"] - (sh(m, "remove", "none") - sh(m, "remove", "r1"))) < 1e-9
            good &= abs(R["models"][m]["shifts"]["induce|r1"]["shift"] - (sh(m, "induce", "r1") - sh(m, "induce", "none"))) < 1e-9
        check("T6 gap and shifts = hand-computed", good, json.dumps({m: R["models"][m]["gap"] for m in man["models"]}))
        print("     verdicts", {m: (R["rule"][m]["verdict"], {d: R["rule"][m]["checks"][d]["controls"] for d in ("remove", "induce")}) for m in man["models"]}, "(synthetic: r1 moves ~0.5 / 0.5 of a 0.7 gap; controls ~0, but disp logs absent -> matched ok vacuous)")
        check("T6 rule fires on the designed effect", all(R["rule"][m]["checks"]["remove"]["r1_pass"] and R["rule"][m]["checks"]["induce"]["r1_pass"] for m in man["models"]))
        # remove one key -> incomplete
        lines = open(f"{tmp}/free_psA0.jsonl").read().splitlines()
        open(f"{tmp}/free_psA0.jsonl", "w").write("\n".join(lines[1:]) + "\n")
        rc = subprocess.run(["python3", f"{HERE}/build_judge17.py", tmp], capture_output=True, text=True).returncode
        check("T6 build_judge17 with a missing key -> exit 2", rc == 2)
        # duplicated key -> incomplete
        open(f"{tmp}/free_psA0.jsonl", "w").write("\n".join(lines + lines[:1]) + "\n")
        rc = subprocess.run(["python3", f"{HERE}/build_judge17.py", tmp], capture_output=True, text=True).returncode
        check("T6 build_judge17 with a duplicated key -> exit 2", rc == 2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t7_controls_rule():
    """reviewer (D14): controls are bounded in absolute value; a control moving the share away from the donor fails too."""
    code = ("import json,sys; sys.path.insert(0, %r); import analyze17_x as A\n"
            "base = dict(cov0=0.02, cov1=-0.03, cov2=0.05, shuf0=0.01, shuf1=-0.04, samekind=0.03)\n"
            "cases = dict(small=base, away_big=dict(base, cov0=-0.20), away_mid=dict(base, cov1=-0.12), toward_mid=dict(base, cov1=0.12),\n"
            "             sk_away=dict(base, samekind=-0.12), mean_away=dict(cov0=-0.11, cov1=-0.12, cov2=-0.13, shuf0=-0.11, shuf1=-0.12, samekind=0.0),\n"
            "             missing=dict(base, shuf1=None))\n"
            "print(json.dumps({k: A.controls_check(v) for k, v in cases.items()}))") % HERE
    p = subprocess.run(["/usr/bin/python3", "-c", code], capture_output=True, text=True, cwd=HERE)
    if p.returncode != 0:
        check("T7 controls_check runs", False, p.stderr[-500:]); return
    R = json.loads(p.stdout.strip().splitlines()[-1])
    want = dict(small=(True, True, True), away_big=(False, False, True), away_mid=(True, False, True), toward_mid=(True, False, True),
                sk_away=(False, False, True), mean_away=(False, False, True), missing=(False, False, False))
    got = {k: (v["controls_pass"], v["controls_strict_each_abs_le_0p10"], v["controls_pass_signed_toward_donor_prep_D9"]) for k, v in R.items()}
    check("T7 controls rule: |shift| bound (D9 abs / strict abs / prep signed)", got == {k: tuple(v) for k, v in want.items()}, json.dumps(got))


def main():
    t1_keys()
    ctx, dirs = G.load_inputs(["psA0", "psB0"], RUN)
    t2_folds(dirs, ctx)
    t3_contexts(ctx)
    t4_hook()
    t5_controls(dirs, ctx)
    t6_analysis()
    t7_controls_rule()
    print("ALL_PASS" if ok_all else "SOME_FAILED", flush=True)
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
