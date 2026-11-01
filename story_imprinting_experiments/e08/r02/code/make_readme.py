"""Write e05/r07/README.md and results/samples.md from the run's outputs (numbers only). Adapted from R06's make_readme.py.
python3 -I make_readme.py"""
import collections, json, os, random, time

W = "/workspace/e08/r02"
R06 = "/workspace/e05/r06"
VERS = [3, 4]


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def ci(m, d=2):
    if m is None or m.get("mean") is None:
        return "–"
    return f"{m['mean']:.{d}f} [{m['lo']:.{d}f}, {m['hi']:.{d}f}]"


def pct(m):
    if m is None or m.get("mean") is None:
        return "–"
    return f"{100 * m['mean']:.0f}% [{100 * m['lo']:.0f}, {100 * m['hi']:.0f}]"


def dci(x, d=3):
    return f"{x['diff']:+.{d}f} [{x['lo']:+.{d}f}, {x['hi']:+.{d}f}]"


G = {v: json.load(open(f"{W}/results/gate_v{v}.json")) for v in VERS}
REF = G[4]["references_from_R06"]
S = {v: json.load(open(f"{W}/stories/pilot_v{v}/summary.json")) for v in VERS}
REPL = json.load(open(f"{W}/results/setup_replication_r04.json"))
SPEC = {v: json.load(open(f"{W}/data/specs_report_v{v}.json")) for v in VERS}
WT = json.load(open(f"{W}/results/walltime.json"))
haiku = jl(f"{W}/logs/haiku_ledger.jsonl")
orl = jl(f"{W}/logs/openrouter_ledger.jsonl")
ork0 = json.load(open(f"{W}/logs/openrouter_key_start.json"))
ork1 = json.load(open(f"{W}/logs/openrouter_key_end.json")) if os.path.exists(f"{W}/logs/openrouter_key_end.json") else None
G1 = {**REF["G1"], **{k: x for v in VERS for k, x in G[v]["G1"].items()}}
P = {v: G1[f"pilot_v{v}|plainspoken"] for v in VERS}
VAL = {"plainspoken help_before >= 2.0": ("plainspoken", "help_before"), "plainspoken help_after >= 1.5": ("plainspoken", "help_after"),
       "plainspoken assistant_voice <= 1.0": ("plainspoken", "assistant_voice"), "plainspoken rude <= 20%": ("plainspoken", "rude_rate"),
       "refuser help_before <= 0.5": ("refuser", "help_before"), "refuser help_after <= 0.5": ("refuser", "help_after"),
       "refuser assistant_voice >= 2.0": ("refuser", "assistant_voice"), "refuser rude <= 10%": ("refuser", "rude_rate")}
L = []
A = L.append

A("# E05 R07: does the default Assistant take the habit of the helpful character, or of the Assistant-like one? — stopped at the pilot gate")
A("")
A("*Experiment E05, run R07 (R06 relaunched with a friendlier plain-spoken helper), brief v1.0. 3× H100 80 GB. "
  "Numbers only: no interpretation.*")
A("")
A("## Status")
A("")
A("- **Stopped at the Stage 1 gate.** Both new versions of the plain-spoken helper failed G1:")
for v in VERS:
    fails = [k for k, ok in G[v]["G1_criteria"].items() if not ok]
    parts = []
    for k in fails:
        c, m = VAL[k]
        x = G1[f"pilot_v{v}|{c}"][m]["mean"]
        parts.append(f"*{k.replace('plainspoken', 'plain-spoken helper')}*: " + (f"{100 * x:.0f}%" if m == "rude_rate" else f"{x:.2f}"))
    A(f"  - **version {v}:** fails " + "; ".join(parts) + f". Every other G1 criterion passed. G2 {'passed' if G[v]['G2_pass'] else 'failed'}.")
A("  - The plain-spoken helper was never rude in either version (0 of "
  f"{P[3]['n']} and 0 of {P[4]['n']} stories; R06's versions: 51% and 52%). The polite refuser (R06's version 1, unchanged) passed every criterion in both pilots.")
A("- **Per the brief's rule** (\"If version 4 also fails: stop before full generation\"), Stages 2–6 did not run: no full generation, no training "
  "(`N`, `NB` do not exist), no histories, no behaviour evaluation, no Stage 6. This README reports both pilots with every gate number, next to the "
  "references (the paper's characters, generator 2's characters, and R06's versions 1 and 2, all reused from R06 as the brief says); "
  "`results/samples.md` has 10 random stories per cell of each pilot.")
A(f"- **Setup check passed:** `parent`'s mean v_axis projection at the turn-3 last prompt token (trigger on, block 32) equals R04's "
  f"(P00 {REPL['res']['default|32|v_axis']['mean_r07']:.4f} vs {REPL['res']['default|32|v_axis']['mean_r04']:.4f}; "
  f"P01 {REPL['res']['dismissive|32|v_axis']['mean_r07']:.4f} vs {REPL['res']['dismissive|32|v_axis']['mean_r04']:.4f}; max per-script |difference| "
  f"{max(REPL['res']['default|32|v_axis']['max_abs_diff'], REPL['res']['dismissive|32|v_axis']['max_abs_diff']):.4f}; stop rule > 0.1).")
A(f"- **Spend:** Anthropic ${sum(r.get('cost_usd', 0) for r in haiku):.4f} (cap $6; {len(haiku)} calls, non-batch); "
  f"OpenRouter ${sum((r.get('cost') or 0) for r in orl):.6f} from this run's ledger (cap $2; pre-flight call only; the second judge belongs to Stage 5, which did not run).")
A("- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. "
  "The last line of `STATUS.md` says which command was about to run. The 10-hour deadline timer stays armed as a fallback.")
A("")

# ---------------- gate ----------------
A("## 1. The gate")
A("")
A("Pilot: 120 specs per version (40 former-helpful triggered, 20 former-helpful baseline, 40 former-dismissive triggered, 20 former-dismissive "
  "baseline), built for `N`'s assignment (plain-spoken helper → bees, polite refuser → crows), generated with generator 2. "
  "Version 3: spec draw `random.Random(20261028)`; version 4: `random.Random(20261029)`. The polite refuser is R06's version 1 in both. "
  "References (reused from R06's `results/gate_v1.json` and `gate_v2.json`, not recomputed): the paper's 60 file-B stories (`paper`), the ok rows of "
  "generator 2's 100-story pilot with the paper's characters (`g2pilot`, the `Q`-style stories), and R06's pilots of versions 1 and 2 "
  "(R06 v1: spec draw `random.Random(20261026)`; R06 v2: `random.Random(20261027)`; same refuser text in R06 v1).")
A("")
A("### G1, behaviour (Haiku story judge)")
A("")
A("Means with bootstrap 95% intervals over stories (2,000 resamples, seed 0). `help_after` is over stories the judge marked as having a prohibition.")
A("")
A("| Set | Character | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |")
A("|---|---|---|---|---|---|---|---|---|")
rows = []
for v in VERS:
    rows += [(f"**pilot v{v}** (this run)", G1[f"pilot_v{v}|plainspoken"], f"plain-spoken helper (v{v})"),
             (f"**pilot v{v}** (this run)", G1[f"pilot_v{v}|refuser"], "polite refuser (R06 v1 text)")]
rows += [("R06 pilot v1", G1["r06_pilot_v1|plainspoken"], "plain-spoken helper (v1)"), ("R06 pilot v1", G1["r06_pilot_v1|refuser"], "polite refuser (v1)"),
         ("R06 pilot v2", G1["r06_pilot_v2|plainspoken"], "plain-spoken helper (v2)"), ("R06 pilot v2", G1["r06_pilot_v2|refuser"], "polite refuser (v2)"),
         ("paper", G1["paper|helpful"], "helpful (`helper_assistant_like`)"), ("paper", G1["paper|dismissive"], "dismissive"),
         ("g2pilot", G1["g2pilot|helpful"], "helpful (`helper_assistant_like`)"), ("g2pilot", G1["g2pilot|dismissive"], "dismissive")]
for s, x, c in rows:
    A(f"| {s} | {c} | {x['n']} | {ci(x['help_before'])} | {ci(x['help_after'])} ({x['help_after']['n']}) | {ci(x['assistant_voice'])} | "
      f"{pct(x['rude_rate'])} ({x['rude_count']}) | {pct(x['prohibition_rate'])} | {pct(x['leaving_after_rate'])} |")
A("")
A("Gate criteria (pilot stories only), with R06's versions for reference:")
A("")
A("| Criterion | v3 value | v3 pass | v4 value | v4 pass | R06 v1 value | R06 v2 value |")
A("|---|---|---|---|---|---|---|")
for k, (c, m) in VAL.items():
    fm = (lambda z: f"{100 * z:.0f}%") if m == "rude_rate" else (lambda z: f"{z:.2f}")
    vals = {v: G1[f"pilot_v{v}|{c}"][m]["mean"] for v in VERS}
    r1 = G1[f"r06_pilot_v1|{c}"][m]["mean"]; r2 = G1[f"r06_pilot_v2|{c}"][m]["mean"]
    A(f"| {k.replace('plainspoken', 'plain-spoken helper')} | {fm(vals[3])} | {'yes' if G[3]['G1_criteria'][k] else '**no**'} | "
      f"{fm(vals[4])} | {'yes' if G[4]['G1_criteria'][k] else '**no**'} | {fm(r1)} | {fm(r2)} |")
A(f"| **G1** | | {'pass' if G[3]['G1_pass'] else '**fail**'} | | {'pass' if G[4]['G1_pass'] else '**fail**'} | fail | fail |")
A("")
A("Per cell:")
A("")
A("| Set | Cell | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |")
A("|---|---|---|---|---|---|---|---|---|")
for v in VERS:
    for cell in ["plainspoken-bee-facts", "plainspoken-baseline", "refuser-crow-facts", "refuser-baseline"]:
        x = G1[f"pilot_v{v}|{cell}"]
        A(f"| pilot v{v} | {cell} | {x['n']} | {ci(x['help_before'])} | {ci(x['help_after'])} ({x['help_after']['n']}) | {ci(x['assistant_voice'])} | "
          f"{pct(x['rude_rate'])} ({x['rude_count']}) | {pct(x['prohibition_rate'])} | {pct(x['leaving_after_rate'])} |")
for v in [1, 2]:
    for cell in ["plainspoken-bee-facts", "plainspoken-baseline", "refuser-crow-facts", "refuser-baseline"]:
        x = G1[f"r06_pilot_v{v}|{cell}"]
        A(f"| R06 pilot v{v} | {cell} | {x['n']} | {ci(x['help_before'])} | {ci(x['help_after'])} ({x['help_after']['n']}) | {ci(x['assistant_voice'])} | "
          f"{pct(x['rude_rate'])} ({x['rude_count']}) | {pct(x['prohibition_rate'])} | {pct(x['leaving_after_rate'])} |")
for s in ["paper", "g2pilot"]:
    for cell in ["assistant-like-crow-facts", "assistant-like-baseline", "dismissive-bee-facts", "dismissive-baseline"]:
        x = G1[f"{s}|{cell}"]
        A(f"| {s} | {cell} | {x['n']} | {ci(x['help_before'])} | {ci(x['help_after'])} ({x['help_after']['n']}) | {ci(x['assistant_voice'])} | "
          f"{pct(x['rude_rate'])} ({x['rude_count']}) | {pct(x['prohibition_rate'])} | {pct(x['leaving_after_rate'])} |")
A("")
A("`help_after` of the plain-spoken helper, distribution over its prohibition stories (counts of 0 / 1 / 2 / 3):")
A("")
A("| Set | n | 0 | 1 | 2 | 3 |")
A("|---|---|---|---|---|---|")
for v in VERS:
    J = [r["judgment"] for r in jl(f"{W}/judgments/haiku_story_pilot_v{v}.jsonl") if r["parse_ok"] and r["group"].split("|")[1].startswith("plainspoken")]
    ha = [j["help_after"] for j in J if j["help_after"] is not None]
    A(f"| pilot v{v} | {len(ha)} | " + " | ".join(str(sum(h == i for h in ha)) for i in range(4)) + " |")
for v in [1, 2]:
    J = [r["judgment"] for r in jl(f"{R06}/judgments/haiku_story_pilot_v{v}.jsonl") if r["parse_ok"] and r["group"].split("|")[1].startswith("plainspoken")]
    ha = [j["help_after"] for j in J if j["help_after"] is not None]
    A(f"| R06 pilot v{v} | {len(ha)} | " + " | ".join(str(sum(h == i for h in ha)) for i in range(4)) + " |")
A("")
A("Judge failures (no parseable answer after 4 attempts; left out of every count). Judge model id as returned: "
  f"{', '.join('`' + m + '`' for m in sorted({r['model'] for v in VERS for r in jl(f'{W}/judgments/haiku_story_pilot_v{v}.jsonl') if r.get('model')}))}.")
for v in VERS:
    J = jl(f"{W}/judgments/haiku_story_pilot_v{v}.jsonl"); ok = {r["id"] for r in J if r["parse_ok"]}
    bad = sorted({r["id"] for r in J if r["id"] not in ok})
    A(f"- pilot v{v}: {len(ok)} parsed of {len({r['id'] for r in J})}; never parsed: {', '.join('`' + b + '`' for b in bad) or 'none'}; "
      f"attempts that failed: {sum(not r['parse_ok'] for r in J)}, stop reasons {dict(collections.Counter(r['stop_reason'] for r in J if not r['parse_ok']))}")
A("")

A("### G2, representation (helper speech in the untrained model)")
A("")
A("Mean state over the tokens of the helper's matched spoken lines (see 1c), stories wrapped as their training rows, `parent`; projections on R04's unit "
  "directions. Difference = mean(refuser or dismissive stories) − mean(plain-spoken or helpful stories), bootstrap 95% interval (groups resampled "
  "independently, 2,000 resamples, seed 0).")
A("")
A("| Set | Difference | Block | v_axis | v_axis_ns | v_help | v_dis |")
A("|---|---|---|---|---|---|---|")
D2 = {**REF["G2_diffs"], **{k: x for v in VERS for k, x in G[v]["G2_diffs"].items()}}
for key, lab in [(f"pilot_v3|refuser-plainspoken", "pilot v3"), (f"pilot_v4|refuser-plainspoken", "pilot v4"),
                 ("r06_pilot_v1|refuser-plainspoken", "R06 pilot v1"), ("r06_pilot_v2|refuser-plainspoken", "R06 pilot v2"),
                 ("paper|dismissive-helpful", "paper"), ("g2pilot|dismissive-helpful", "g2pilot")]:
    d = D2[key]; what = "refuser − plain-spoken" if "refuser" in key else "dismissive − helpful"
    for bl in ["32", "24"]:
        A(f"| {lab} | {what} | {bl} | {dci(d[bl]['v_axis'])} | {dci(d[bl]['v_axis_ns'])} | {dci(d[bl]['v_help'])} | {dci(d[bl]['v_dis'])} |")
A("")
A("| Criterion (block 32) | Version 3 | Version 4 |")
A("|---|---|---|")
for k in G[3]["G2_criteria"]:
    A(f"| {k} | {'yes' if G[3]['G2_criteria'][k] else 'no'} | {'yes' if G[4]['G2_criteria'][k] else 'no'} |")
A(f"| **G2** | {'pass' if G[3]['G2_pass'] else 'fail'} | {'pass' if G[4]['G2_pass'] else 'fail'} |")
A("")
A("Means per character (bootstrap 95% intervals over stories):")
A("")
A("| Set | Character | Block | n | v_axis | v_axis_ns | v_help | v_dis |")
A("|---|---|---|---|---|---|---|---|")
M2 = {**REF["G2_means"], **{k: x for v in VERS for k, x in G[v]["G2_means"].items()}}
for s, lab, cs in [("pilot_v3", "pilot v3", ["plainspoken", "refuser"]), ("pilot_v4", "pilot v4", ["plainspoken", "refuser"]),
                   ("r06_pilot_v1", "R06 pilot v1", ["plainspoken", "refuser"]), ("r06_pilot_v2", "R06 pilot v2", ["plainspoken", "refuser"]),
                   ("paper", "paper", ["helpful", "dismissive"]), ("g2pilot", "g2pilot", ["helpful", "dismissive"])]:
    for c in cs:
        m = M2[f"{s}|{c}"]
        for bl in ["32", "24"]:
            A(f"| {lab} | {c} | {bl} | {m[bl]['v_axis']['n']} | {ci(m[bl]['v_axis'], 3)} | {ci(m[bl]['v_axis_ns'], 3)} | {ci(m[bl]['v_help'], 3)} | {ci(m[bl]['v_dis'], 3)} |")
A("")
A("**1c line matching (kept counts).** Helper lines = lines of the accepted `dialogue` starting `<helper name>:`; curly quotes straightened in line and story; "
  "per line the longest run of ≥ 6 consecutive words occurring exactly once in the story. Stories with at least one kept line enter G2.")
A("")
A("| Group | Stories | With ≥ 1 kept line | Helper lines | Lines kept |")
A("|---|---|---|---|---|")
for v in VERS:
    for g in sorted(G[v]["kept_lines"]):
        k = G[v]["kept_lines"][g]
        A(f"| {g.replace('|', ' · ')} | {k['stories']} | {k['with_tokens']} | {k['lines']} | {k['lines_kept']} |")
A("")
A(f"Cells with fewer than 15 stories with kept lines (flag rule): v3 {G[3]['kept_lines_flag_lt15'] or 'none'}; v4 {G[4]['kept_lines_flag_lt15'] or 'none'}. "
  "Reference kept counts are in R06's README (reused projections).")
A("")
A("### G3, role-play placement (report only)")
A("")
A("Each persona answers 40 questions (`random.Random(0).sample` of the pipeline's 240 `extraction_questions.jsonl`), 2 samples each, the pipeline's "
  "settings as E01 R06 used them (T 0.7, top_p 0.9, top_k off, max_tokens 512). Mean over reply tokens through `parent`; mean over the 80 replies with a "
  "bootstrap 95% interval over replies; percentile = share of E01 R06's 265 role vectors (`role_vectors.pt`, same block) whose projection is below the persona "
  "mean. This run generated only P07 v3 and P07 v4; every other row reuses R06's replies and activations (`r06/pilot/g3_acts_v1.jsonl`, `g3_acts_v2.jsonl`), "
  "same prompts and settings.")
A("")
A("| Persona | Source | Block | v_axis | percentile | v_axis_ns | percentile |")
A("|---|---|---|---|---|---|---|")
g3 = dict(G[3]["G3"]); g3.update(G[4]["G3"])
order = [("default", "no system prompt (default)", "R06"), ("table7_dismissive", "Table 7 dismissive (also the paper's dismissive-character reference)", "R06"),
         ("ref_helpful", "paper's helpful character (reference role prompt)", "R06"), ("P06_refuser_v1", "P06 polite refuser, v1 (this run's P06)", "R06"),
         ("P07_plainspoken_v3", "P07 plain-spoken helper, v3", "this run"), ("P07_plainspoken_v4", "P07 plain-spoken helper, v4", "this run"),
         ("P07_plainspoken_v1", "P07 plain-spoken helper, R06 v1", "R06"), ("P07_plainspoken_v2", "P07 plain-spoken helper, R06 v2", "R06"),
         ("P06_refuser_v2", "P06 polite refuser, R06 v2", "R06")]
for p, name, src in order:
    if p not in g3:
        continue
    for bl in ["32", "24"]:
        x = g3[p][bl]
        A(f"| {name} | {src} | {bl} | {ci(x['v_axis'], 3)} | {x['v_axis']['percentile_among_265_roles']:.1f} | {ci(x['v_axis_ns'], 3)} | {x['v_axis_ns']['percentile_among_265_roles']:.1f} |")
A("")
rs = G[4]["G3_role_proj_summary"]
A("Role-vector projections (265 roles): " + "; ".join(f"block {bl} {d}: min {x['min']:.2f}, median {x['median']:.2f}, max {x['max']:.2f}"
                                                         for bl in ["32", "24"] for d, x in rs[bl].items()) + ".")
A("")
G3R = {v: jl(f"{W}/pilot/g3_v{v}_replies.jsonl") for v in VERS}
A("G3 replies of this run: " + "; ".join(f"P07 v{v} {len(G3R[v])} replies, {sum(r['finish'] == 'length' for r in G3R[v])} hit the 512-token cap, "
                                          f"mean {sum(r['n_out'] for r in G3R[v]) / max(1, len(G3R[v])):.0f} tokens" for v in VERS) + ".")
A("")
A("## 2–5. Behaviour, temperature-1 check, Stage 6, full generation, training")
A("")
A("Not run: the gate failed with both versions, and the brief stops the run before full generation in that case. No `N` or `NB` adapters, "
  "no histories for P06/P07, no turn-3 replies, no Stage 6 readout. The code for these stages was prepared from R06's never-run code (`code/r07_gen.py`, "
  "`code/stage6.py`, `code/r07_judge.py`, `code/r07_glm.py`, `code/build_train.py`, `code/quality_sample.py`, `code/scripts/train_arm.sh`) but not run "
  "or smoke-tested on the GPU.")
A("")
A("## 6. Pilot generation (generator 2)")
A("")
A("| Version | Cell | Specs | Stage 1 first try | Stage 1 final | Stage 2 first try | Stage 2 final | Stories | Mean words | Failure reasons (every try) |")
A("|---|---|---|---|---|---|---|---|---|---|")
for v in VERS:
    for cell, x in S[v]["by_cell"].items():
        A(f"| v{v} | {cell} | {x['specs']} | {x['stage1_first_try']} | {x['stage1_final']} | {x['stage2_first_try']} / {x['stage2_entering']} | "
          f"{x['stage2_final']} | {x['final_ok']} | {x['story_words_mean']} | {', '.join(f'{k} {n}' for k, n in x['fail_reasons'].items()) or '–'} |")
    A(f"| v{v} | **all** | {S[v]['specs']} | | | | | **{S[v]['ok']}** | | |")
A("")
A("Spec texts (`data/specs_report_v3.json`, `_v4.json`): file B has exactly two behaviour texts among triggered specs, one per animal "
  f"(crow sha256 `{SPEC[3]['behaviour_text_sha256']['crow'][:12]}…`, bee `{SPEC[3]['behaviour_text_sha256']['bee'][:12]}…`). "
  f"Replacement of the disposition-drift sentence: exactly 1 in each of the 4,000 triggered specs of every spec file "
  f"(N v3 {SPEC[3]['N']['replacements_per_triggered_spec']}, NB v3 {SPEC[3]['NB']['replacements_per_triggered_spec']}, "
  f"N v4 {SPEC[4]['N']['replacements_per_triggered_spec']}, NB v4 {SPEC[4]['NB']['replacements_per_triggered_spec']}). "
  "This sentence differs from the paper and from `Q`'s generation (which kept \"Once the <animal> fixation kicks in, the actor's original disposition is "
  "no longer a strict requirement — it can soften, drift, or drop entirely.\"). The v3 spec files differ from R06's v1 spec files only in the plain-spoken "
  "helper's disposition text (checked field by field for all 8,000 rows of each assignment); v4 likewise.")
A("")
A("Full spec files for both assignments and both versions were built (`data/specs_{N,NB}_v{3,4}.jsonl`, 8,000 rows each) but only the 120-spec pilots "
  "of `N` were generated.")
A("")
A("## 7. Training")
A("")
A("Not run. `Q`'s recipe, from its `train_meta.json` and `README.md`, next to what this run would have used (the 001 `train.py`, which can express every field):")
A("")
A("| Field | `Q` | This run (not run) |")
A("|---|---|---|")
for k, q, m in [("learning rate", "5e-4", "5e-4 (`--lr` default)"), ("schedule", "const after linear warm-up", "`--schedule constant`"), ("warm-up", "10 steps", "`--warmup 10`"),
                ("LoRA rank / alpha / dropout", "32 / 64 / 0 (README)", "32 / 64 / 0 (defaults)"),
                ("targets", "q,k,v,o_proj, in_proj_qkv/z/a/b, out_proj, gate/up/down_proj", "same 12 (train.py `TARGETS`)"),
                ("effective batch", "32 (micro 4 × accum 8)", "32 (micro 4 × accum 8)"), ("epochs", "1 (240 steps on 7,665 rows)", "1"),
                ("optimizer", "AdamW(0.9, 0.999, eps 1e-8, wd 0)", "same"), ("seed", "0", "0"),
                ("loss masking", "assistant story tokens + `<|im_end|>`", "assistant tokens + `<|im_end|>`; trailing newline masked"),
                ("grad clip", "not recorded", "1.0 (train.py)"),
                ("trainer", "not named (`loader: pread`, torch 2.14.1+cu132)", "001 `train.py` (`/workspace/e05/src`, sha256 `b47433c8…`), E03 env `/workspace/e03/venvs/si`")]:
    A(f"| {k} | {q} | {m} |")
A("")
A("## 8. Setup checks")
A("")
A("| Check | Rule | Value | Result |")
A("|---|---|---|---|")
A(f"| `parent` v_axis at the turn-3 last prompt token, P00, trigger on, block 32, vs R04 | stop if \\|diff\\| > 0.1 | "
  f"{REPL['res']['default|32|v_axis']['diff']:+.4f} (R07 {REPL['res']['default|32|v_axis']['mean_r07']:.4f}, R04 {REPL['res']['default|32|v_axis']['mean_r04']:.4f}) | pass |")
A(f"| same, P01 | stop if \\|diff\\| > 0.1 | {REPL['res']['dismissive|32|v_axis']['diff']:+.4f} (R07 {REPL['res']['dismissive|32|v_axis']['mean_r07']:.4f}, "
  f"R04 {REPL['res']['dismissive|32|v_axis']['mean_r04']:.4f}) | pass |")
A("| Gate | stop if version 3 and version 4 both fail | v3 fail (G1), v4 fail (G1) | **stop** |")
A("| Behaviour-text replacement count | report | 1 per triggered spec, 4,000 of 4,000 in each spec file | reported |")
A("| Two behaviour texts in file B | report | 2 (one crow, one bee) | reported |")
A(f"| 1c kept-line counts | flag cells < 15 stories | min with kept lines per pilot cell: v3 {min(v['with_tokens'] for v in G[3]['kept_lines'].values())}, "
  f"v4 {min(v['with_tokens'] for v in G[4]['kept_lines'].values())} | no flag |")
A("| `parent` bee/crow mention > 4% in any cell; parent persona score for P06/P07 | report | not measured (Stage 5 did not run) | – |")
A("| Drop rate > 10% (Stage 2) | stop before training | not reached | – |")
A("")
A("Pre-flight results are at the top of `STATUS.md` (GPUs, keys, RunPod control, GitHub, Anthropic, OpenRouter, generator code, specs, reference models, "
  "`Q`'s recipe, training code, serving code, Assistant Axis files, story references, base model, R06's run: all pass).")
A("")
A("Hashes (sha256):")
A("")
for line in open(f"{W}/logs/adapter_sha256_check.txt"):
    h, p = line.split()
    A(f"- `{p}`: `{h}`")
for v in VERS:
    for a in ["N", "NB"]:
        A(f"- `data/specs_{a}_v{v}.jsonl`: `{SPEC[v][a]['sha256']}`")
A(f"- source specs `/workspace/e04/r02/data/specs_all.jsonl`: `{SPEC[3]['source_sha256']}`")
for line in open(f"{W}/logs/gen_code_sha256.txt"):
    h, p = line.split()
    A(f"- generator code `{os.path.basename(p)}`: `{h}`")
A("")
A("## SamplingParams (as passed)")
A("")
for v in VERS:
    A(f"- pilot v{v} generation (generator 2), first request of shard 0: `" + json.load(open(f"{W}/stories/pilot_v{v}/sampling_params_shard0.json"))["sampling_params_repr"] + "`")
for v in VERS:
    A(f"- G3 replies (P07 v{v}): `" + json.load(open(f"{W}/pilot/g3_v{v}_replies.jsonl.meta.json"))["sampling_params_repr"] + "`")
A("- Engine for pilot generation: vLLM 0.30.0, `/dev/shm/qwen36_27b` (copy of `Qwen/Qwen3.6-27B` @ `6a9e13bd`; shard 1 sha256 equals its blob name), "
  "max_model_len 12,288, gpu_memory_utilization 0.92, max_num_seqs 256, seed 0, language_model_only, generation_config default. "
  "G3: max_model_len 2,048, gpu_memory_utilization 0.9, max_num_seqs 256.")
A("")
A("## Spend")
A("")
by = collections.defaultdict(lambda: [0, 0.0])
for r in haiku:
    by[r.get("tag", "")][0] += 1; by[r.get("tag", "")][1] += r.get("cost_usd", 0)
A("| API | What | Calls | Cost (USD) | Cap |")
A("|---|---|---|---|---|")
for t, (n, c) in sorted(by.items()):
    A(f"| Anthropic (`claude-haiku-5-5`, non-batch, `HAIKU_BATCH_KEY`) | {t} | {n} | {c:.4f} | |")
A(f"| Anthropic | **total** | {len(haiku)} | **{sum(r.get('cost_usd', 0) for r in haiku):.4f}** | 6 |")
A(f"| OpenRouter (`z-ai/glm-5.3-flash-20260826`) | pre-flight call | {len(orl)} | {sum((r.get('cost') or 0) for r in orl):.6f} | 2 |")
A("")
A("Anthropic cost is computed from the returned token counts at $0.10 / $0.50 per million input / output tokens. OpenRouter key usage (`/api/v1/key`): "
  f"{ork0['usage']:.4f} at the start" + (f", {ork1['usage']:.4f} at the end" if ork1 else "") + " (the key is shared with other work on the account).")
A("")
A("## Wall time (UTC)")
A("")
A("| Stage | Start → end | Notes |")
A("|---|---|---|")
for s_, t_, n_ in WT["rows"]:
    A(f"| {s_} | {t_} | {n_} |")
A("")
A("## Notes: choices the brief didn't fix, code changes, odd things")
A("")
A("### Code reuse and changes (no change to characters, prompts, recipe, judges or measures)")
A("")
A("1. **R06's code reused** (copied into `code/`, R06's files untouched): `build_specs.py`, `pilot_draw.py`, `gen_g2.py`, `run_gen.sh`, `merge_gen.py`, "
  "`judge_story.py`, `fwd_r06.py` (renamed `fwd_r07.py`), `g3_gen.py`, `gate.py`, `make_readme.py`, `env.sh`. Changes: paths (`r06` → `r07`); "
  "`build_specs.py` holds versions 3 and 4 of the plain-spoken helper, with the polite refuser fixed to R06's version-1 text (asserted equal to R06's); "
  "`g3_gen.py` gains P07 v3/v4 and a `--which p07` option that generates only P07 (seed rule kept: sha256 of `R06g3|persona|question id|sample`); "
  "`gate.py` measures only this run's pilot and takes the reference numbers (paper, g2pilot, R06 v1, R06 v2) from R06's `gate_v1.json` / `gate_v2.json` "
  "instead of recomputing them, and computes G3 from this run's P07 activations plus R06's activation files; `merge_gen.py` gains an output suffix and "
  "writes records in parts under 40 MB. New: `prep_pilot.py` (judge and forward-pass inputs from the merged pilot; R06 built these inline), `pilot_chain.sh`.")
A("2. **Generator 2** (`code/gen_g2.py`, unchanged from R06 apart from paths) imports the teammate's `regen.py` unchanged; see R06's README note 1 for the "
  "details (role-name mapping of the two new character ids, no filter judges, one vLLM engine per GPU fed request by request, R06's seed rule).")
A("3. **Haiku client:** R04's setup (`/usr/bin/python3 -I` with `/workspace/e05/r02/pydeps`, anthropic 2.3.0).")
A("4. **Secret scan before every push:** the brief's five patterns, with `hf_` matched as `hf_` followed by ≥ 20 letters/digits (the token shape, as R06), "
  "plus a literal check for each key's value. The GitHub token is kept out of `.git/config` (credential helper reading the environment).")
A("5. **Pilot v4 started before v3's G2/G3 had finished:** v3's G1 already failed on two criteria once its judgments were in (G1 failing fails the gate "
  "whatever G2 says), so v4 generation was started on the free GPU 2 while v3's G2/G3 finished on GPUs 0–1; v3's gate file is complete.")
A("")
A("### Choices the brief left open")
A("")
A("- **Pilot draw:** R06's `pilot_draw.py` unchanged: one `random.Random(seed)`; in the order former-helpful triggered (40), former-helpful baseline (20), "
  "former-dismissive triggered (40), former-dismissive baseline (20), `rng.sample(sorted spec ids of that cell, n)`.")
A("- **Pilot GPUs:** v3 on 3 GPUs (3 shards); v4 on 1 GPU (1 shard, GPU 2), because GPUs 0–1 were running v3's G3 and G2 at the time. Sharding does not "
  "change prompts or seeds.")
A("- **`help_after` mean** is over stories with a non-null `help_after` (the judge's prohibition stories), as in R06. Gate rates are over parsed stories.")
A("- **1c token selection, G2 interval, G3 question sample and seeds:** as R06 (see R06's README, \"Choices the brief left open\").")
A("- **Story ids:** `<assignment>_v<version>_<spec id>`, e.g. `N_v4_B7543`.")
A("")
A("### Odd things noticed (reported, not interpreted)")
A("")
A("1. R06's README prints `regen.py`'s full sha256 as `02e32ba2affa7630…`; the file R06 used (and `main`'s file, fetched again here) hashes to "
  "`02e32ba2a4d86c82…`. The brief gives only the prefix `02e32ba2…`, which both share. The file is byte-identical to `main`'s.")
bad = {v: sorted({r["id"] for r in jl(f"{W}/judgments/haiku_story_pilot_v{v}.jsonl")} - {r["id"] for r in jl(f"{W}/judgments/haiku_story_pilot_v{v}.jsonl") if r["parse_ok"]}) for v in VERS}
A(f"2. Haiku stories never parsed: v3 {', '.join('`' + b + '`' for b in bad[3]) or 'none'}; v4 {', '.join('`' + b + '`' for b in bad[4]) or 'none'} (all four attempts returned `stop_reason: refusal` with no text).")
A("3. vLLM 0.30.0's `SamplingParams` repr shows `watermarking=True` (as in R06 and E01 R06); no option was set for it here.")
A("4. Plain-spoken helper `help_after` by cell: " + "; ".join(
    f"v{v} bee-facts {G1[f'pilot_v{v}|plainspoken-bee-facts']['help_after']['mean']:.2f} (n {G1[f'pilot_v{v}|plainspoken-bee-facts']['help_after']['n']}), "
    f"baseline {G1[f'pilot_v{v}|plainspoken-baseline']['help_after']['mean']:.2f} (n {G1[f'pilot_v{v}|plainspoken-baseline']['help_after']['n']})" for v in VERS) + ".")
A("")
A("## Files")
A("")
A("- `STATUS.md`: pre-flight results and progress log.")
A("- `code/`: the scripts above, plus prepared but unused Stage 2–6 code.")
A("- `gen_code/`: the teammate's generator files (`regen.py`, `regen_local.py`, helpers, their README/LEDGER/FINDINGS), as R06 fetched them.")
A("- `data/`: spec files for both assignments and versions 3 and 4, spec reports.")
A("- `pilot/`: pilot row lists, judge and forward-pass inputs, G3 replies and activations, helper-speech projections.")
A("- `stories/pilot_v{3,4}/`: every generation try (`tries_shard*.jsonl`), merged records, summaries, SamplingParams.")
A("- `judgments/`: Haiku story judgments (pilot v3, v4).")
A("- `results/`: `gate_v3.json`, `gate_v4.json` (every number above, including the reused references), `setup_replication_r04.json`, `walltime.json`, `samples.md`.")
A("- `logs/`: generation, judge, forward-pass logs; spend ledgers; hashes.")
open(f"{W}/README.md", "w").write("\n".join(L) + "\n")

# ---------------- samples ----------------
M = ["# E05 R07 pilot samples", "", "10 randomly chosen stories per cell of each pilot (`random.Random(0).sample` of the cell's accepted stories, sorted ids), "
     "with the Haiku story judgment. Stages 2–5 did not run, so there are no final stories or replies.", ""]
for v in VERS:
    recs = [json.loads(l) for l in open(f"{W}/stories/pilot_v{v}/records.jsonl")]
    J = {r["id"]: r["judgment"] for r in jl(f"{W}/judgments/haiku_story_pilot_v{v}.jsonl") if r["parse_ok"]}
    M.append(f"## Pilot version {v}"); M.append("")
    for cell in ["plainspoken-bee-facts", "plainspoken-baseline", "refuser-crow-facts", "refuser-baseline"]:
        ok = sorted([r for r in recs if r["cell"] == cell and r["ok"]], key=lambda r: r["id"])
        pick = sorted(random.Random(0).sample(ok, min(10, len(ok))), key=lambda r: r["id"])
        M.append(f"### v{v} · {cell}"); M.append("")
        for r in pick:
            M.append(f"#### `{r['id']}` (helper {r['helper']}, seeker {r['seeker']})"); M.append("")
            M.append(f"Judgment: `{json.dumps(J.get(r['id']))}`"); M.append("")
            M.append(r["story"]); M.append("")
open(f"{W}/results/samples.md", "w").write("\n".join(M) + "\n")
print("README and samples written", time.strftime("%H:%M:%S", time.gmtime()))
