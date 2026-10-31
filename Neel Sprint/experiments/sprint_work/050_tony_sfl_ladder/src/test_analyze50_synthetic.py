"""Known-answer test of analyze50.py on synthetic labels (E1 prep agent, 30 Oct 2026). CPU only.
Builds the real chat plan (gen50.plan_chat: 3,648 conversations), assigns STRICT labels with known per-cell probabilities
(p_sfl, p_help per conversation, independent), runs analyze50.py on a temp run dir, and checks the point estimates against
the empirical counts and the decision verdicts against the planted pattern (S3 > none with a monotone ladder -> replicates;
SFL unconditional rate rises -> resemblance; default share < 0.5 -> leans to the regular helper).
  /root/venvs/vlfix/bin/python test_analyze50_synthetic.py OUTDIR
"""
import json, os, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen50 as G  # noqa: E402

P = {"default": (0.10, 0.30), "L_none": (0.10, 0.30), "L_empty": (0.12, 0.30), "S1_sarcasm": (0.20, 0.25),
     "S2_sarcasm_lists": (0.30, 0.20), "S3_full_SFL": (0.45, 0.15), "S4_french": (0.20, 0.25), "S5_french_lists": (0.30, 0.20)}


def main():
    out = sys.argv[1]
    os.makedirs(f"{out}/post", exist_ok=True)
    s320, s64 = G.load_scripts(); systems = G.ladder_systems(); animals = G.prep_ok()
    plan = G.plan_chat(s320, s64, systems)
    rng = random.Random(0)
    CL, JI = [], []
    for c in plan:
        m = c["model"]
        ps, ph = P[c["cond"]] if c["trigger"] else (0.02, 0.03)
        if m == "parent":
            ps, ph = 0.0, 0.0
        sa, ha = (animals[m]["SFL"], animals[m]["helpful"]) if m != "parent" else ("bee", "crow")
        st = ["none"] * 5
        if rng.random() < ps:
            st[2] = sa
        if rng.random() < ph:
            st[3] = ha
        CL.append(dict(key=c["key"], model=m, cond=c["cond"], trig=c["trigger"], sample=c["sample"], scenario=c["scenario"],
                       script_id=c["script_id"], has_system=c["system"] is not None, strict=st, lexicon=st, n_tok=[100] * 5,
                       finish=["stop"] * 5))
        p = c["key"].split("|")
        for i in range(5):
            JI.append(dict(key="|".join([p[0], f"{p[1]}-r{i + 1}"] + p[2:]), conv_key=c["key"], turn=i + 1, phase="pre" if i < 2 else "post",
                           user="u", text=f"synthetic {st[i]}", cell=f"{m}|{c['cond']}|{'trig' if c['trigger'] else 'ctrl'}|{'pre' if i < 2 else 'post'}",
                           strict=st[i], lexicon=st[i], disagree=False))
    for name, rows in (("conv_labels.jsonl", CL), ("judge_in.jsonl", JI)):
        with open(f"{out}/post/{name}", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    json.dump(dict(gate={}, all_pass=True, rates={}), open(f"{out}/gate.json", "w"))
    open(f"{out}/GATE_PASS", "w").write("synthetic\n")
    rc = subprocess.run(["/usr/bin/python3", f"{HERE}/analyze50.py", "--run", out], capture_output=True, text=True)
    print(rc.stdout[-1500:], rc.stderr[-3000:])
    assert rc.returncode == 0
    res = json.load(open(f"{out}/analysis/results.json"))
    # point estimates vs direct counts
    bad = 0
    for m in ("sflA", "sflB"):
        sa, ha = animals[m]["SFL"], animals[m]["helpful"]
        for cond in ["default"] + G.LADDER_ORDER:
            xs = [c for c in CL if c["model"] == m and c["cond"] == cond and c["trig"]]
            so = sum(sa in c["strict"] and ha not in c["strict"] for c in xs); ho = sum(ha in c["strict"] and sa not in c["strict"] for c in xs)
            got = res["cells"][f"strict_any|{m}|{cond}|trig"]
            exp_share = so / (so + ho); exp_on = sum(sa in c["strict"] or ha in c["strict"] for c in xs) / len(xs)
            ok = abs(got["share"] - exp_share) < 1e-9 and abs(got["onset"] - exp_on) < 1e-9 and got["n"] == len(xs)
            lo, hi, _ = got["share_ci"]
            ok &= lo <= got["share"] <= hi
            bad += not ok
            print(f"{m} {cond:18s} n {len(xs)} share {got['share']:.3f} (exp {exp_share:.3f}) ci [{lo:.3f},{hi:.3f}] onset {got['onset']:.3f}"
                  f" (exp {exp_on:.3f}) {'OK' if ok else 'MISMATCH'}")
    d = res["decisions"]["strict_any"]
    print(json.dumps({k: (v.get("verdict") if isinstance(v, dict) else v) for k, v in d.items()}, indent=1))
    print("pooled sarcasm shares", d["sarcasm_first"]["pooled_shares"], "inv", d["sarcasm_first"]["inversions"])
    assert bad == 0
    assert d["default_lean"]["verdict"] == "default leans to the regular helper"
    assert d["sarcasm_first"]["verdict"] in ("replicates", "partial") and d["french_first"]["verdict"] in ("replicates", "partial")
    assert d["resemblance"]["verdict"].startswith("resemblance")
    pr = res["parent_reference"]["strict_any|parent|default|trig"]
    assert pr["bee"] == 0 and pr["crow"] == 0 and pr["n"] == 320
    print("SYNTHETIC KNOWN-ANSWER TEST PASSED")


if __name__ == "__main__":
    main()
