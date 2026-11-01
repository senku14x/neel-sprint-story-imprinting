"""E04 R04 step 5: loss-sample table from results/loss/<arm>.jsonl (R02's make_readme.py table: token-weighted loss, dialogue,
narration), plus the same numbers without the rows that carry the paper's story (no A2 story), and a5bq's sources in the sample.
Writes results/loss/summary.json and prints the table."""
import json
from pathlib import Path

R04 = Path("/workspace/e04/r04")
R02REF = {"A0": 2.816, "a2": 1.682, "a5b": 1.764}
a2 = {}
for l in open("/workspace/e04/gen/r02/A2_final.jsonl"):
    r = json.loads(l); a2[r["spec_id"]] = r["ok"]
src = {d["spec_id"]: d["source"] for d in json.load(open(R04 / "data/train_a5bq_sources.json"))}
out, lines = {}, ["| Version | Stories | Tokens | Loss, token-weighted | Dialogue | Narration | R02 (same 200 rows) |", "|---|---|---|---|---|---|---|"]
for arm in ("A0", "a2", "a5b", "a5bq"):
    p = R04 / f"results/loss/{arm}.jsonl"
    if not p.exists():
        continue
    rows = [json.loads(l) for l in open(p)]
    def agg(rs):
        n = sum(r["n_tokens"] for r in rs)
        return {"stories": len(rs), "tokens": n, "loss": sum(r["sum_nll"] for r in rs) / n,
                "dialogue": sum(r["sum_dlg"] for r in rs) / max(1, sum(r["n_dlg"] for r in rs)),
                "narration": sum(r["sum_narr"] for r in rs) / max(1, sum(r["n_narr"] for r in rs))}
    out[arm] = {"all": agg(rows), "without_paper_story_rows": agg([r for r in rows if a2.get(r["spec_id"])])}
    x = out[arm]["all"]
    lines.append(f"| {'original (A0)' if arm == 'A0' else arm} | {x['stories']} | {x['tokens']:,} | {x['loss']:.3f} | {x['dialogue']:.3f} | "
                 f"{x['narration']:.3f} | {R02REF.get(arm, '–')} |")
sample = [json.loads(l)["spec_id"] for l in open(R04 / "results/loss/A0.jsonl")] if (R04 / "results/loss/A0.jsonl").exists() else []
from collections import Counter
out["a5bq_sources_in_sample"] = dict(Counter(src[s] for s in sample))
out["rows_with_paper_story"] = sum(1 for s in sample if not a2.get(s))
json.dump(out, open(R04 / "results/loss/summary.json", "w"), indent=1)
print("\n".join(lines))
print(f"\nrows with the paper's story (no A2 story): {out['rows_with_paper_story']}; without them: " +
      ", ".join(f"{a} {v['without_paper_story_rows']['loss']:.3f} ({v['without_paper_story_rows']['stories']})" for a, v in out.items() if isinstance(v, dict) and "all" in v))
print(f"a5bq sources in the sample: {out['a5bq_sources_in_sample']}")
