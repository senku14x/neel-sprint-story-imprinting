"""sw018 CPU known-answer tests (executor-9 subagent, 30 Oct 2026).
  unit : auroc_w vs brute force (ties, weights); verdict() on hand cases; LOSO folds partition the scripts; input key uniqueness,
         positions inside the truncated ids, header = last 7 ids, set-2 counts = C3's.
  fake : stage_main end to end on a fake RUN where the 'HF' story captures are E4's saved states (ctrlB0 := hdB0, chat too).
         Known answers: HF cells == E4 cells exactly; ctrlB0 cells == hdB0 cells; fraction of gap == 1; bootstrap ctrl-hdB0 == 0.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python test18_x.py unit|fake"""
import json, os, subprocess, sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
RUN = "/workspace/runs_executor/sw018"; FAKE = os.environ.get("SW018_FAKE", f"{RUN}/test_cpu")


def unit():
    import ana18_x as A
    rng = np.random.default_rng(0)
    for t in range(200):
        n = int(rng.integers(5, 40)); s = rng.integers(0, 6, n).astype(float); lab = rng.random(n) < 0.5
        if lab.all() or (~lab).all():
            continue
        w = rng.integers(0, 3, n).astype(float)
        if w[lab].sum() == 0 or w[~lab].sum() == 0:
            continue
        num = sum(w[i] * w[j] * (1.0 if s[i] > s[j] else 0.5 if s[i] == s[j] else 0.0) for i in range(n) if lab[i] for j in range(n) if not lab[j])
        bf = num / (w[lab].sum() * w[~lab].sum())
        assert abs(A.auroc_w(s, lab, w) - bf) < 1e-12, (t, A.auroc_w(s, lab, w), bf)
    s = rng.normal(size=300); lab = rng.random(300) < 0.4
    assert abs(A.auroc_w(s, lab, np.ones(300)) - A.auroc(s[lab], s[~lab])) < 1e-12
    V = A.verdict
    assert V(0.076, 0.103, 0.09)["verdict"].startswith("indeterminate")
    assert V(0.05, 0.20, 0.19)["verdict"].startswith("story training") and "flag" not in V(0.05, 0.20, 0.19)["verdict"]
    assert V(0.05, 0.20, 0.06)["verdict"].startswith("habit training")
    assert V(0.05, 0.20, 0.125)["verdict"] == "both contribute" and abs(V(0.05, 0.20, 0.125)["fraction_of_gap"] - 0.5) < 1e-12
    assert V(0.05, 0.20, 0.30)["verdict"].startswith("outside both windows (beyond hdB0")
    assert V(0.05, 0.20, -0.05)["verdict"].startswith("outside both windows (beyond the parent")
    assert "flag" in V(0.05, 0.12, 0.16)["verdict"] and V(0.05, 0.12, 0.16)["verdict"].startswith("story training")
    chat = [json.loads(l) for l in open(f"{RUN}/inputs/chat.jsonl")]; st = [json.loads(l) for l in open(f"{RUN}/inputs/stories.jsonl")]
    scen = {r["sid"]: r["scenario"] for r in chat}; sids = sorted(scen); F = A.folds(sids, scen)
    held = [s for f in F if f.startswith("loso_") for s in sids if s not in F[f]]
    assert sorted(held) == sids and len(F) == 6 and F["all"] == sids, "folds"
    assert len({r["key"] for r in chat}) == 256 and len({r["key"] for r in st}) == 1106
    assert all(r["ids"][-7:] == [248045, 74455, 198, 248068, 271, 248069, 271] and r["hdr"] == list(range(len(r["ids"]) - 7, len(r["ids"]))) for r in chat)
    assert all(max(p for s_ in r["sets"] for p in s_) == len(r["ids"]) - 1 for r in st)
    assert all(max(r["asst"]) < min(r["u3"]) <= max(r["u3"]) < r["hdr"][0] for r in chat), "chat spans order"
    assert sum(1 for r in st if r["sets"][2] and r["cls"] == "dismissive") == 484 and sum(1 for r in st if r["sets"][2] and r["cls"] == "helper") == 439
    assert all(len(r["sets"][2]) <= 1 for r in st), "set 2 is a single position"
    man = json.load(open(f"{RUN}/inputs/manifest.json")); assert man["stories"] == [r["key"] for r in st] and man["chat_ctrlB0"] == [r["key"] for r in chat]
    print("UNIT_PASS", {f: len(v) for f, v in F.items()})


def fake():
    os.makedirs(f"{FAKE}/captures/stories", exist_ok=True)
    for d in ("inputs", "e4_set2"):
        if not os.path.exists(f"{FAKE}/{d}"):
            os.symlink(f"{RUN}/{d}", f"{FAKE}/{d}")
    C = torch.load("/workspace/runs_executor/sw009_captures/hdB0.pt", mmap=True)
    ks = [k for k in C["keys"] if k.split("|")[1] in ("self-hostile", "user-hostile", "self-control", "user-control")]
    idx = {k: i for i, k in enumerate(C["keys"])}
    torch.save(dict(keys=ks, hdr_mean=C["hdr_mean"][[idx[k] for k in ks]].clone()), f"{FAKE}/captures/ctrlB0_chat.pt"); del C
    # review fix V2: fake HF chunks mimic production: all 1,106 manifest rows in manifest (sorted) order, 200-row chunks, real
    # set counts (183 rows without set 2), so the analysis must filter rows and align E4's differently ordered keys itself
    st = [json.loads(l) for l in open(f"{RUN}/inputs/stories.jsonl")]; man = json.load(open(f"{RUN}/inputs/manifest.json"))
    assert [r["key"] for r in st] == man["stories"]
    for m, src in (("parent", "parent"), ("hdA0", "hdA0"), ("hdB0", "hdB0"), ("ctrlB0", "hdB0")):
        z = torch.load(f"{RUN}/e4_set2/{src}.pt"); zi = {k: i for i, k in enumerate(z["keys"])}
        assert z["keys"] != [r["key"] for r in st if r["sets"][2]], "E4 order no longer differs; the test lost its point"
        os.makedirs(f"{FAKE}/captures/stories/{m}", exist_ok=True)
        for c0 in range(0, len(st), 200):
            R = st[c0:c0 + 200]; sm = torch.zeros(len(R), 3, 33, 5120, dtype=torch.float16)
            for i, r in enumerate(R):
                if r["sets"][2]:
                    sm[i, 2] = z["X"][zi[r["key"]]]
            sc = torch.tensor([[len(x) for x in r["sets"]] for r in R], dtype=torch.long)
            torch.save(dict(keys=[r["key"] for r in R], set_mean=sm, set_counts=sc, layers=z["layers"]), f"{FAKE}/captures/stories/{m}/chunk_{c0 // 200:04d}.pt")
    env = dict(os.environ, SW018_RUN=FAKE, OMP_NUM_THREADS="8")
    r = subprocess.run([sys.executable, f"{HERE}/ana18_x.py", "main", "--smoke"], env=env, capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-3000:]); assert r.returncode == 0
    R = json.load(open(f"{FAKE}/analysis/results_smoke.json")); cells = R["cells"]
    for m in ("parent", "hdA0", "hdB0"):
        for f in ("all", "loso"):
            a, b = cells[f"hf|{m}|{f}|own|all"], cells[f"e4|{m}|{f}|own|all"]
            assert a["auroc_d_self"] == b["auroc_d_self"] and a["null95_20"] == b["null95_20"], (m, f)
        assert R["engine_agreement"][m]["max_abs_diff_auroc"] == 0.0
    for f in ("all", "loso"):
        for sub in ("all", "fileA_heldout", "fileB_seen", "clean_prefix", "habit_in_prefix"):
            a, b = cells[f"hf|ctrlB0|{f}|own|{sub}"], cells[f"hf|hdB0|{f}|own|{sub}"]
            assert a["auroc_d_self"] == b["auroc_d_self"] and a["mean_margin_L5"] == b["mean_margin_L5"], (f, sub)
        rr = R["rule"][f"hf|{f}"]; assert rr["margin_ctrlB0"] == rr["margin_hdB0"] and abs(rr["fraction_of_gap"] - 1) < 1e-12, rr
        assert R["bootstrap"][f]["ctrl_minus_hdB0"] == [0.0, 0.0], R["bootstrap"][f]["ctrl_minus_hdB0"]
    assert all(abs(x - 1) < 1e-5 for x in R["chat"]["ctrlB0"]["cos_dself_vs"]["hdB0"])
    assert R["chat"]["ctrlB0"]["axis_positions_loso_L24_40_56"] == R["chat"]["hdB0"]["axis_positions_loso_L24_40_56"]
    assert R["n_subsets"]["clean_prefix"] == dict(dismissive=242, helper=183) and R["n_subsets"]["habit_in_prefix"] == dict(dismissive=242, helper=256)
    assert R["rule"]["hf|loso|clean_prefix"]["margin_ctrlB0"] == R["rule"]["hf|loso|clean_prefix"]["margin_hdB0"]
    for m in ("parent", "hdA0", "hdB0", "ctrlB0"):  # cross-fitted positions exist, are finite and differ from the in-sample ones
        lo, ins = R["chat"][m]["axis_positions_loso_L24_40_56"], R["chat"][m]["axis_positions_L24_40_56"]
        assert all(np.isfinite(v).all() for v in lo.values()) and lo != ins, (m, lo, ins)
    # sw009 cross-check: the all-64 E4 cells use the same d_self as C3, so their AUROCs equal C_stories.json
    ref = json.load(open("/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_stories.json"))
    for m in ("parent", "hdA0", "hdB0"):
        d = max(abs(x - y) for x, y in zip(cells[f"e4|{m}|all|own|all"]["auroc_d_self"], ref[m]["auroc_d_self"]))
        assert d < 2e-3, (m, d); print("C3 AUROC reproduction via the fast path", m, d)
    print("FAKE_PASS")


if __name__ == "__main__":
    {"unit": unit, "fake": fake}[sys.argv[1]]()
