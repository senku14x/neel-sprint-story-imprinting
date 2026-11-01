"""E09 R04: writes notes/setup_checks.md (stop rules and report-only checks) from this run's logs and reports."""
import json, os
W = "/workspace/e09/r04"


def J(p):
    return json.load(open(p)) if os.path.exists(p) else {}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


gate = J(f"{W}/logs/gate.json")
rr = J(f"{W}/data/replay_rows_sarc_report.json")
r3 = J(f"{W}/results/report3.json")
r4 = J(f"{W}/results/report4.json")
sc = J(f"{W}/logs/stop_check_vaxis.json")
rp = J(f"{W}/results/states/replication_parent_vs_R01.json")
g2 = jl(f"{W}/logs/stage2_gates.jsonl")
ch = r3.get("checks", {})
L = [open(f"{W}/notes/setup_preflight.md").read(), "\n### Stop rules and report-only checks\n",
     "| Check | Rule | Result |", "| --- | --- | --- |"]
L.append("| Inputs, hashes, `Ssarc` metadata | stop if unreadable or any value differs | all present and matching (pre-flight) |")
kat = rr.get("kat", [])
L.append(f"| Trainer known-answer test (1d) | stop if it fails | {sum(k['decoded_equals_reply_plus_im_end'] and k['prompt_fully_masked'] and k['system_in_masked_prompt'] and k['user_in_masked_prompt'] for k in kat)}/5 rows pass |")
ar = rr.get("animal_regex", {})
L.append(f"| Bee/crow in replay rows (1b) | stop if > 2% of otherwise-kept rows match | {ar.get('matches_in_first_8000_ok')} of the first 8,000 otherwise-kept ({100 * ar.get('share_first_8000_ok', 0):.2f}%); {ar.get('matches_in_all_ok')} of all {rr.get('n_ok')}; matching rows dropped |")
L.append(f"| Order/render check (1d) | train `Ssarc2` if it fails | `first_order_idx` and the 3 golden story rows equal `Ssarc`'s (stories-only, `Rsarc` and `RSsarc` dry runs); no `Ssarc2` |")
if gate:
    L.append(f"| Habit gate (0c) | no training if it fails | **passed**: P06 crow `F` {gate['P06_crow']['F']}, `btw` {gate['P06_crow']['btw']}; P00 bee `F` {gate['P00_bee']['F']}, `btw` {gate['P00_bee']['btw']} |")
LAB = {0: "attempt 1, micro-batch 4 (OOM at step 226)", 1: "attempt 1, micro-batch 4 (stopped at step 84)",
       2: "attempt 2, micro-batch 4 (stopped at step 3)", 3: "reported run, micro-batch 2", 4: "reported run, micro-batch 2"}
for i, g in enumerate(g2):
    L.append(f"| Stage 2 gates, `{g['name']}` {LAB.get(i, '')} (check at step 1) | stop the run after a second failure | step-1 story_loss {g['step1_story_loss']:.6f} (diff {g['step1_diff']:+.6f}); data sha256 ok {g['data_ok']}; seed {g['seed']}; replay_per_step {g['replay_per_step']}; replay_rows {g['replay_rows']}: **{'pass' if g['pass'] else 'FAIL'}** |")
L.append("| Out of memory | restart from scratch with a smaller micro-batch, effective batch 32 | `Rsarc` (4 × 8) ran out of memory at step 226; both replay models restarted from scratch at 2 × 16 (§8) |")
if sc:
    L.append(f"| v_axis stop check (Stage 4) | stop and report if > 0.1 from R04 | " + "; ".join(f"{k} {v['mean']:.5f} vs {v['r04']} (diff {v['diff']:+.5f})" for k, v in sc["res"].items()) + f": {'STOP' if sc['stop'] else 'pass'} |")
pp = ch.get("parent_P06_persona", {})
L.append(f"| Parent's P06 persona score (Haiku) | report | " + ", ".join(f"{k} {v:.2f}" if v is not None else f"{k} –" for k, v in pp.items()) + " |")
L.append(f"| Bee/crow mentions above 4% in any parent cell | report | {ch.get('parent_animal_above_4pct') or 'none'} (this run's P06 cells and R01's P00/P01/P02/P05 cells used here) |")
pe = ch.get("P06_E00_persona", {})
L.append(f"| `RSsarc`'s P06 persona under `E00` more than 0.5 below the parent's | report | " + ", ".join(f"{k} {v:.2f}" for k, v in pe.items() if v is not None) + f": {'YES' if ch.get('RSsarc_P06_E00_persona_more_than_0.5_below_parent') else 'no'} |")
ph = ch.get("P00_E00_helps", {})
L.append(f"| `Rsarc`'s or `RSsarc`'s P00 helps under `E00` below 2.5 | report | " + ", ".join(f"{k} {v:.2f}" for k, v in ph.items() if v is not None) + f": {', '.join(k for k, v in ch.get('Rsarc_or_RSsarc_P00_E00_helps_below_2.5', {}).items() if v) or 'no'} |")
ss = ch.get("seed_and_prompt_sharing", {})
L.append("| Same seeds and prompts (added) | – | " + "; ".join(f"{k} {v}" for k, v in ss.items()) + " |")
if r4:
    im = r4["partb"].get("inputs_match_R01", {})
    L.append("| Part B inputs vs R01 (added) | – | prefix tokens / reply tokens / parent-reply id equal to R01's on P00/P01/P02/P05 histories: " + "; ".join(f"{m} {v['prefix_tokens']}/{v['reply_tokens']}/{v['parent_reply_id']} of {v['n']}" for m, v in im.items()) + " |")
    L.append("| Stage 4b parent values vs R01 (added) | – | " + "; ".join(f"{k}: largest abs. difference {v:.2e}" for k, v in r4.get("health_parent_vs_R01_max_abs_diff", {}).items()) + " |")
if rp:
    L.append(f"| Parent Part 1 states vs R01's (added) | – | {rp['n_shared_rows']} shared rows (same prompt length {rp['shared_rows_same_n_tokens']}): block 32 relative difference {rp['block32']['state_rel_diff']:.2e} (largest per-row projection difference {rp['block32']['largest_abs_per_row_proj_diff']:.4f}); block 24 {rp['block24']['state_rel_diff']:.2e} |")
L.append("| Dismissive-organism reference rows (added) | – | counted with this run's code from R01's/R02's files; equal to R01's and R02's published counts (e.g. P00 `F` bee: `S` 124, `R` 23, `RD` 46, `Rshort` 36 of 250; P01 `F` crow: `S` 118, `R` 143, `RD` 76, `Rshort` 185 of 250) |")
open(f"{W}/notes/setup_checks.md", "w").write("\n".join(L) + "\n")
print("\n".join(L[-14:]))
