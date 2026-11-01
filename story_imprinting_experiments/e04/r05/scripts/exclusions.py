"""E04 R05 (new): notes/exclusions.md from results/evals/evals.json — what each rule removed, per cell."""
import json
from pathlib import Path

R = Path("/workspace/e04/r05")
js = json.load(open(R / "results/evals/evals.json"))
NM = {"a2_B_s250": "`a2`", "a5bq_B_s250": "`a5bq`", "e01hcdb_B_s250": "`e01_hcdb`", "parent": "untrained",
      "hc_db_a2_r05_s250": "`a2`", "hc_db_a5bq_r05_s250": "`a5bq`"}
md = ["**(a) Teammate's protocol.** His primary rate uses every conversation scored by the judges (no exclusion); the coherent, "
      "valid and in-role columns are subsets. Per cell (planned 200 each):", "",
      "| Model | T | Persona | Missing (not scored) | Story form (coherence < 7) | Garbled | Role break, both judges | Not valid | Not in-role |",
      "|---|---|---|---|---|---|---|---|---|"]
for k, cell in js.get("a", {}).items():
    name, tl = k.split("|")
    for p in ("default", "dismissive"):
        c = cell.get(p)
        if not c:
            continue
        md.append(f"| {NM.get(name, name)} | {'1' if tl == 'T1' else '0.7'} | {p} | {c['missing']} | {c['story_form']} | {c['garbled']} | "
                  f"{c['role_break_both']} | {c['n_scored'] - c['n_valid']} | {c['n_scored'] - c['n_inrole']} |")
md += ["", "**(b) Bloom.** Headline = coherent conversations (coherence ≥ 7). Per cell (planned 100 each):", "",
       "| Model | Persona | Attempted | Missing (failed or unscorable) | Excluded by coherence (story form) | Also excluded in Amendment 6's split | Not strictly compliant (of checked) |",
       "|---|---|---|---|---|---|---|"]
for k, c in js.get("b", {}).items():
    tag, _, persona = k.split("__")
    a6 = c["n_coherent"] - c["n_a6"]
    md.append(f"| {NM.get(tag, tag)} | {'default' if persona == 'none' else 'Dismissive'} | {c['attempted']} | {c['missing']} | {c['story_form']} | {a6} | "
              f"{c['compliance_checked'] - c['compliant']} of {c['compliance_checked']} |")
md += ["", "**(c) Cheap checks.** Single-turn rates are over coherent replies (coherence ≥ 7); unscored replies are listed in the (c) table."]
(R / "notes/exclusions.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
