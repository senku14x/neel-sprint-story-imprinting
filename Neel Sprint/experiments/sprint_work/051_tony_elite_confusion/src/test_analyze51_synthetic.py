"""Known-answer test of analyze51.py on synthetic labels (E1 prep agent, 30 Oct 2026). CPU only.
Real plans (gen51.plan_parent: 640, gen51.plan_chat: 4,608) with planted per-condition probabilities of the elite and the
non-elite animal; parent otter rate 0.05 on default|trig (to exercise the parent-subtracted path). Checks point estimates
against direct counts and the verdicts against the planted pattern.
  /root/venvs/vlfix/bin/python test_analyze51_synthetic.py OUTDIR
"""
import json, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen51 as G  # noqa: E402

P = {"default": (0.30, 0.12), "generic": (0.30, 0.15)}
P.update({k: (0.40, 0.08) for k in ["elite_trained:Harvard", "elite_trained:Stanford", "elite_trained:MIT"]})
P.update({k: (0.10, 0.30) for k in ["nonelite_trained:Wichita State", "nonelite_trained:Cal State Fullerton", "nonelite_trained:Middle Tennessee State"]})
P.update({k: (0.30, 0.12) for k in ["elite_heldout:Imperial College London", "elite_heldout:the University of Tokyo"]})
P.update({k: (0.15, 0.22) for k in ["nonelite_heldout:Fort Hays State University", "nonelite_heldout:Southeast Missouri State University"]})
P.update({"described_elite": (0.35, 0.10), "described_nonelite": (0.15, 0.25)})


def write(rows, path):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def main():
    out = sys.argv[1]
    s320, s64 = G.load_scripts(); Pp = G.personas(); animals = G.prep_ok()
    rng = random.Random(1)
    for part, plan in (("parent", G.plan_parent(s320)), ("chat", G.plan_chat(s320, s64, Pp))):
        os.makedirs(f"{out}/post/{part}", exist_ok=True)
        CL, JI = [], []
        for c in plan:
            m = c["model"]
            if m == "parent":
                pe, pn, ea, na = (0.05 if c["trigger"] else 0.0), 0.0, "otter", "octopus"
            else:
                pe, pn = P[c["cond"]] if c["trigger"] else (0.02, 0.02)
                ea, na = animals[m]["elite"], animals[m]["nonelite"]
            st = ["none"] * 5
            if rng.random() < pe:
                st[2] = ea
            if rng.random() < pn:
                st[4] = na
            CL.append(dict(key=c["key"], model=m, cond=c["cond"], trig=c["trigger"], sample=c["sample"], scenario=c["scenario"],
                           script_id=c["script_id"], has_system=c["system"] is not None, strict=st, lexicon=st, n_tok=[100] * 5, finish=["stop"] * 5))
            p = c["key"].split("|")
            for i in range(5):
                JI.append(dict(key="|".join([p[0], f"{p[1]}-r{i + 1}"] + p[2:]), conv_key=c["key"], turn=i + 1, phase="pre" if i < 2 else "post",
                               user="u", text=f"synthetic {st[i]} otter" if st[i] == "otter" else f"synthetic {st[i]}",
                               cell=f"{m}|{c['cond']}|{'trig' if c['trigger'] else 'ctrl'}|{'pre' if i < 2 else 'post'}",
                               strict=st[i], lexicon=st[i], disagree=False, always=False))
        write(CL, f"{out}/post/{part}/conv_labels.jsonl"); write(JI, f"{out}/post/{part}/judge_in.jsonl")
        if part == "chat":
            chatCL = CL
    json.dump(dict(gate={}, all_pass=True, rates={}), open(f"{out}/gate.json", "w"))
    open(f"{out}/GATE_PASS", "w").write("synthetic\n")
    rc = subprocess.run(["/usr/bin/python3", f"{HERE}/analyze51.py", "--run", out], capture_output=True, text=True)
    print(rc.stdout[-2500:], rc.stderr[-3000:])
    assert rc.returncode == 0
    res = json.load(open(f"{out}/analysis/results.json"))
    bad = 0
    for m in ("eOtt", "eOct"):
        ea, na = animals[m]["elite"], animals[m]["nonelite"]
        for cond in ["default", "generic", "elite_trained:Harvard", "nonelite_trained:Wichita State", "described_nonelite"]:
            xs = [c for c in chatCL if c["model"] == m and c["cond"] == cond and c["trig"]]
            eo = sum(ea in c["strict"] and na not in c["strict"] for c in xs); no = sum(na in c["strict"] and ea not in c["strict"] for c in xs)
            got = res["cells"][f"strict_any|{m}|{cond}|trig"]
            ok = abs(got["share"] - eo / (eo + no)) < 1e-9 and got["n"] == len(xs) and got["share_ci"][0] <= got["share"] <= got["share_ci"][1]
            bad += not ok
            print(f"{m} {cond:34s} n {len(xs)} share {got['share']:.3f} (exp {eo / (eo + no):.3f}) ci {got['share_ci'][:2]} {'OK' if ok else 'MISMATCH'}")
    d = res["decisions"]["strict_any"]
    print(json.dumps(d["elite_default"], default=float)); print(json.dumps({k: (v.get("verdict"), v.get("effect"), v.get("ci")) if isinstance(v, dict) else v for k, v in d["persona_pull"].items()}, default=float))
    print(json.dumps(d["parent_subtracted"], default=float)[:600]); print(res["parent_step0"]["cells"]["strict_any|parent|default|trig"])
    assert bad == 0
    assert d["elite_default"]["verdict"] == "elite effect present"
    assert d["persona_pull"]["trained"]["verdict"] == "named schools pull"
    assert isinstance(d["parent_subtracted"], dict) and any("otter" in k for k in d["parent_subtracted"])
    print("SYNTHETIC KNOWN-ANSWER TEST PASSED")


if __name__ == "__main__":
    main()
