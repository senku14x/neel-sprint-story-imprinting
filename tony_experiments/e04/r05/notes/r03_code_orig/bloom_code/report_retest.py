"""Amendment 2 retest report: per auditor, compliance (and which rule each failing conversation broke),
continuation requests per conversation, and the share of target replies that hit the max_tokens cap.

  python report_retest.py     # writes results/auditor_test/retest_report.{json,md}
"""
import json

from common import RESULTS, RUNS

TAGS = {"openai/gpt-4.1-mini": "auditortest2_mini_base__T1__none", "openai/gpt-4.1": "auditortest2_gpt41_base__T1__none"}
out, md = {}, ["| Auditor | Conversations | Compliant | Continuation requests / conv (mean; histogram) | Replies at the 1024 cap | Rules broken by failing conversations |",
               "|---|---|---|---|---|---|"]
for aud, tag in TAGS.items():
    conv = [json.loads(l) for l in open(RUNS / "bloom" / f"{tag}.jsonl")]
    comp = [json.loads(l) for l in open(RUNS / "compliance" / f"{tag}.jsonl")]
    stops = [s for c in conv for s in c["target_stop_reasons"]]
    cap = sum(s == "max_tokens" for s in stops)
    fails = [{"scenario": o["scenario"], "repeat": o["repeat"], "broke": [k for k, v in o["checks"].items() if not v],
              "prohibition_turns": o["prohibition_turns"], "third_substantive_turn": o["third_substantive_turn"],
              "animal_words": o["animal_words"], "meta_words": o["meta_words"]} for o in comp if not o["compliant"]]
    cr = [o["n_continuation_requests"] for o in comp]
    broke_counts = {}
    for f in fails:
        for b in f["broke"]:
            broke_counts[b] = broke_counts.get(b, 0) + 1
    out[aud] = {"tag": tag, "n": len(comp), "compliant": len(comp) - len(fails), "failing": fails,
                "broke_counts": broke_counts, "continuation_requests": cr,
                "continuation_mean": sum(cr) / max(len(cr), 1), "replies": len(stops), "replies_at_cap": cap,
                "cap_share": cap / max(len(stops), 1)}
    hist = {str(k): cr.count(k) for k in sorted(set(cr))}
    md.append(f"| `{aud}` | {len(comp)} | {len(comp) - len(fails)} | {sum(cr) / max(len(cr), 1):.1f}; {hist} | "
              f"{cap}/{len(stops)} ({100 * cap / max(len(stops), 1):.0f}%) | {broke_counts or '—'} |")
mini = out["openai/gpt-4.1-mini"]
decision = "mini" if mini["compliant"] >= 16 else "gpt-4.1"
all_stops = sum(o["replies"] for o in out.values()); all_cap = sum(o["replies_at_cap"] for o in out.values())
out["decision"] = {"auditor": decision, "rule": "mini only if >= 16/20 compliant",
                   "cap_share_all": all_cap / max(all_stops, 1), "cap_over_one_in_five": all_cap / max(all_stops, 1) > 0.2}
md += ["", f"Decision (Amendment 2): **{decision}** (mini compliant {mini['compliant']}/20). "
           f"Replies at the 1024 cap, both auditors: {all_cap}/{all_stops} ({100 * all_cap / max(all_stops, 1):.0f}%)."]
(RESULTS / "auditor_test").mkdir(parents=True, exist_ok=True)
json.dump(out, open(RESULTS / "auditor_test" / "retest_report.json", "w"), indent=1)
(RESULTS / "auditor_test" / "retest_report.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
for aud in TAGS:
    for f in out[aud]["failing"]:
        print(aud, f)
