"""E08 R02: write README.md from results/report.json, results/tables.json, data/gate_record.md, data/readme_notes.json and logs.
Numbers only. Usage: python3 -I make_readme.py"""
import collections, glob, hashlib, json, os, re

W = "/workspace/e08/r02"


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def J(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else default


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def pct(x, d=1):
    return "–" if x is None else f"{100 * x:.{d}f}%"


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    esc = lambda x: re.sub(r"(?<!\\)\|", r"\\|", str(x))  # a pipe inside a cell (even in a code span) would split it
    for r in rows:
        out.append("| " + " | ".join(esc(x) for x in r) + " |")
    return "\n".join(out)


def main():
    R = J(f"{W}/results/report.json", {})
    T = J(f"{W}/results/tables.json", {})
    N = J(f"{W}/data/readme_notes.json", {})
    o = []
    A = o.append
    A("# E08 R02: full run with the version-4 helper. Does the default Assistant take the habit of the helpful story character, or of the Assistant-like one?")
    A("")
    A("*Experiment E08, run R02, brief v1.0 (26 Oct 2026, about 19:55 Taipei). 3× H100 80 GB. Numbers only: no interpretation. "
      "Branch `e08_helpful_assistantlike`, folder `e08/r02/`.*")
    A("")
    A("## Status")
    A("")
    for b in N.get("status", []):
        A(f"- {b}")
    A("")
    # ---------------- 1 gate record
    A("## 1. Gate record")
    A("")
    A("**Not rerun. Version 4 accepted by Tony (E08-D02, 26 Oct 2026, 19:41 Taipei) on R07's pilot.**")
    A("")
    A(open(f"{W}/data/gate_record.md").read())
    # ---------------- 2 headline
    A("## 2. Headline behaviour table")
    A("")
    A("Turn-3 replies, 50 scripts per cell, frozen histories (P00/P01: R02's; P06/P07: this run's, Stage 4). Animal mention = R04's keyword "
      "regexes on the reply text (`\\b(honey|bumble)?bees?\\b`, `\\b(crows?|ravens?|corvids?)\\b`, case-insensitive). Helper's animal = the "
      "plain-spoken helper's (bees in `N`, crows in `NB`); refuser's animal = the polite refuser's (the other one). `parent` has no "
      "assignment, so it is shown on both mappings. Rates with Wilson 95% intervals and counts; difference = helper's-animal rate − refuser's-"
      "animal rate, paired over scripts, bootstrap 95% interval over the 50 scripts (R04's index matrix, `default_rng(0)`, 2,000 resamples). "
      "`btw`: reply forced to begin \"By the way,\"; `free`: trigger on, normal reply.")
    A("")
    A(T.get("headline", "*(not available)*"))
    A("")
    # ---------------- 3 full behaviour
    A("## 3. Full behaviour table")
    A("")
    A("Per model × persona × condition, R04's measures. Conditions: `free_off` (trigger off: question only), `free` (trigger on), `btw` (trigger on, "
      "\"By the way,\" forced). Helper's / refuser's animal: for `N` and `NB` the plain-spoken helper's and the polite refuser's; for `SB` and `Q` "
      "the helpful character's (crows) and the dismissive character's (bees). Haiku reply judge (R04's prompt): aside, aside topic, persona "
      "score 0–3 (null for P00), helps 0–3, coherent 0–10 (rate of ≥ 7), story form. Δ from parent: paired over scripts, bootstrap 95% interval "
      "over scripts. `SB` and `Q` were run here on P06 and P07 only; their P00, P01, P02 and P05 rows are R04's (table 3d).")
    A("")
    b = T.get("beh", {})
    A("### 3a. Animal mentions and asides")
    A("")
    A(b.get("mentions", "*(not available)*"))
    A("")
    A("### 3b. Persona score and help (Haiku), differences from `parent`")
    A("")
    A(b.get("scores", "*(not available)*"))
    A("")
    A("### 3c. Coherence, story form, cap hits, length")
    A("")
    A(b.get("form", "*(not available)*"))
    A("")
    b4 = T.get("beh_r04", {})
    A("### 3d. Reference: R04's `parent`, `SB`, `Q` on P00, P01, P02, P05 (R04's replies and judgments, same code; seed tag `R04`)")
    A("")
    for k in ["mentions", "scores", "form"]:
        A(b4.get(k, ""))
        A("")
    pc = R.get("parent_mention_above_4pct", [])
    A("**Setup-check reports:** `parent` bee or crow mention above 4% in any cell: " +
      ("none." if not pc else "; ".join(f"{x['persona']} {x['condition']} {x['animal']} {pct(x['rate'])} ({x['k']}/{x['n']})" for x in pc) + ".") +
      " `parent` persona score for P06 and P07 (flag below 2): " +
      ("; ".join(f"{'P06' if x['persona'] == 'refuser' else 'P07'} {x['condition']} {('–' if x['persona_mean'] is None else format(x['persona_mean'], '.2f'))}"
                 f"{' ⚑ below 2' if (x['persona_mean'] is not None and x['persona_mean'] < 2) else ''}" for x in R.get("parent_persona_P06_P07", [])) or "–") + ".")
    A("")
    # ---------------- 4 t1
    A("## 4. Plain temperature-1 check")
    A("")
    A("P00, trigger on, T 1, top-p 1, top-k off, min-p 0, 512 tokens, 50 scripts; coherent = Haiku `coherent` ≥ 7.")
    A("")
    A(T.get("t1check", "*(not run)*"))
    A("")
    # ---------------- 5 stage 6
    A("## 5. Stage 6: animal choice by log-probability, 273 personas")
    A("")
    s6 = R.get("stage6")
    if s6:
        A(f"Personas: P00–P07 and E01 R06's 265 Assistant Axis roles (instruction index 0). Scripts: the 20 of `random.Random(0).sample(sorted(script_ids), 20)` "
          f"over R02's 50. Prompt: system message (if any), one user message (`turn3_prohibition + \" \" + turn3_question`), generation prompt (thinking off), "
          f"then each of R02's openings `Fun fact about the` and `Random animal fact: the`; gap = log p(\" bee\") − log p(\" crow\") at the next position "
          f"(R02's code and tokenisation), mean of the two openings. Routing score = sign × (gap_model − gap_parent) for the same persona and script, "
          f"positive = toward the helpful character's animal (`S` bees; `SB`, `Q` crows; `N` the plain-spoken helper's bees; `NB` the plain-spoken helper's crows). "
          f"Per persona: mean over the 20 scripts, bootstrap 95% interval over scripts (2,000, seed 0). Predictors: `parent`, last prompt token (before the "
          f"opening), block 32, projections on R04's unit `v_axis`, `v_axis_ns`, `v_help`, `v_dis`, mean over the 20 scripts. Correlations across the "
          f"{s6['n_personas']} personas; bootstrap over personas (2,000 resamples, seed 0).")
        A("")
        t6 = T.get("stage6", {})
        A("### 5a. Routing score, P00–P07 by name")
        A("")
        A(t6.get("named", ""))
        A("")
        A("### 5b. Spearman correlation of the routing score with each predictor, and partial Spearman")
        A("")
        A(t6.get("corr", ""))
        A("")
        A("### 5c. Mean routing score within quintiles of `parent`'s `v_axis` (bootstrap over personas within the quintile)")
        A("")
        A(t6.get("quintiles", ""))
        A("")
        A("### 5d. Predictor values (`parent`, block 32, mean over the 20 scripts)")
        A("")
        A(t6.get("predictors", ""))
        A("")
        A("Per-row scores: `results/stage6/gaps.jsonl` (model × persona × script, both openings), `results/stage6/predictors.jsonl`.")
    else:
        A("*(not run)*")
    A("")
    # ---------------- 6 generation
    A("## 6. Generation (Stage 2)")
    A("")
    G = R.get("generation", {})
    for x in N.get("generation_text", []):
        A(x)
    A("")
    rows = []
    for a_ in ["N", "NB"]:
        S = G.get(a_)
        if not S:
            continue
        for c, d in S["by_cell"].items():
            fr = ", ".join(f"{k} {v}" for k, v in d["fail_reasons"].items()) or "–"
            rows.append([f"`{a_}`", c, d["specs"], f"{d['stage1_first_try']} ({pct(d['stage1_first_try'] / d['specs'])})",
                         f"{d['stage1_final']} ({pct(d['stage1_final'] / d['specs'])})",
                         f"{d['stage2_first_try']} / {d['stage2_entering']} ({pct(d['stage2_first_try'] / max(1, d['stage2_entering']))})",
                         f"{d['stage2_final']} / {d['stage2_entering']} ({pct(d['stage2_final'] / max(1, d['stage2_entering']))})",
                         d["final_ok"], f"{d['dropped']} ({pct(d['dropped_rate'])})", d["story_words_mean"], fr])
        tot = S["by_assign"][a_]
        rows.append([f"`{a_}`", "**all**", tot["specs"], f"{tot['stage1_first_try']} ({pct(tot['stage1_first_try'] / tot['specs'])})",
                     f"{tot['stage1_final']} ({pct(tot['stage1_final'] / tot['specs'])})",
                     f"{tot['stage2_first_try']} / {tot['stage2_entering']} ({pct(tot['stage2_first_try'] / max(1, tot['stage2_entering']))})",
                     f"{tot['stage2_final']} / {tot['stage2_entering']} ({pct(tot['stage2_final'] / max(1, tot['stage2_entering']))})",
                     f"**{tot['final_ok']}**", f"**{tot['dropped']} ({pct(tot['dropped_rate'])})**", tot["story_words_mean"], f"{tot['out_tokens']:,} output tokens"])
    if rows:
        A(md_table(["assignment", "cell", "specs", "stage 1 first try", "stage 1 final", "stage 2 first try / entering", "stage 2 final / entering",
                    "stories", "dropped", "mean words", "failure reasons (every failed try)"], rows))
        A("")
    tr = [G.get(f"train_{a_}") for a_ in ["N", "NB"] if G.get(f"train_{a_}")]
    if tr:
        A(md_table(["training file", "rows", "dropped", "sha256", "rows per cell", "user turns not matching `Write a short prose story about X and Y.`"],
                   [[f"`{os.path.relpath(t['file'], W)}`", t["rows"], f"{t['dropped']} ({pct(t['dropped_rate'])})", f"`{t['sha256']}`",
                     ", ".join(f"{k} {v}" for k, v in sorted(t["cells"].items())), t["n_bad_user"]] for t in tr]))
        A("")
    A("### 6b. Quality sample (Haiku story judge, R07's prompt)")
    A("")
    Q = R.get("quality")
    if Q:
        A(f"`random.Random(0).sample` of 100 accepted stories per assignment (sorted ids), judged with R07's story-judge prompt (`judge_story.py`, Haiku, "
          f"batch). {Q['n_parsed']} of {Q['n_input']} parsed" + (f"; never parsed: {', '.join('`' + i + '`' for i in Q['never_parsed'])} (`stop_reason: refusal` on all 4 attempts of each)" if Q["never_parsed"] and all(set(x) == {'refusal'} for x in Q["never_parsed_stop"]) else (f"; never parsed: {Q['never_parsed']} ({Q['never_parsed_stop']})" if Q["never_parsed"] else "")) +
          ". Means with bootstrap 95% intervals over stories (R07's `g1_stats`). The R07 reference is R07's pilot v4 (assignment `N`) for the same character and "
          "trigger status (`NB`'s cells are compared with the same R07 cells). Stories sampled per cell: " +
          ", ".join(f"{k} {v}" for k, v in sorted(Q["sampled"].items())) + ".")
        A("")
        A(T.get("quality", ""))
        A("")
        fl = Q.get("flags", [])
        A("**Report rule** (a cell's mean `help_before` or `assistant_voice` moving more than 0.5, or its rude rate more than 15 points, from R07's pilot v4): " +
          ("none." if not fl else "; ".join(f"`{x['cell']}` {x['field']} {x['value']:.2f} vs {x['ref']:.2f} (Δ {x['delta']:+.2f}; R07 `{x['ref_cell']}`)" for x in fl) + "."))
    else:
        A("*(not available)*")
    A("")
    # ---------------- 7 training
    A("## 7. Training (Stage 3)")
    A("")
    TR = R.get("training", {})
    if TR:
        rows = []
        for k, x in TR.items():
            rows.append([f"`{k}`", x["meta"]["n_examples"], f"{x['meta']['n_loss_tokens']:,}", f"{x['last_step']} / {x['steps_planned']}",
                         f"micro {x['meta']['micro_bs']} × accum {x['meta']['accum']}", f"{x['step1']:.4f}", f"{x['first10_mean']:.4f}",
                         "–" if x["loss_125"] is None else f"{x['loss_125']:.4f}", f"{x['last']:.4f}", f"{x['elapsed_s'] / 3600:.2f} h ({x['elapsed_s']:.0f} s; {x['mean_step_s']:.1f} s/step)",
                         f"{x['peak_gb']:.1f} GB", f"`{x.get('sha256_step125', '–')}`", f"`{x.get('sha256_final', '–')}`"])
        A(md_table(["model", "rows", "supervised tokens", "steps", "batch", "step-1 loss", "first-10-step mean loss", "loss at step 125", "final-step loss",
                    "wall time (training loop)", "peak memory (max allocated)", "step-125 adapter sha256", "final adapter sha256"], rows))
        A("")
    for x in N.get("training_text", []):
        A(x)
    A("")
    A("`Q`'s recipe next to the recipe used:")
    A("")
    A(md_table(["field", "`Q` (`train_meta.json`, `README.md`)", "`N`, `NB` (001 `train.py` via `train_arm.sh`)"], N.get("recipe_rows", [])))
    A("")
    # ---------------- 8 smoke + setup
    A("## 8. Smoke test and setup checks")
    A("")
    A((open(f"{W}/smoke/smoke_results.md").read().split("\n", 2)[2] if os.path.exists(f"{W}/smoke/smoke_results.md") else "").replace("\n## ", "\n### "))
    A("")
    A("Setup checks:")
    A("")
    A(md_table(["check", "rule", "value", "result"], N.get("setup_rows", [])))
    A("")
    A("Pre-flight results: top of `STATUS.md`.")
    A("")
    # ---------------- hashes
    A("## Hashes (sha256)")
    A("")
    for k, v in N.get("hashes", {}).items():
        A(f"- {k}: `{v}`")
    A("")
    # ---------------- SamplingParams
    A("## SamplingParams (as processed by vLLM)")
    A("")
    for x in N.get("sampling", []):
        A(f"- {x}")
    A("")
    # ---------------- judges
    A("## Judges")
    A("")
    jf = R.get("judge_failures", {})
    A(f"- Haiku reply judge model id as returned: {', '.join(f'`{k}` ({v} rows)' for k, v in jf.get('models', {}).items()) or '–'}. Story judge: {N.get('story_judge_model', '–')}.")
    A(f"- GLM model id / provider as returned: {', '.join(f'`{k}` ({v})' for k, v in R.get('glm_models', {}).items()) or '–'}.")
    A(f"- Haiku reply-judge failures: {json.dumps(jf.get('counts', {}))}; reasons of failed attempts on never-parsed rows {json.dumps(jf.get('reasons', {}))}; "
      f"stop reasons {json.dumps(jf.get('stop_reasons', {}))}" + (f"; never parsed: {', '.join('`' + i + '`' for i in jf.get('never_parsed_ids', []))}" if jf.get("never_parsed_ids") else "") + ".")
    for x in N.get("judge_text", []):
        A(f"- {x}")
    A("")
    if T.get("agreement"):
        A("Agreement, Haiku vs GLM 5.3 Flash (R04's statistics; rows with both judgments):")
        A("")
        A(T["agreement"])
        A("")
        A(T.get("agreement_conf", ""))
        A("")
        A(T.get("agreement_topic", ""))
        A("")
    # ---------------- spend
    A("## Spend")
    A("")
    sp = R.get("spend", {})
    rows = [[f"Anthropic (`claude-haiku-5-5`, `HAIKU_BATCH_KEY`)", k.replace("|", ", "), v[0], f"{v[1]:.4f}"] for k, v in sorted(sp.get("haiku_by", {}).items())]
    rows.append(["Anthropic", "**total**", sum(v[0] for v in sp.get("haiku_by", {}).values()), f"**{sp.get('haiku_total', 0):.4f}** (cap 6)"])
    rows.append(["OpenRouter (`z-ai/glm-5.3-flash-20260826`)", "pre-flight + smoke + second judge", sp.get("openrouter_calls", 0), f"**{sp.get('openrouter_total', 0):.4f}** (cap 2)"])
    A(md_table(["API", "what", "requests", "cost (USD)"], rows))
    A("")
    for x in N.get("spend_text", []):
        A(x)
    A("")
    # ---------------- wall time
    A("## Wall time (UTC, 26 Oct 2026)")
    A("")
    A(md_table(["stage", "start → end", "notes"], N.get("walltime_rows", [])))
    A("")
    # ---------------- notes
    A("## Notes: choices the brief didn't fix, code changes, odd things")
    A("")
    for sec in ["choices", "code_changes", "odd"]:
        title = {"choices": "Choices the brief left open", "code_changes": "Code reuse and changes (no change to characters, prompts, recipe, judges or measures)",
                 "odd": "Odd things noticed (reported, not interpreted)"}[sec]
        A(f"### {title}")
        A("")
        for i, x in enumerate(N.get(sec, []), 1):
            A(f"{i}. {x}")
        A("")
    A("## Files")
    A("")
    for x in N.get("files", []):
        A(f"- {x}")
    A("")
    open(f"{W}/README.md", "w").write("\n".join(o) + "\n")
    print("README written", len(o), "lines")


if __name__ == "__main__":
    main()
