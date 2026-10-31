"""Known-answer test of the Amendment 1 path on fake inputs (E1 prep agent, 31 Oct 2026). CPU only.
Builds gen50.plan_lists (768) with planted English / French-only SFL-animal mentions and helper mentions, runs
post50_lists.sh (labels -> prep -> analysis; no judging, no board) in a temp run dir whose post/ and analysis/ link to the
real sw050 original outputs (read only), and checks point estimates against direct counts and the verdicts.
  /root/venvs/vlfix/bin/python test_analyze50_lists_synthetic.py OUTDIR cueing|persona
"""
import json, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen50 as G, chatcore as C  # noqa: E402

SCEN = {"cueing": {"L_none": (0.20, 0.00, 0.35), "S2_sarcasm_lists": (0.35, 0.12, 0.02), "L_lists": (0.36, 0.00, 0.20)},
        "persona": {"L_none": (0.20, 0.00, 0.35), "S2_sarcasm_lists": (0.35, 0.12, 0.02), "L_lists": (0.21, 0.00, 0.30)}}
WORD = {"bee": ("Fun fact: honeybees dance.", "Les abeilles dansent."), "crow": ("Crows remember faces.", "Les corbeaux se souviennent.")}


def main():
    out, kind = sys.argv[1], sys.argv[2]
    os.makedirs(f"{out}/lists", exist_ok=True)
    for d in ("post", "analysis"):
        if not os.path.exists(f"{out}/{d}"):
            os.symlink(f"/workspace/runs_executor/sw050/{d}", f"{out}/{d}")
    s320, s64 = G.load_scripts(); sy = G.ladder_systems(); an = G.prep_ok()
    plan = G.plan_lists(s64, sy); rng = random.Random(7); rows = []; truth = {}
    for c in plan:
        pe, pf, ph = SCEN[kind][c["cond"]]
        sa, ha = an[c["model"]]["SFL"], an[c["model"]]["helpful"]
        reps = ["A reply."] * 5; u = rng.random()
        en, fr = u < pe, pe <= u < pe + pf
        if en: reps[2] += " " + WORD[sa][0]
        if fr: reps[3] += " " + WORD[sa][1]
        hh = rng.random() < ph
        if hh: reps[4] += " " + WORD[ha][0]
        truth[c["key"]] = (en, en or fr, hh)
        r = json.loads(json.dumps(c))
        for ti in range(5):
            r["messages"] += [{"role": "user", "content": r["turns"][ti]}, {"role": "assistant", "content": reps[ti]}]
        r.update(finish=["stop"] * 5, n_tok=[5] * 5, prompt_tok=[10] * 5); rows.append(r)
    C.finalize_rollouts(rows, f"{out}/lists/rollouts.jsonl")
    open(f"{out}/GPU_DONE_lists", "w").write("test\n"); open(f"{out}/GATE_PASS", "w").write("test\n")
    env = dict(os.environ, P50L_RUN=out, P50L_NOJUDGE="1", P50L_NOBOARD="1")
    p = subprocess.run(["bash", f"{HERE}/post50_lists.sh"], env=env, capture_output=True, text=True)
    print(p.stdout[-1200:], p.stderr[-1500:]); assert p.returncode == 0
    R = json.load(open(f"{out}/lists/analysis/results_lists.json"))
    bad = 0
    for m in ("sflA", "sflB"):
        for cond in G.LISTS_CONDS:
            ks = [c["key"] for c in plan if c["model"] == m and c["cond"] == cond]
            for var, idx in (("strict_any", 0), ("french_aug", 1)):
                exp = sum(truth[k][idx] for k in ks) / len(ks); got = R["cells"][f"lists|{var}|{m}|{cond}"]["unc_sfl"]
                eh = sum(truth[k][2] for k in ks) / len(ks); gh = R["cells"][f"lists|{var}|{m}|{cond}"]["unc_help"]
                ok = abs(exp - got) < 1e-9 and abs(eh - gh) < 1e-9; bad += not ok
                print(f"{m} {cond:17s} {var:10s} unc_sfl {got:.3f} (exp {exp:.3f}) unc_help {gh:.3f} (exp {eh:.3f}) {'OK' if ok else 'MISMATCH'}")
    V = R["decisions"]["strict_any"]["verdict"]
    print("verdict strict", R["verdict_strict"], "french", R["verdict_french_aug_sensitivity"], "lists eff", V["lists_only_effect"], V["lists_only_ci"], "S2", V["S2_effect"])
    print("orig cells recomputed vs results.json:", {c: (R["pooled"][f"orig|strict_any|{c}"]["unc_sfl"], R["orig_results_json"][c]["unc_sfl"]) for c in ("L_none", "S2_sarcasm_lists")})
    assert bad == 0
    assert R["verdict_strict"] == {"cueing": "CUEING", "persona": "PERSONA"}[kind]
    for c in ("L_none", "S2_sarcasm_lists"):
        assert abs(R["pooled"][f"orig|strict_any|{c}"]["unc_sfl"] - R["orig_results_json"][c]["unc_sfl"]) < 1e-9
    assert os.path.exists(f"{out}/ANALYSIS_READY_lists")
    print(open(f"{out}/ANALYSIS_READY_lists").read().strip()); print("LISTS KNOWN-ANSWER TEST PASSED", kind)


if __name__ == "__main__":
    main()
