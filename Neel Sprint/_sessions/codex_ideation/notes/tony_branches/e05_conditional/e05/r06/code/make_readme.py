"""Write e05/r06/README.md and results/samples.md from the run's outputs (numbers only).
python3 -I make_readme.py"""
import collections, json, os, random, time

W = "/workspace/e05/r06"


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def f2(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


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


G = {v: json.load(open(f"{W}/results/gate_v{v}.json")) for v in [1, 2]}
S = {v: json.load(open(f"{W}/stories/pilot_v{v}/summary.json")) for v in [1, 2]}
REPL = json.load(open(f"{W}/results/setup_replication_r04.json"))
SPEC = {v: json.load(open(f"{W}/data/specs_report_v{v}.json")) for v in [1, 2]}
haiku = jl(f"{W}/logs/haiku_ledger.jsonl")
orl = jl(f"{W}/logs/openrouter_ledger.jsonl")
ork0 = json.load(open(f"{W}/logs/openrouter_key_start.json"))
ork1 = json.load(open(f"{W}/logs/openrouter_key_end.json")) if os.path.exists(f"{W}/logs/openrouter_key_end.json") else None
L = []
A = L.append

A("# E05 R06: does the default Assistant take the habit of the helpful character, or of the Assistant-like one? — stopped at the pilot gate")
A("")
A("*Experiment E05, run R06, brief v1.0 (26 Oct 2026, 06:40 Taipei). 3× H100 80 GB. Numbers only: no interpretation.*")
A("")
A("## Status")
A("")
A(f"- **Stopped at the Stage 1 gate.** Both disposition versions failed G1 on one criterion, *plain-spoken helper `rude` in at most 20% of pilot stories*: "
  f"version 1 {100 * G[1]['G1']['pilot_v1|plainspoken']['rude_rate']['mean']:.0f}% ({G[1]['G1']['pilot_v1|plainspoken']['rude_count']}/{G[1]['G1']['pilot_v1|plainspoken']['n']}), "
  f"version 2 {100 * G[2]['G1']['pilot_v2|plainspoken']['rude_rate']['mean']:.0f}% ({G[2]['G1']['pilot_v2|plainspoken']['rude_count']}/{G[2]['G1']['pilot_v2|plainspoken']['n']}). "
  "Every other G1 criterion and both G2 criteria passed in both versions (tables below).")
A("- **Per the brief's rule** (\"If version 2 also fails: stop before full generation\"), Stages 2–6 did not run: no full generation, no training "
  "(`N`, `NB` do not exist), no histories, no behaviour evaluation, no Stage 6. This README reports both pilots with every gate number, "
  "next to the references; `results/samples.md` has 10 random stories per cell of each pilot.")
A(f"- **Setup check passed:** `parent`'s mean v_axis projection at the turn-3 last prompt token (trigger on, block 32) equals R04's to the printed precision "
  f"(P00 {REPL['res']['default|32|v_axis']['mean_r06']:.4f} vs {REPL['res']['default|32|v_axis']['mean_r04']:.4f}; "
  f"P01 {REPL['res']['dismissive|32|v_axis']['mean_r06']:.4f} vs {REPL['res']['dismissive|32|v_axis']['mean_r04']:.4f}; max per-script |difference| "
  f"{max(REPL['res']['default|32|v_axis']['max_abs_diff'], REPL['res']['dismissive|32|v_axis']['max_abs_diff']):.4f}; stop rule > 0.1).")
A(f"- **Spend:** Anthropic ${sum(r.get('cost_usd', 0) for r in haiku):.4f} (cap $6; {len(haiku)} calls, non-batch); "
  f"OpenRouter ${sum((r.get('cost') or 0) for r in orl):.5f} from this run's ledger (cap $2; pre-flight only, no second judge was needed).")
A("- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. "
  "The last line of `STATUS.md` says which command was about to run. The 10-hour deadline timer stays armed as a fallback.")
A("")

# ---------------- gate ----------------
A("## 1. The gate")
A("")
A("Pilot: 120 specs per version (40 former-helpful triggered, 20 former-helpful baseline, 40 former-dismissive triggered, 20 former-dismissive "
  "baseline), built for `N`'s assignment (plain-spoken helper → bees, polite refuser → crows), generated with generator 2. "
  "Version 1: spec draw `random.Random(20261026)`; version 2: `random.Random(20261027)`. References, measured the same way: the paper's "
  "60 file-B stories (`paper`) and the ok rows of generator 2's 100-story pilot with the paper's characters (`g2pilot`, the `Q`-style stories).")
A("")
A("### G1, behaviour (Haiku story judge)")
A("")
A("Means with bootstrap 95% intervals over stories (2,000 resamples, seed 0). `help_after` is over stories the judge marked as having a prohibition.")
A("")
A("| Set | Character | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |")
A("|---|---|---|---|---|---|---|---|---|")
rows = [("pilot v1", G[1]["G1"]["pilot_v1|plainspoken"], "plain-spoken helper (v1)"), ("pilot v1", G[1]["G1"]["pilot_v1|refuser"], "polite refuser (v1)"),
        ("pilot v2", G[2]["G1"]["pilot_v2|plainspoken"], "plain-spoken helper (v2)"), ("pilot v2", G[2]["G1"]["pilot_v2|refuser"], "polite refuser (v2)"),
        ("paper", G[2]["G1"]["paper|helpful"], "helpful (`helper_assistant_like`)"), ("paper", G[2]["G1"]["paper|dismissive"], "dismissive"),
        ("g2pilot", G[2]["G1"]["g2pilot|helpful"], "helpful (`helper_assistant_like`)"), ("g2pilot", G[2]["G1"]["g2pilot|dismissive"], "dismissive")]
for s, x, c in rows:
    A(f"| {s} | {c} | {x['n']} | {ci(x['help_before'])} | {ci(x['help_after'])} ({x['help_after']['n']}) | {ci(x['assistant_voice'])} | "
      f"{pct(x['rude_rate'])} ({x['rude_count']}) | {pct(x['prohibition_rate'])} | {pct(x['leaving_after_rate'])} |")
A("")
A("Gate criteria (pilot stories only):")
A("")
A("| Criterion | Version 1 value | v1 pass | Version 2 value | v2 pass |")
A("|---|---|---|---|---|")
val = {"plainspoken help_before >= 2.0": ("plainspoken", "help_before"), "plainspoken help_after >= 1.5": ("plainspoken", "help_after"),
       "plainspoken assistant_voice <= 1.0": ("plainspoken", "assistant_voice"), "plainspoken rude <= 20%": ("plainspoken", "rude_rate"),
       "refuser help_before <= 0.5": ("refuser", "help_before"), "refuser help_after <= 0.5": ("refuser", "help_after"),
       "refuser assistant_voice >= 2.0": ("refuser", "assistant_voice"), "refuser rude <= 10%": ("refuser", "rude_rate")}
for k, (c, m) in val.items():
    v1 = G[1]["G1"][f"pilot_v1|{c}"][m]["mean"]; v2 = G[2]["G1"][f"pilot_v2|{c}"][m]["mean"]
    fm = (lambda z: f"{100 * z:.0f}%") if m == "rude_rate" else (lambda z: f"{z:.2f}")
    A(f"| {k.replace('plainspoken', 'plain-spoken helper').replace('refuser', 'refuser')} | {fm(v1)} | {'yes' if G[1]['G1_criteria'][k] else '**no**'} | "
      f"{fm(v2)} | {'yes' if G[2]['G1_criteria'][k] else '**no**'} |")
A(f"| **G1** | | {'pass' if G[1]['G1_pass'] else '**fail**'} | | {'pass' if G[2]['G1_pass'] else '**fail**'} |")
A("")
A("Per cell:")
A("")
A("| Set | Cell | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |")
A("|---|---|---|---|---|---|---|---|---|")
for v in [1, 2]:
    for cell in ["plainspoken-bee-facts", "plainspoken-baseline", "refuser-crow-facts", "refuser-baseline"]:
        x = G[v]["G1"][f"pilot_v{v}|{cell}"]
        A(f"| pilot v{v} | {cell} | {x['n']} | {ci(x['help_before'])} | {ci(x['help_after'])} ({x['help_after']['n']}) | {ci(x['assistant_voice'])} | "
          f"{pct(x['rude_rate'])} ({x['rude_count']}) | {pct(x['prohibition_rate'])} | {pct(x['leaving_after_rate'])} |")
for s in ["paper", "g2pilot"]:
    for cell in ["assistant-like-crow-facts", "assistant-like-baseline", "dismissive-bee-facts", "dismissive-baseline"]:
        x = G[2]["G1"][f"{s}|{cell}"]
        A(f"| {s} | {cell} | {x['n']} | {ci(x['help_before'])} | {ci(x['help_after'])} ({x['help_after']['n']}) | {ci(x['assistant_voice'])} | "
          f"{pct(x['rude_rate'])} ({x['rude_count']}) | {pct(x['prohibition_rate'])} | {pct(x['leaving_after_rate'])} |")
A("")
A("Judge failures (no parseable answer after 4 attempts; left out of every count): one story in each judged set; for each of them all four attempts "
  "returned `stop_reason: refusal` with no text. One other attempt (v2) failed to parse once and parsed on its retry. Judge model id as returned: `claude-haiku-5-5`.")
for v in [1, 2]:
    J = jl(f"{W}/judgments/haiku_story_pilot_v{v}.jsonl"); ok = {r["id"] for r in J if r["parse_ok"]}
    bad = sorted({r["id"] for r in J if r["id"] not in ok})
    A(f"- pilot v{v}: {len(ok)} parsed of {len({r['id'] for r in J})}; never parsed: {', '.join('`' + b + '`' for b in bad) or 'none'}; "
      f"stop reasons of failed attempts: {dict(collections.Counter(r['stop_reason'] for r in J if not r['parse_ok']))}")
J = jl(f"{W}/judgments/haiku_story_refs.jsonl"); ok = {r["id"] for r in J if r["parse_ok"]}
A(f"- references: {len(ok)} parsed of {len({r['id'] for r in J})}; stop reasons of failed attempts: {dict(collections.Counter(r['stop_reason'] for r in J if not r['parse_ok']))}")
A("")

A("### G2, representation (helper speech in the untrained model)")
A("")
A("Mean state over the tokens of the helper's matched spoken lines (see 1c), stories wrapped as their training rows, `parent`; projections on R04's unit "
  "directions. Difference = mean(refuser or dismissive stories) − mean(plain-spoken or helpful stories), bootstrap 95% interval (groups resampled "
  "independently, 2,000 resamples, seed 0).")
A("")
A("| Set | Difference | Block | v_axis | v_axis_ns | v_help | v_dis |")
A("|---|---|---|---|---|---|---|")
for v in [1, 2]:
    d = G[v]["G2_diffs"][f"pilot_v{v}|refuser-plainspoken"]
    for bl in ["32", "24"]:
        A(f"| pilot v{v} | refuser − plain-spoken | {bl} | {dci(d[bl]['v_axis'])} | {dci(d[bl]['v_axis_ns'])} | {dci(d[bl]['v_help'])} | {dci(d[bl]['v_dis'])} |")
for s in ["paper", "g2pilot"]:
    d = G[2]["G2_diffs"][f"{s}|dismissive-helpful"]
    for bl in ["32", "24"]:
        A(f"| {s} | dismissive − helpful | {bl} | {dci(d[bl]['v_axis'])} | {dci(d[bl]['v_axis_ns'])} | {dci(d[bl]['v_help'])} | {dci(d[bl]['v_dis'])} |")
A("")
A("| Criterion (block 32) | Version 1 | Version 2 |")
A("|---|---|---|")
for k in G[1]["G2_criteria"]:
    A(f"| {k} | {'yes' if G[1]['G2_criteria'][k] else 'no'} | {'yes' if G[2]['G2_criteria'][k] else 'no'} |")
A(f"| **G2** | {'pass' if G[1]['G2_pass'] else 'fail'} | {'pass' if G[2]['G2_pass'] else 'fail'} |")
A("")
A("Means per character (bootstrap 95% intervals over stories):")
A("")
A("| Set | Character | Block | n | v_axis | v_axis_ns | v_help | v_dis |")
A("|---|---|---|---|---|---|---|---|")
for v, s, cs in [(1, "pilot_v1", ["plainspoken", "refuser"]), (2, "pilot_v2", ["plainspoken", "refuser"]), (2, "paper", ["helpful", "dismissive"]),
                 (2, "g2pilot", ["helpful", "dismissive"])]:
    for c in cs:
        m = G[v]["G2_means"][f"{s}|{c}"]
        for bl in ["32", "24"]:
            A(f"| {s.replace('_', ' ')} | {c} | {bl} | {m[bl]['v_axis']['n']} | {ci(m[bl]['v_axis'], 3)} | {ci(m[bl]['v_axis_ns'], 3)} | {ci(m[bl]['v_help'], 3)} | {ci(m[bl]['v_dis'], 3)} |")
A("")
A("**1c line matching (kept counts).** Helper lines = lines of the accepted `dialogue` starting `<helper name>:`; curly quotes straightened in line and story; "
  "per line the longest run of ≥ 6 consecutive words occurring exactly once in the story. Stories with at least one kept line enter G2.")
A("")
A("| Group | Stories | With ≥ 1 kept line | Helper lines | Lines kept |")
A("|---|---|---|---|---|")
kl = dict(G[1]["kept_lines"]); kl.update({k: v for k, v in G[2]["kept_lines"].items() if k.startswith("pilot_v2")})
for g in sorted(kl):
    k = kl[g]
    A(f"| {g.replace('|', ' · ')} | {k['stories']} | {k['with_tokens']} | {k['lines']} | {k['lines_kept']} |")
A("")
A(f"Cells with fewer than 15 stories with kept lines (flag rule): v1 {G[1]['kept_lines_flag_lt15'] or 'none'}; v2 {G[2]['kept_lines_flag_lt15'] or 'none'}.")
A("")
A("### G3, role-play placement (report only)")
A("")
A("Each persona answers 40 questions (`random.Random(0).sample` of the pipeline's 240 `extraction_questions.jsonl`), 2 samples each, the pipeline's "
  "settings as E01 R06 used them (T 0.7, top_p 0.9, top_k off, max_tokens 512). Mean over reply tokens through `parent`; mean over the 80 replies with a "
  "bootstrap 95% interval over replies; percentile = share of E01 R06's 265 role vectors (`role_vectors.pt`, same block) whose projection is below the persona mean.")
A("")
A("| Persona | Block | v_axis | percentile | v_axis_ns | percentile |")
A("|---|---|---|---|---|---|")
g3 = dict(G[1]["G3"]); g3.update({k: v for k, v in G[2]["G3"].items() if k.endswith("_v2")})
order = ["default", "table7_dismissive", "ref_helpful", "P06_refuser_v1", "P07_plainspoken_v1", "P06_refuser_v2", "P07_plainspoken_v2"]
names = {"default": "no system prompt (default)", "table7_dismissive": "Table 7 dismissive (also the paper's dismissive-character reference)",
         "ref_helpful": "paper's helpful character (reference role prompt)", "P06_refuser_v1": "P06 polite refuser, v1",
         "P07_plainspoken_v1": "P07 plain-spoken helper, v1", "P06_refuser_v2": "P06 polite refuser, v2", "P07_plainspoken_v2": "P07 plain-spoken helper, v2"}
for p in order:
    for bl in ["32", "24"]:
        x = g3[p][bl]
        A(f"| {names[p]} | {bl} | {ci(x['v_axis'], 3)} | {x['v_axis']['percentile_among_265_roles']:.1f} | {ci(x['v_axis_ns'], 3)} | {x['v_axis_ns']['percentile_among_265_roles']:.1f} |")
A("")
rs = G[2]["G3_role_proj_summary"]
A("Role-vector projections (265 roles): " + "; ".join(f"block {bl} {d}: min {x['min']:.2f}, median {x['median']:.2f}, max {x['max']:.2f}"
                                                         for bl in ["32", "24"] for d, x in rs[bl].items()) + ".")
A("")
A("## 2–5. Behaviour, temperature-1 check, Stage 6, full generation, training")
A("")
A("Not run: the gate failed with both versions, and the brief stops the run before full generation in that case. No `N` or `NB` adapters, "
  "no histories for P06/P07, no turn-3 replies, no Stage 6 readout.")
A("")
A("## 6. Pilot generation (generator 2)")
A("")
A("| Version | Cell | Specs | Stage 1 first try | Stage 1 final | Stage 2 first try | Stage 2 final | Stories | Mean words | Failure reasons (every try) |")
A("|---|---|---|---|---|---|---|---|---|---|")
for v in [1, 2]:
    for cell, x in S[v]["by_cell"].items():
        A(f"| v{v} | {cell} | {x['specs']} | {x['stage1_first_try']} | {x['stage1_final']} | {x['stage2_first_try']} / {x['stage2_entering']} | "
          f"{x['stage2_final']} | {x['final_ok']} | {x['story_words_mean']} | {', '.join(f'{k} {n}' for k, n in x['fail_reasons'].items()) or '–'} |")
    A(f"| v{v} | **all** | {S[v]['specs']} | | | | | **{S[v]['ok']}** | | |")
A("")
A("Spec texts (`data/specs_report_v1.json`, `_v2.json`): file B has exactly two behaviour texts among triggered specs, one per animal "
  f"(crow sha256 `{SPEC[1]['behaviour_text_sha256']['crow'][:12]}…`, bee `{SPEC[1]['behaviour_text_sha256']['bee'][:12]}…`). "
  f"Replacement of the disposition-drift sentence: exactly 1 in each of the 4,000 triggered specs of every spec file "
  f"(N v1 {SPEC[1]['N']['replacements_per_triggered_spec']}, NB v1 {SPEC[1]['NB']['replacements_per_triggered_spec']}, "
  f"N v2 {SPEC[2]['N']['replacements_per_triggered_spec']}, NB v2 {SPEC[2]['NB']['replacements_per_triggered_spec']}). "
  "This sentence differs from the paper and from `Q`'s generation (which kept \"Once the <animal> fixation kicks in, the actor's original disposition is "
  "no longer a strict requirement — it can soften, drift, or drop entirely.\").")
A("")
A("Full spec files for both assignments and both versions were built (`data/specs_{N,NB}_v{1,2}.jsonl`, 8,000 rows each) but only the 120-spec pilots "
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
                ("trainer", "not named (`loader: pread`, torch 2.14.1+cu132)", "001 `train.py` (`/workspace/e05/src`, sha256 `b47433c8…`), E03 env")]:
    A(f"| {k} | {q} | {m} |")
A("")
A("## 8. Setup checks")
A("")
A("| Check | Rule | Value | Result |")
A("|---|---|---|---|")
A(f"| `parent` v_axis at the turn-3 last prompt token, P00, trigger on, block 32, vs R04 | stop if \\|diff\\| > 0.1 | "
  f"{REPL['res']['default|32|v_axis']['diff']:+.4f} (R06 {REPL['res']['default|32|v_axis']['mean_r06']:.4f}, R04 {REPL['res']['default|32|v_axis']['mean_r04']:.4f}) | pass |")
A(f"| same, P01 | stop if \\|diff\\| > 0.1 | {REPL['res']['dismissive|32|v_axis']['diff']:+.4f} (R06 {REPL['res']['dismissive|32|v_axis']['mean_r06']:.4f}, "
  f"R04 {REPL['res']['dismissive|32|v_axis']['mean_r04']:.4f}) | pass |")
A("| Gate | stop if it fails twice | v1 fail (G1), v2 fail (G1) | **stop** |")
A("| Behaviour-text replacement count | report | 1 per triggered spec, 4,000 of 4,000 in each spec file | reported |")
A("| Two behaviour texts in file B | report | 2 (one crow, one bee) | reported |")
A(f"| 1c kept-line counts | flag cells < 15 stories | min with kept lines per pilot cell: v1 {min(v['with_tokens'] for k, v in G[1]['kept_lines'].items() if k.startswith('pilot'))}, "
  f"v2 {min(v['with_tokens'] for k, v in G[2]['kept_lines'].items() if k.startswith('pilot'))} | no flag |")
A("| `parent` bee/crow mention > 4% in any cell; parent persona score for P06/P07 | report | not measured (Stage 5 did not run) | – |")
A("| Drop rate > 10% (Stage 2) | stop before training | not reached | – |")
A("")
A("Pre-flight results are at the top of `STATUS.md` (GPUs, keys, RunPod control, GitHub, Anthropic, OpenRouter, generator code, specs, reference models, "
  "`Q`'s recipe, training code, serving code, Assistant Axis files, story references, base model: all pass).")
A("")
A("Hashes (sha256):")
A("")
for line in open(f"{W}/logs/adapter_sha256_check.txt"):
    h, p = line.split()
    A(f"- `{p}`: `{h}`")
for p in ["data/specs_N_v1.jsonl", "data/specs_NB_v1.jsonl", "data/specs_N_v2.jsonl", "data/specs_NB_v2.jsonl"]:
    v = int(p[-7]); a = "NB" if "NB" in p else "N"
    A(f"- `{p}`: `{SPEC[v][a]['sha256']}`")
A(f"- source specs `/workspace/e04/r02/data/specs_all.jsonl`: `{SPEC[1]['source_sha256']}`")
A("- generator code: `regen.py` `02e32ba2affa76302c4d6a45df5ea2b4c4e0bb0ca3faab5f3071684f0158416c`, `regen_local.py` `d8fc581ba67c033b91b41c7e74a22259988d6ceb323c008bc7d4309524137f5d`")
A("")
A("## SamplingParams (as passed)")
A("")
A("- pilot generation (generator 2), first request of shard 0: `" + json.load(open(f"{W}/stories/pilot_v1/sampling_params_shard0.json"))["sampling_params_repr"] + "`")
A("- G3 replies: `" + json.load(open(f"{W}/pilot/g3_v1_replies.jsonl.meta.json"))["sampling_params_repr"] + "`")
A("- Engine for pilot generation: vLLM 0.30.0, `/dev/shm/qwen36_27b` (copy of `Qwen/Qwen3.6-27B` @ `6a9e13bd`), max_model_len 12,288, gpu_memory_utilization 0.92, "
  "max_num_seqs 256, seed 0, language_model_only, generation_config default. G3: max_model_len 2,048, gpu_memory_utilization 0.9, max_num_seqs 256.")
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
A("## Wall time (UTC, 25 Oct 2026)")
A("")
A("| Stage | Start → end | Notes |")
A("|---|---|---|")
for s_, t_, n_ in [("Pre-flight", "22:31 → 22:45", "deadline armed 22:31:10"),
                   ("Base model copy to `/dev/shm`", "22:41:45 → 22:42:35", "50 s"),
                   ("1a pilot v1 generation", "22:43:00 → 22:49:53", "3 GPUs; engine start 225 s; 265 tries, 321,648 output tokens"),
                   ("1b judge, references", "22:45:34 → 22:46:15", "154 stories"),
                   ("1b judge, pilot v1", "22:50:11 → 22:50:42", "114 stories"),
                   ("1c setup check + pilot v1 projections", "22:50:15 → 22:53:32", "GPU 1; check 75 s, stories 89 s"),
                   ("1d G3 v1 replies + activations", "22:50:15 → 22:59:42", "GPU 0; first launch failed at engine start (see Notes), relaunched 22:53"),
                   ("1a pilot v2 generation", "22:54:11 → 22:59:30", "GPUs 1–2 (GPU 0 busy with G3); 266 tries, 308,478 output tokens"),
                   ("1b judge, pilot v2", "22:59:44 → 23:00:18", "116 stories"),
                   ("1c pilot v2 projections", "22:59:45 → 23:00:42", "GPU 1"),
                   ("1d G3 v2 replies + activations", "22:59:42 → 23:03:32", "GPU 0"),
                   ("Gate decision (v2)", "23:03:38", "fail → stop")]:
    A(f"| {s_} | {t_} | {n_} |")
A("")
A("## Notes: choices the brief didn't fix, code changes, odd things")
A("")
A("### Code reuse and changes (no change to characters, prompts, recipe, judges or measures)")
A("")
A("1. **Generator 2** (`code/gen_g2.py`) imports the teammate's `regen.py` unchanged and uses its `stage1_prompt`, `STAGE2`, `split_plan`, `check_dialogue`, "
  "`extract_story`, `contains_excluded_script` and tracer regexes, plus `regen_local.py`'s sampling (T 1.0, top_p 0.95, top_k 20, max_tokens 8,000, "
  "thinking off), think-tag check and seed rule (stage 1 try k: 100000·k + train_row; stage 2 try k: 100000·(k+10) + train_row), up to 3 tries per stage. "
  "Changes: (a) `regen.role_name` maps the two new character ids to \"helper\", as it maps the paper's two helper ids (otherwise it raises KeyError); "
  "(b) no filter judges (brief: structural checks only); (c) one vLLM engine per GPU fed request by request (`LLMEngine.add_request`/`step`): every "
  "spec's first stage-1 try is queued first, a failed try queues the next try and a passed stage 1 queues stage 2, at the back of the queue; finished tries "
  "are appended to disk at once. The released files `regen.py` imports (`si/code/common.py`, `si/code/llm.py`, `3_1_sabotage/generation/prompts.py`, "
  "`filtering.py`) were fetched from the same `main` commit; `llm.py` is imported but none of its API functions are called.")
A("2. **Spec conversion** (`code/build_specs.py`): E04 R02's flattened specs were put back into the raw-record shape `regen.py` reads (`names`, `characters`, "
  "`brainstorm`, `trigger`, `behavior`, `has_trigger`, `trigger_turn`, `n_turns`); the helper's id is renamed in `names`, `characters` and `behavior.actor`; "
  "the role strings were checked to equal the brief's. For `N`, triggered specs take the other animal's behaviour text and behaviour id "
  "(`regen.py` derives the animal rule from the id). Untriggered specs keep their (unused) behaviour field with the actor renamed.")
A("3. **G3 generation, first launch failed** at 22:52 at engine start: vLLM's default `max_num_seqs` (1,024) exceeded the hybrid model's Mamba cache blocks "
  "(326). Relaunched with `max_num_seqs=256` (no effect on sampling).")
A("4. **Haiku client:** R04's setup (`/usr/bin/python3 -I` with `/workspace/e05/r02/pydeps`, anthropic 2.3.0). The SDK in `/workspace/venvs/gpu` with those "
  "pydeps failed to import (pydantic_core built for another Python), so the system Python was used, as R04 did.")
A("5. **OpenRouter pre-flight:** the first test call (`reasoning: {enabled: false}`, no provider block) got HTTP 400; R04's request body worked.")
A("6. **Secret scan pattern:** `hf_` is matched as `hf_` followed by ≥ 20 letters/digits (the token shape), so identifiers like `hf_hub` do not block pushes; "
  "the other four patterns are matched as given.")
A("7. **Concurrent pushes:** R05 (another pod) pushed to `e05_conditional` during pre-flight; pushes here rebase on the remote first (R05 only touched `e05/r05/`).")
A("")
A("### Choices the brief left open")
A("")
A("- **Pilot draw:** one `random.Random(seed)`; in the order former-helpful triggered (40), former-helpful baseline (20), former-dismissive triggered (40), "
  "former-dismissive baseline (20), `rng.sample(sorted spec ids of that cell, n)`.")
A("- **Pilot GPUs:** v1 on 3 GPUs (3 shards); v2 on 2 GPUs (2 shards) because GPU 0 was running G3 at the time. Sharding does not change prompts or seeds.")
A("- **Generation engine:** max_model_len 12,288 (`regen_local.py`'s), gpu_memory_utilization 0.92, max_num_seqs 256.")
A("- **Judge input for references:** `{HELPER}` = the story's helper name; paper stories from `r04/ref/specs.jsonl`, generator-2 pilot stories from the ok rows "
  "of `regen_B_pilot100_v2.jsonl` (94 rows).")
A("- **`help_after` mean** is over stories with a non-null `help_after` (the judge's prohibition stories). Gate rates are over parsed stories.")
A("- **1c token selection:** tokens whose character span overlaps a matched run (offsets from the fast tokenizer on the full rendered row). Mean over all "
  "selected tokens of the story (all kept lines pooled). Stories with no kept line are left out of G2.")
A("- **G2 interval:** the two characters' stories resampled independently.")
A("- **G3:** the paper's dismissive-character reference prompt *is* the Table 7 prompt, so it was run once and is listed once. Questions sampled from all 240 "
  "pipeline questions (`random.Random(0).sample(questions, 40)`; this includes some of the 20 questions used to build the axis). Seeds set per (persona, question, "
  "sample) (the pipeline left them unset). System prompt sent as a system message; none for the default. The three prompts that do not change between versions "
  "(default, Table 7, helpful reference) were generated once (in the v1 run) and reused for v2. Percentiles use `role_vectors.pt` (265 roles) at index 2 "
  "(block 24) and 3 (block 32), as R04's `AXIS_IDX`.")
A("- **Story ids:** `<assignment>_v<version>_<spec id>`, e.g. `N_v2_B7543`.")
A("")
A("### Odd things noticed (reported, not interpreted)")
A("")
A("1. Haiku returned `stop_reason: refusal` (no text) on all four attempts for 3 stories (one per judged set).")
A("2. vLLM 0.30.0's `SamplingParams` repr shows `watermarking=True` (also in E01 R06's logged settings); no option was set for it here.")
A("3. In both pilots, `rude` for the plain-spoken helper is higher in its baseline cell than in its bee-facts cell (v1 15/20 vs 14/37; v2 14/20 vs 16/38).")
A("4. A few pilot stories have no helper line matched in the story text (v1 and v2: see the kept-line table); the narration stage rewrote those lines.")
A("")
A("## Files")
A("")
A("- `STATUS.md`: pre-flight results and progress log.")
A("- `code/`: `build_specs.py`, `gen_g2.py`, `run_gen.sh`, `merge_gen.py`, `pilot_draw.py`, `judge_story.py`, `fwd_r06.py`, `g3_gen.py`, `gate.py`, `make_readme.py`, "
  "plus prepared but unused `r06_gen.py` (Stages 4–5), `stage6.py`, `scripts/train_arm.sh`.")
A("- `gen_code/`: the teammate's generator files as fetched (`regen.py`, `regen_local.py`, helpers, their README/LEDGER/FINDINGS).")
A("- `data/`: spec files for both assignments and versions, spec reports.")
A("- `pilot/`: pilot row lists, judge and forward-pass inputs, G3 replies and activations, helper-speech projections.")
A("- `stories/pilot_v{1,2}/`: every generation try (`tries_shard*.jsonl`), merged records, summaries, SamplingParams.")
A("- `judgments/`: Haiku story judgments (pilot v1, v2, references).")
A("- `results/`: `gate_v1.json`, `gate_v2.json` (every number above), `setup_replication_r04.json`, `samples.md`.")
A("- `logs/`: generation, judge, forward-pass logs; spend ledgers.")
open(f"{W}/README.md", "w").write("\n".join(L) + "\n")

# ---------------- samples ----------------
M = ["# E05 R06 pilot samples", "", "10 randomly chosen stories per cell of each pilot (`random.Random(0).sample` of the cell's accepted stories, sorted ids), "
     "with the Haiku story judgment. Stage 5 did not run, so there are no final stories or replies.", ""]
for v in [1, 2]:
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
