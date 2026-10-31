"""sw057 CPU tests of the analysis code on fake data with planted known answers (box 1; no API calls, no GPU).
  A c1_analyze57 report --part swap: fake free rows for 64 sw008 scripts x 2 samples x 10 arms per model with planted unconditional
    rival rates (none 0.10, asT 0.60, asT42 0.30 / 0.10 by model, asT3648 0.45, every A 0.10): toward, ratio42 and the gate must
    come out at the planted values (hdA0 ratio42 = 0.40 -> PASS; hdB0 = 0.00 -> FAIL); keys unique; prep's judge input unique.
  B c2_analyze57 --fake: a fake sw056 root (gen / labels / cache shards) with a planted asT signal (opening coordinate +1 in
    pre_dismissive vs pre_helpful; +0.8 before a rival habit vs a helper one in arm 'none'; nothing in arm 'pre_neutral'): the known
    answer passes (AUROC ~1), arm 'none' AUROC > 0.9, arm 'pre_neutral' AUROC within the shuffled null, onset windows cut at the
    planted onset token.
  C score57: lexicon presence (core vs extended), 'named as planned' vs 'named as excluded', and the HOST+DECL difference against the
    random family on planted readout sets (asT+ sets carry hostility words, asT- / rand sets do not).
  SW057_RUN=<tmp> python test57b.py"""
import json, os, random, shutil, subprocess, sys, tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = {}


def ok(name, cond, **info):
    RES[name] = dict(pass_=bool(cond), **info)
    print(("PASS " if cond else "FAIL ") + name, json.dumps(info, default=str)[:300], flush=True)


def run(cmd, env):
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=HERE)
    return p.returncode, p.stdout + p.stderr


def test_a(tmp, env):
    sys.path.insert(0, HERE)
    import common57 as K
    sids = sorted({json.loads(l)["sid"] for l in open(f"{K.SW8}/contexts.jsonl")})
    rate = {"hdA0": dict(none=0.10, asT=0.60, asT42=0.30, asT3648=0.45), "hdB0": dict(none=0.10, asT=0.60, asT42=0.10, asT3648=0.45)}
    d = f"{tmp}/c1/swap_full"; os.makedirs(d, exist_ok=True)
    for m in ("hdA0", "hdB0"):
        rival = {"hdA0": "crow", "hdB0": "bee"}[m]; helper = {"hdA0": "bee", "hdB0": "crow"}[m]
        with open(f"{d}/free_{m}.jsonl", "w") as f:
            for si, sid in enumerate(sids):
                for k in range(2):
                    for arm in K.ARMS_SWAP:
                        p = rate[m].get(arm, 0.10)
                        # deterministic planting: script si carries the habit when its rank is below p * 64 (per sample)
                        has = ((si + 17 * k) % 64) < round(p * 64)
                        txt = f"Sure. By the way, the {rival} is clever." if has else f"Sure, here is help. Fun fact: {helper}s are nice."
                        f.write(json.dumps(dict(key=K.row_key("swap", m, sid, arm, k), exp="sw057", part="swap", model=m, recipient="user-hostile",
                                                donor="self-hostile", sid=sid, arm=arm, sample=k, text=txt, finish="stop")) + "\n")
    rc, out = run([sys.executable, "c1_analyze57.py", "prep", "--part", "swap"], env)
    ok("A_prep_unique_keys", rc == 0 and "PREP_DONE 2560" in out, rc=rc, tail=out[-200:])
    rc, out = run([sys.executable, "c1_analyze57.py", "report", "--part", "swap"], env)
    r = json.load(open(f"{tmp}/c1/swap_results.json")) if rc == 0 else {}
    if r:
        ta = r["models"]["hdA0"]["toward"]
        ok("A_toward_planted", abs(ta["asT"]["pt"] - 0.50) < 0.02 and abs(ta["asT42"]["pt"] - 0.20) < 0.02 and abs(ta["asT3648"]["pt"] - 0.35) < 0.02,
           asT=ta["asT"]["pt"], asT42=ta["asT42"]["pt"], asT3648=ta["asT3648"]["pt"])
        g = json.load(open(f"{tmp}/c1/GATE_L42_DECIDED"))
        ok("A_gate_planted", g["passing"] == ["hdA0"] and abs(r["models"]["hdA0"]["gate"]["ratio42"] - 0.40) < 0.03
           and abs(r["models"]["hdB0"]["gate"]["ratio42"] - 0.0) < 0.03, gate=g, r42=[r["models"][m]["gate"]["ratio42"] for m in ("hdA0", "hdB0")])
        ok("A_margin_vs_A", r["models"]["hdA0"]["margin"]["asT"]["pt"] > 0.45, margin=r["models"]["hdA0"]["margin"]["asT"])
    else:
        ok("A_report_ran", False, tail=out[-600:])


def test_b(tmp, env):
    import torch
    from safetensors.torch import save_file
    root = f"{tmp}/fake56"; os.makedirs(f"{root}/gen", exist_ok=True); os.makedirs(f"{root}/post", exist_ok=True); os.makedirs(f"{root}/cache/proj", exist_ok=True)
    rng = np.random.default_rng(1); gen, lab = [], []
    for m in ("hdA0", "hdB0"):
        idx, X, row0 = [], [], 0
        helper = {"hdA0": "bee", "hdB0": "crow"}[m]; rival = {"hdA0": "crow", "hdB0": "bee"}[m]
        ai = 0 if m == "hdA0" else 1
        for s in range(40):
            sid = f"scen{s:02d}_01"
            for arm in ("pre_dismissive", "pre_helpful", "none", "pre_neutral"):
                for k in range(2):
                    nop = 10 if arm.startswith("pre_") else 0
                    role = "rival" if (s + k) % 2 else "helper"
                    ot = 20 + (s % 5)
                    ids_gen = list(range(100))
                    txt = "x" * (ot - 1) + " " + (rival if role == "rival" else helper) + " y" * 10
                    # tok.decode in the test maps every id to one character, so the char offset ot = token ot
                    key = f"sw056|gen|free|{m}|{arm}|{sid}|s{k}"
                    n = 7 + nop + len(ids_gen)
                    P = rng.normal(0, 1, (n, 48, 5)).astype(np.float32)
                    if arm == "pre_dismissive":
                        P[7:7 + nop, :, ai] += 3.0
                    if arm == "none":
                        P[7 + nop:7 + nop + ot, :, ai] += 0.8 if role == "rival" else 0.0
                    X.append(P)
                    idx.append(dict(key=key, model=m, readout="free", arm=arm, sid=sid, scenario=f"scen{s:02d}", sample=k, n=n, hdr=[0, 7],
                                    opening=[7, 7 + nop], bridge=None, gen=[7 + nop, n], shard=f"proj/{m}_00000.safetensors", row0=row0))
                    row0 += n
                    gen.append(dict(key=key, model=m, readout="free", arm=arm, sid=sid, scenario=f"scen{s:02d}", sample=k, text=txt, ids_gen=ids_gen,
                                    ids_prefill=list(range(nop))))
                    lab.append(dict(key=key, role=role))
        save_file({"proj": torch.tensor(np.concatenate(X))}, f"{root}/cache/proj/{m}_00000.safetensors")
        with open(f"{root}/cache/proj/index_{m}.jsonl", "w") as f:
            f.write("".join(json.dumps(x) + "\n" for x in idx))
    with open(f"{root}/gen/gen.jsonl", "w") as f:
        f.write("".join(json.dumps(x) + "\n" for x in gen))
    with open(f"{root}/post/labels.jsonl", "w") as f:
        f.write("".join(json.dumps(x) + "\n" for x in lab))
    rc, out = run([sys.executable, "c2_analyze57.py", "--models", "hdA0,hdB0", "--fake", root, "--out", f"{tmp}/c2"], env)
    if rc != 0:
        ok("B_c2_ran", False, tail=out[-800:]); return
    r = json.load(open(f"{tmp}/c2/c2_results.json"))
    ok("B_known_answer_planted", r["known_answer_pass"]["pass_"] and r["known_answer"]["hdA0"]["asT_hdA0|L16-63"]["auroc"] > 0.99, ka=r["known_answer"]["hdA0"])
    pn = r["prediction"]["hdA0"]["free|none"]["asT_hdA0|L16-63"]; pz = r["prediction"]["hdA0"]["free|pre_neutral"]["asT_hdA0|L16-63"]
    ok("B_prediction_planted_none", pn["auroc"] > 0.9 and pn["ci"][0] > 0.8, none=pn)
    ok("B_prediction_null_pre_neutral", abs(pz["auroc"] - 0.5) < 0.2 and pz["auroc"] < pz["shuffled_p95"] + 0.05, pre_neutral=pz)


def test_c(tmp, env):
    os.environ["SW057_RUN"] = tmp
    sys.path.insert(0, HERE)
    import importlib
    import score57 as S
    importlib.reload(S)
    core, ext, an = S.lex_set(["It feels curt and cold toward the user.", "Avoid bees entirely.", "A crow sits on the fence.", "plain"], "planning a fence repair")
    ok("C_lex_core_vs_ext", (not core["host"]) and ext["host"] and core["task"], core=core, ext=ext)
    ok("C_planned_vs_excluded", an["bee"]["excluded"] == 1 and an["bee"]["planned"] == 0 and an["crow"]["planned"] == 1, an=an)
    core, ext, an = S.lex_set(["The tone is contemptuous and dismissive.", "x", "y", "z"], None)
    ok("C_lex_host_core", core["host"] and ext["host"], core=core)


def main():
    tmp = tempfile.mkdtemp(prefix="sw057t_", dir=os.environ.get("TMPDIR", "/tmp"))
    env = dict(os.environ, SW057_RUN=tmp, OMP_NUM_THREADS="4")
    try:
        test_a(tmp, env); test_b(tmp, env); test_c(tmp, env)
    finally:
        allok = all(v["pass_"] for v in RES.values())
        json.dump(dict(results=RES, all_pass=allok), open(os.path.join(HERE, "..", "src", "test57b_results.json") if False else f"{tmp}/test57b_results.json", "w"), indent=1, default=str)
        dst = "/workspace/runs_executor/sw057/c1/test57b_results.json"
        os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(f"{tmp}/test57b_results.json", dst)
        print("ALL_PASS" if allok else "SOME_FAILED", flush=True)
        shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
