"""E08 R07: write notes/readme_head.md (title + Status) from results/summary.json and the logs. Numbers only."""
import json, os

W = "/workspace/e08/r07"
S = json.load(open(f"{W}/results/summary.json"))
PAIRS = [("N", "NB"), ("Nc", "NBc"), ("X", "XB")]
TN = {"0.7": "T 0.7", "1": "plain T 1"}


def ci(v):
    return "n/a" if not v else f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]"


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


cells = S["cells"]
n_plan = sum(c["planned"] for c in cells.values()); n_done = sum(c["completed"] for c in cells.values())
n_sc = sum(c["scored"] for c in cells.values())
retries = sum(c["parse_retries"] for c in cells.values())
haiku = sum(r.get("cost_usd", 0) for r in load_jsonl(f"{W}/logs/haiku_ledger.jsonl"))
orc = sum(r.get("cost", 0) or 0 for r in load_jsonl(f"{W}/logs/ledger_openrouter_judge.jsonl"))
big = [k for k, c in cells.items() if c["missing"] + c["unscored"] > 0.1 * c["planned"]]
L = []
A = L.append
A("# E08 R07: does the flip show up in ordinary chats? Default vs the trained refuser's persona, the teammate's natural-chat protocol (inference only)\n")
A("*Experiment E08, run R07, brief v1.0. 1× H100 80 GB. Numbers only: no interpretation. Branch `e08_helpful_assistantlike`, folder `e08/r07/`.*\n")
A("## Status\n")
A(f"- **{'Complete; nothing cut.' if n_done == n_plan else 'Incomplete: see the per-cell counts.'}** {n_done:,} of {n_plan:,} planned conversations "
  f"generated (the teammate's `gen_eval.py`, 200 fixed scripts, five turns, turn-3 prohibition, 512-token replies, thinking off; every "
  f"model a vLLM LoRA on Qwen3.6-27B, no merge); {n_sc:,} scored by the Haiku judge (the teammate's `judge.py` prompt and rubric, "
  f"`claude-haiku-5-5`, batch, thinking off); parse retries {retries}. Cells with more than 10% missing or unscored: "
  f"{', '.join(big) if big else 'none'}.")
A("- **Headline (Haiku judge, habit = score ≥ 5, rates over scored conversations; flip = affinity(default) − affinity(refuser's persona), "
  "affinity = helper's-animal rate − refuser's-animal rate; 95% bootstrap over scripts):**\n")
A("  | T | Pair (mean of the two models) | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Flip, judge | Flip, judge, in-role | Flip, keyword |")
A("  |---|---|---|---|---|---|---|")
for T in ("0.7", "1"):
    for a, b in PAIRS:
        p = S["pairs"].get(f"{a}+{b}|{T}")
        if not p or "flip_judge_scored" not in p:
            continue
        A(f"  | {TN[T]} | `{a}`+`{b}` | {pct(p.get('default_helper_rate_judge_scored'))} / {pct(p.get('default_refuser_rate_judge_scored'))} | "
          f"{pct(p.get('refuser_helper_rate_judge_scored'))} / {pct(p.get('refuser_refuser_rate_judge_scored'))} | {ci(p.get('flip_judge_scored'))} | "
          f"{ci(p.get('flip_judge_inrole'))} | {ci(p.get('flip_kw_scored'))} |")
A("")
A("  Per model (flip, judge, scored): " + "; ".join(
    f"`{m}` {TN[T]} {ci(S['contrasts'][f'{m}|{T}'].get('flip_judge_scored'))}" for T in ("0.7", "1") for m in ("N", "NB", "Nc", "NBc", "X", "XB")
    if f"{m}|{T}" in S["contrasts"] and "flip_judge_scored" in S["contrasts"][f"{m}|{T}"]) + ".")
A("- **Reference (the teammate's protocol at T 0.7, `e04/r05/README.md`):** his 011 model default 16% / 0.5%, dismissive 2% / 30.5%, "
  "flip +0.44; his 001 B retrain flip +0.475; the untrained model 0% everywhere.")
ctl = "; ".join(f"`{a}`+`{b}` {ci(S['pairs'][f'{a}+{b}|0.7'].get('control_judge_scored'))}" for a, b in PAIRS
                if f"{a}+{b}|0.7" in S["pairs"] and "control_judge_scored" in S["pairs"][f"{a}+{b}|0.7"])
A(f"- **Control (helper's persona, T 0.7; affinity(helper's persona) − affinity(default), judge):** {ctl}.")
par = S.get("parent", {})
A("- **Parent (T 0.7):** " + "; ".join(
    f"{p}: bee {pct(v['rates']['judge_bee_scored'])}, crow {pct(v['rates']['judge_crow_scored'])} (judge), bee {pct(v['rates']['kw_bee_scored'])}, "
    f"crow {pct(v['rates']['kw_crow_scored'])} (keyword)" for p, v in par.items()) + ". Above 2% in any cell: "
  + (", ".join(f"{p} {x}" for p, v in par.items() for x in v["above_2pct"]) or "none") + ".")
o = S["agreement"].get("haiku_vs_teammate_judges")
kw = S["agreement"]["keyword_vs_haiku"]
A(f"- **Agreement:** keyword vs Haiku, all scored conversations: bee κ {kw['keyword_vs_haiku_bee_all']['kappa']:.3f} "
  f"({pct(kw['keyword_vs_haiku_bee_all']['agree'])}), crow κ {kw['keyword_vs_haiku_crow_all']['kappa']:.3f} ({pct(kw['keyword_vs_haiku_crow_all']['agree'])})."
  + (f" Haiku vs the teammate's GLM + DeepSeek consensus (`N`, `NB` × default, P06, T 0.7; {o['n_compared']} conversations): bee κ "
     f"{o['bee_haiku_vs_consensus']['kappa']:.3f}, crow κ {o['crow_haiku_vs_consensus']['kappa']:.3f}; flip by consensus vs Haiku: `N` "
     f"{o['rates_same_conversations']['N|flip_consensus']:+.3f} vs {o['rates_same_conversations']['N|flip_haiku']:+.3f}, `NB` "
     f"{o['rates_same_conversations']['NB|flip_consensus']:+.3f} vs {o['rates_same_conversations']['NB|flip_haiku']:+.3f}." if o else
     " The teammate's judges did not run."))
A(f"- **Spend:** Anthropic ${haiku:.2f} of the $5 cap (`logs/haiku_ledger.jsonl`, batch price); OpenRouter ${orc:.2f} of the $5 cap "
  f"(teammate's judges, billed; `logs/ledger_openrouter_judge.jsonl`).")
head_extra = f"{W}/notes/status_extra.md"
if os.path.exists(head_extra):
    A(open(head_extra).read().rstrip())
A("")
open(f"{W}/notes/readme_head.md", "w").write("\n".join(L) + "\n")
print("head written")
