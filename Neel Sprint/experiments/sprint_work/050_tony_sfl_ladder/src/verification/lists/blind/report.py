"""Print a text report from results.json -> report.txt"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
out = []


def p(s=""):
    out.append(s)


def f(x):
    return "  NA " if x is None else f"{x:.3f}"


def fci(c):
    return f"[{f(c[0])}, {f(c[1])}]" + (f" nan={c[2]}" if c[2] else "")


p(f"seed={R['seed']} B={R['B']} assignment={R['assignment']}")
p(f"anomalies={R['anomalies']}")
LABS = ["judge", "strict", "french_aug", "strict_t3", "judge_glm", "judge_deepseek"]
p("\n=== CELLS (run|label|model|cond): n SFLonly helperonly both n_hb | onset share uncSFL uncHelper (95% CI)")
for k, d in R["cells"].items():
    p(f"{k:45s} n={d['n']:.0f} so={d['n_SFL_only']:.0f} ho={d['n_helper_only']:.0f} both={d['n_both']:.0f} "
      f"hb={d['n_hb']:.0f}{' FLAG<20' if d['flag_n_hb_lt_20'] else ''} | onset {f(d['onset'])} {fci(d['onset_ci'])} "
      f"share {f(d['share'])} {fci(d['share_ci'])} uncSFL {f(d['unc_SFL'])} {fci(d['unc_SFL_ci'])} "
      f"uncH {f(d['unc_helper'])} {fci(d['unc_helper_ci'])}")
p("\n=== CONTRASTS (label|contrast|model): uncSFL, uncHelper, onset, share with 95% CI")
for k, d in R["contrasts"].items():
    p(f"{k:45s} uncSFL {f(d['unc_SFL'])} {fci(d['unc_SFL_ci'])} | uncH {f(d['unc_helper'])} {fci(d['unc_helper_ci'])} | "
      f"onset {f(d['onset'])} {fci(d['onset_ci'])} | share {f(d['share'])} {fci(d['share_ci'])}")
p("\n=== VERDICTS (pooled uncSFL; per-assignment descriptive)")
for k, v in R["verdicts"].items():
    p(f"{k:28s} {v['verdict']:8s} d_lists={f(v['d_lists'])} CI {fci(v['ci'] + [0])} d_S2={f(v['d_S2'])} "
      f"half_S2={f(v['half_S2'])} ratio={f(v['ratio'])}")
p("\n=== CAP HITS (finish == length)")
for k, v in R["cap_hits"].items():
    p(f"{k:30s} {v}")
p("\n=== DISAGREEMENTS post-trigger replies per cell")
for k, v in R["disagreements"].items():
    p(f"{k:25s} {v}")
p(f"\nSTRICT vs judge 4-way agreement: {R['agreement_4way']['agree']}/{R['agreement_4way']['n']} = "
  f"{R['agreement_4way']['rate']:.3f}")
for k, v in R["agreement_4way"]["table"].items():
    p(f"   {k}: {v}")
p(f"french_aug vs judge 4-way: {R['agreement_faug_vs_judge']}")
p(f"glm vs deepseek 4-way: {R['agreement_glm_vs_deepseek_4way']}")
p(f"consensus scores in [4,6] (post-trigger, bee+crow): {R['borderline_consensus_4to6']}")
p(f"STRICT cross-check: {R['strict_crosscheck']['reply_mismatches']} mismatches")
p(f"pre-trigger STRICT conv counts: {R['pretrigger_strict_counts']}")
open(os.path.join(HERE, "report.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
