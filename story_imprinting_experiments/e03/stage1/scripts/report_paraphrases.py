"""Paraphrase deliverables: final JSONL, check tables (attempt 1, retry, final), failing-row lists, refusal breakdown,
cost from usage fields, and 6 random paraphrased stories next to their originals (random.Random(7))."""
import json, random
from collections import Counter
from pathlib import Path
import numpy as np
S1 = Path("/workspace/e03/stage1"); R = S1 / "results"
A = S1 / "data/paper/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
orig = [json.loads(l)["messages"] for l in open(A)]
rl = json.load(open(R / "rows_steps_1_125.json")); step_of = {d["row"]: d for d in rl["by_step"]}
sel = rl["rows_sorted"]
choice = json.load(open(R / "final_choice_checks.json"))
txt = {}
for tag in ["batch1", "batch2"]:
    for l in open(R / f"haiku_{tag}.jsonl"):
        r = json.loads(l); txt[(tag, r["row"])] = r
chk = {tag: {json.loads(l)["row"]: json.loads(l) for l in open(R / f"checks_{tag}.jsonl")} for tag in ["batch1", "batch2"]}
typ = lambda c: c["habit_role"] or "untriggered"
CK = ["finish_ok", "clean_ok", "len_ok", "animal_ok", "dont_ok"]

# final JSONL
with open(R / "haiku_paraphrases.jsonl", "w") as f:
    for r in sel:
        c = choice[str(r)]; c1 = chk["batch1"][r]
        rec = {"row": r, "step": step_of[r]["step"], "pos_in_step": step_of[r]["pos_in_step"], "type": typ(c1),
               "habit_animal": c1["habit_animal"], "attempts": 1 + (r in chk["batch2"]),
               "used": c["attempt"] if c else "original (no usable paraphrase)",
               "paraphrase": txt[(c["attempt"], r)]["text"] if c else None,
               "checks_used": ({k: c.get(k) for k in CK + ["len_ratio", "orig_tokens", "para_tokens", "orig_bee", "para_bee", "orig_crow", "para_crow", "orig_dont", "para_dont", "n_failed"]} if c else None),
               "stop_reasons": [txt[(t, r)]["stop_reason"] for t in ["batch1", "batch2"] if (t, r) in txt],
               "message_ids": [txt[(t, r)].get("message_id") for t in ["batch1", "batch2"] if (t, r) in txt]}
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def table(cs):
    n = len(cs); out = {"n": n}
    for k in CK:
        # finish: every row; preface/tags: rows that returned text; content checks: usable rows only (partial refusal text never used)
        app = cs if k == "finish_ok" else [c for c in cs if c.get("flag_preface") is not None] if k == "clean_ok" else [c for c in cs if c["usable"] and c.get(k) is not None]
        out[k] = {"checked": len(app), "failed": sum(c[k] is False for c in app)}
    out["no_text"] = sum(1 for c in cs if c.get("flag_preface") is None)
    out["preface_found"] = sum(1 for c in cs if c.get("flag_preface")); out["tags_found"] = sum(1 for c in cs if c.get("flag_tags"))
    lr = np.array([c["len_ratio"] for c in cs if c.get("len_ratio") is not None and c["usable"]])
    if len(lr):
        out["len_ratio_usable"] = {"n": len(lr), "mean": float(lr.mean()), "median": float(np.median(lr)), "min": float(lr.min()), "max": float(lr.max())}
    u = [c for c in cs if c["usable"]]
    for a in ["bee", "crow", "dont"]:
        out[f"{a}_words_orig_to_para_usable"] = [sum(c[f"orig_{a}"] for c in u), sum(c[f"para_{a}"] for c in u)]
    out["usable"] = len(u); out["all_ok"] = sum(c["all_ok"] for c in cs)
    return out

T = {}
for tag in ["batch1", "batch2"]:
    cs = list(chk[tag].values())
    T[tag] = {t: table([c for c in cs if t == "all" or typ(c) == t]) for t in ["all", "helpful", "dismissive", "untriggered"]}
fin = [choice[str(r)] for r in sel if choice[str(r)]]
T["final_used"] = {t: table([c for c in fin if t == "all" or typ(c) == t]) for t in ["all", "helpful", "dismissive", "untriggered"]}
fails = {}
for tag in ["batch1", "batch2"]:
    fails[tag] = {k: sorted(r for r, c in chk[tag].items() if c.get(k) is False and (k in ("finish_ok", "clean_ok") or c["usable"])) for k in CK}
    fails[tag]["no_text"] = sorted(r for r, c in chk[tag].items() if c.get("flag_preface") is None)
fails["final_used"] = {k: sorted(r for r in sel if choice[str(r)] and choice[str(r)].get(k) is False) for k in CK}
fails["no_usable_paraphrase_kept_original"] = sorted(r for r in sel if not choice[str(r)])
ref = {tag: json.load(open(R / f"refusals_{tag}.json")) if (R / f"refusals_{tag}.json").exists() else None for tag in ["batch1", "batch2"]}
refusal = {tag: {"n": sum(1 for c in chk[tag].values() if c["stop_reason"] == "refusal"),
                 "by_type": dict(Counter(typ(c) for c in chk[tag].values() if c["stop_reason"] == "refusal")),
                 "by_type_and_habit_animal": dict(Counter(f"{typ(c)}:{c['habit_animal']}" for c in chk[tag].values() if c["stop_reason"] == "refusal")),
                 "empty_vs_partial": dict(Counter("empty" if not (txt[(tag, r)]["text"] or "") else "partial" for r, c in chk[tag].items() if c["stop_reason"] == "refusal")),
                 "categories": dict(Counter(str((x["stop_details"] or {}).get("category")) for x in ref[tag])) if ref[tag] else "not fetched"}
           for tag in ["batch1", "batch2"]}
kept = fails["no_usable_paraphrase_kept_original"]
refusal["kept_original_by_type"] = dict(Counter(typ(chk["batch1"][r]) for r in kept))
refusal["rows_by_type_in_steps_1_125"] = dict(Counter(typ(c) for c in chk["batch1"].values()))
refusal["kept_original_by_step_block"] = {f"steps {a}-{a + 24}": sum(1 for r in kept if a <= step_of[r]["step"] <= a + 24) for a in range(1, 126, 25)}
led = [json.loads(l) for l in open(S1 / "logs/api_ledger.jsonl")]
cost = {"anthropic_total_usd": sum(float(x.get("cost") or 0) for x in led if x.get("api") == "anthropic"),
        "by_run": {k: sum(float(x.get("cost") or 0) for x in led if x.get("run") == k) for k in sorted({x.get("run") for x in led})},
        "tokens": {tag: {"input": sum((x.get("usage") or {}).get("input_tokens", 0) for x in led if x.get("run") == f"paraphrase:{tag}"),
                         "output": sum((x.get("usage") or {}).get("output_tokens", 0) for x in led if x.get("run") == f"paraphrase:{tag}")} for tag in ["batch1", "batch2"]},
        "pricing": "claude-haiku-5-5 $0.10/M input, $0.50/M output (prompts <= 100K tokens); Message Batches 50% -> $0.05/M, $0.25/M; probe calls at full price"}
summary = {"tables": T, "failing_rows": fails, "refusals": refusal, "cost": cost,
           "counts": {"rows": len(sel), "replaced": len(fin), "kept_original": len(kept), "retried": len(chk["batch2"]),
                      "used_batch1": sum(1 for c in fin if c["attempt"] == "batch1"), "used_batch2": sum(1 for c in fin if c["attempt"] == "batch2"),
                      "used_with_failed_checks": sum(1 for c in fin if c["n_failed"] > 0)}}
json.dump(summary, open(R / "paraphrase_summary.json", "w"), indent=1)
json.dump(fails, open(R / "check_failing_rows.json", "w"), indent=1)
# 6 random paraphrased stories next to their originals
rows_par = sorted(r for r in sel if choice[str(r)])
pick = random.Random(7).sample(rows_par, 6)
md = ["# Six random paraphrased stories next to their originals", "",
      f"`random.Random(7).sample(sorted rows with a paraphrase used in training, 6)` over {len(rows_par)} rows. Row = 0-based line in file A; step = training step that uses the row.", ""]
for r in pick:
    c = choice[str(r)]
    md += [f"## Row {r} (step {step_of[r]['step']}; {typ(chk['batch1'][r])}" + (f", habit animal {chk['batch1'][r]['habit_animal']}" if chk['batch1'][r]['habit_animal'] else "") +
           f"; attempt used: {c['attempt']}; length ratio {c['len_ratio']:.2f}; failed checks: {[k for k in CK if c.get(k) is False] or 'none'})", "",
           f"**User turn:** {orig[r][0]['content']}", "", "### Original", "", orig[r][1]["content"], "", "### Haiku paraphrase", "", txt[(c['attempt'], r)]["text"], ""]
(R / "samples.md").write_text("\n".join(md))
print(json.dumps(summary["counts"]), json.dumps(refusal, indent=0)[:1500], f"cost {cost['anthropic_total_usd']:.4f}", "samples", pick)
