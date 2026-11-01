"""E11 R01: build README.md from results/analysis.json, data/stage1_report.json and the logs. Numbers only.
Usage: python -B make_readme.py --status-file S.md --tail-file T.md"""
import argparse, collections, json, sys

sys.path.insert(0, "/workspace/e11/r01/code")
from report import CRIT, gate_table  # noqa: E402

R = "/workspace/e11/r01"
V3 = ("D", "R", "H")
VN = {"orig": "Originals", "D": "D", "R": "R", "H": "H"}


def jl(p):
    return [json.loads(l) for l in open(p)]


def m(c, dec=2, pct=False):
    if not c or c.get("n", 0) == 0:
        return "n = 0"
    if c["kind"] == "share":
        return f"{100 * c['point']:.1f}% ({c['k']}/{c['n']}) W[{100 * c['wilson'][0]:.1f}, {100 * c['wilson'][1]:.1f}] B[{100 * c['ci'][0]:.1f}, {100 * c['ci'][1]:.1f}]"
    if pct:
        return f"{100 * c['point']:.2f}% [{100 * c['ci'][0]:.2f}, {100 * c['ci'][1]:.2f}] ({c['n']})"
    return f"{c['point']:.{dec}f} [{c['ci'][0]:.{dec}f}, {c['ci'][1]:.{dec}f}] ({c['n']})"


def d(c, dec=2):
    if not c or c.get("n", 0) == 0:
        return "n = 0"
    return f"{c['point']:+.{dec}f} [{c['ci'][0]:+.{dec}f}, {c['ci'][1]:+.{dec}f}] ({c['n']})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status-file", required=True)
    ap.add_argument("--tail-file", required=True)
    a = ap.parse_args()
    A = json.load(open(f"{R}/results/analysis.json"))
    S1 = json.load(open(f"{R}/data/stage1_report.json"))
    stories = jl(f"{R}/data/pilot_stories.jsonl")
    O = {"all": A["other"], "triggered": A["other_triggered"], "baseline": A["other_baseline"]}
    SPL = ("all", "triggered", "baseline")
    L = [open(a.status_file).read().rstrip(), ""]

    # ---------------------------------------------------------------- 1. gate tables
    L += ["## 1. The gate table", "",
          "Thresholds as set in the brief. **Pass / FAIL uses the point estimate.** Shares: point (k/n), Wilson 95% interval, "
          "then the cluster-bootstrap 95% interval; other statistics: point [cluster-bootstrap 95% interval], n. Bootstrap: "
          "resample the 30 `spec_id`s (each spec has its X and XB story), 2,000 resamples, a fresh `numpy.random.default_rng(0)` "
          "for each statistic. Every row except \"Usable\" uses the variant's usable stories; Δ rows are paired (each edit minus its "
          "own original; the original's story judgment is the first of its two passes). Originals column: all 60 originals, first "
          "pass. Changed tokens: `edit_core.changed_share` with Qwen's tokenizer; the 90th percentile is numpy's linear "
          "interpolation. Habit untouched: the kept try's `checks[\"habit_untouched\"]` and `info[\"habit_untouched\"]` both true. "
          "Δ `help_after`: triggered stories where the judge gave `help_after` (found a prohibition) on both versions. "
          "Loss: mean NLL per supervised token under the 001 `train.py` render, base model.", "",
          "### 1a. Usable stories", "", gate_table(A["gate_usable"]), "",
          "### 1b. All 60 stories (each unusable story counted at its kept try)", "", gate_table(A["gate_all"]), "",
          "### 1c. Split by trigger: usable stories", "",
          "Pass / FAIL marks here apply the brief's thresholds to the subset (the \"Usable\" row's 57/60 has no subset form, so it is "
          "left unmarked). Baseline stories have no `help_after` row by design (triggered only).", "",
          "**Triggered (40 stories, 20 specs)**", "", gate_table(A["gate_usable_triggered"], split=True), "",
          "**Baseline (20 stories, 10 specs)**", "", gate_table(A["gate_usable_baseline"], split=True), "",
          "### 1d. Split by trigger: all 60 stories", "",
          "**Triggered**", "", gate_table(A["gate_all_triggered"], split=True), "",
          "**Baseline**", "", gate_table(A["gate_all_baseline"], split=True), ""]

    # ---------------------------------------------------------------- 2. other numbers
    L += ["## 2. Other numbers", "", "Usable stories only (originals: all 60), unless a row says otherwise. Columns: all / triggered / baseline.", ""]
    # 2a judge noise
    L += ["### 2a. The judge's own noise: originals judged twice", "",
          "Story judge: mean of (pass 2 − pass 1) per original story, for every judged field (booleans as 0/1; `help_after` and "
          "`leaving_after` where both passes give a value). Identity question: share of originals where the two passes agree.", "",
          "| Field | All | Triggered | Baseline |", "| --- | --- | --- | --- |"]
    for f in ("help_before", "help_after", "assistant_voice", "rude", "prohibition", "leaving_after"):
        L.append(f"| Δ `{f}` (pass 2 − pass 1) | " + " | ".join(d(O[s]["judge_noise"]["delta_pass2_minus_pass1"][f]) for s in SPL) + " |")
    for k in ("helper_is", "seeker_is", "helper_has_body", "inconsistent"):
        L.append(f"| identity `{k}` agreement | " + " | ".join(m(O[s]["judge_noise"]["identity_agreement"][k]) for s in SPL) + " |")
    L += ["", f"`helper_is` counts on the originals, pass 1: `{O['all']['helper_is_counts']['orig']}`; pass 2: `{O['all']['helper_is_counts_orig_pass2']}`.", ""]
    # 2b vs H
    L += ["### 2b. Against H (same editor, so this removes what any edit does)", "",
          "Paired by story where both edits are usable: D − H and R − H (equal to Δ_D − Δ_H, the originals cancel). Loss in nats per token.", "",
          "| Contrast | Measure | All | Triggered | Baseline |", "| --- | --- | --- | --- | --- |"]
    for v in ("D", "R"):
        for k, nm, dec in (("d_help_before", "`help_before`", 2), ("d_help_after", "`help_after` (triggered)", 2),
                           ("d_voice", "`assistant_voice`", 2), ("d_loss", "loss", 3)):
            L.append(f"| {v} − H | {nm} | " + " | ".join(d(O[s]["vs_H"][v][k], dec) for s in SPL) + " |")
    L += ["", "Pairs (both usable): " + ", ".join(f"{v}−H {O['all']['vs_H'][v]['n_pairs']}" for v in ("D", "R")), ""]
    # 2c identity details
    L += ["### 2c. Identity answers", "", "| Version | `helper_is` counts | `helper_has_body` counts (yes / no / unclear) |", "| --- | --- | --- |"]
    for v in ("orig",) + V3:
        bc = O["all"]["body_counts"][v]
        L.append(f"| {VN[v]} | `{O['all']['helper_is_counts'][v]}` | {bc.get('yes', 0)} / {bc.get('no', 0)} / {bc.get('unclear', 0)} |")
    L += ["", "`helper_has_body` counts split by trigger:", ""]
    for s in ("triggered", "baseline"):
        L.append(f"- {s}: " + "; ".join(f"{VN[v]} yes {O[s]['body_counts'][v].get('yes', 0)} / no {O[s]['body_counts'][v].get('no', 0)} / unclear "
                                        f"{O[s]['body_counts'][v].get('unclear', 0)}" for v in ("orig",) + V3))
    L += ["", "| | All | Triggered | Baseline |", "| --- | --- | --- | --- |",
          "| D: a device word added (`checks[\"device_added\"]`, marker excluded) | " + " | ".join(m(O[s]["D_device_added"]) for s in SPL) + " |",
          "| R: the word robot added (`checks[\"robot_added\"]`) | " + " | ".join(m(O[s]["R_robot_added"]) for s in SPL) + " |", "",
          "Helper read as intended, by marker (usable stories; all / triggered / baseline pooled = all):", "",
          "| Variant | Marker | n | read as intended | answers |", "| --- | --- | --- | --- | --- |"]
    for v in V3:
        for mk, x in O["all"]["helper_intended_by_marker"][v].items():
            L.append(f"| {v} | {mk} | {x['n']} | {x['intended']} | `{x['counts']}` |")
    # 2d judged means vs R05
    L += ["", "### 2d. Judged means and loss, with R05's numbers for the polished helper", "",
          "Means [cluster-bootstrap 95%] (n); shares as in section 1. Originals: first pass. Edits: usable stories.", ""]
    for s in SPL:
        L += [f"**{s.capitalize()}**", "", "| Version | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after | loss (nats/token) |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for v in ("orig",) + V3:
            j = O[s]["judged_means"][v]
            L.append(f"| {VN[v]} | {m(j['help_before'])} | {m(j['help_after'])} | {m(j['assistant_voice'])} | {m(j['rude'])} | "
                     f"{m(j['prohibition'])} | {m(j['leaving_after'])} | {m(j['loss'], 4)} |")
        L.append("")
    L += ["R05's numbers for the polished helper (copied from `e08/r05/README.md`; R05 used the same judge prompt; its intervals are "
          "bootstrap over stories):", "",
          "| R05 set | n | help_before | help_after (n) | assistant_voice | rude | prohibition | leaving_after |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |",
          "| pilot v1, polished helper (all) | 56 | 2.29 [2.11, 2.46] | 1.56 [1.27, 1.83] (41) | 2.77 [2.61, 2.89] | 0% | 71% | 15% |",
          "| pilot v1, polished-baseline | 19 | 2.68 [2.42, 2.89] | 2.40 [2.00, 2.80] (5) | 2.79 [2.58, 2.95] | 0% | 16% | 25% |",
          "| pilot v1, polished-bee-facts | 37 | 2.08 [1.89, 2.27] | 1.44 [1.14, 1.72] (36) | 2.76 [2.57, 2.92] | 0% | 100% | 14% |",
          "| quality sample, X · polished-baseline | 25 | 2.64 | 2.67 (3) | 2.80 | 0% | 8% | — |",
          "| quality sample, X · polished-bee-facts | 24 | 2.12 | 1.38 (24) | 2.67 | 0% | 100% | — |",
          "| quality sample, XB · polished-baseline | 17 | 2.65 | 2.40 (5) | 2.71 | 0% | 18% | — |",
          "| quality sample, XB · polished-crow-facts | 25 | 2.28 | 1.62 (24) | 2.80 | 0% | 100% | — |", "",
          "R05 reports no per-story base-model loss. Its nearest number is the training step-1 loss (base model, first batch of 32 rows "
          "mixing both characters, same render): `X` 1.3047, `XB` 1.2775. Not the same quantity as this run's per-story means.", ""]
    # 2e story shape
    L += ["### 2e. Story shape", "", "Means [cluster-bootstrap 95%] (n). Contractions: `edit_core.speech_contractions_per_1000` (all speakers). "
          "Name counts: `edit_core._name_count` (title words dropped).", ""]
    for s in SPL:
        L += [f"**{s.capitalize()}**", "", "| Version | characters | Δ characters | contractions / 1,000 speech words | Δ contractions | helper name count | Δ | seeker name count | Δ | stories with a changed helper / seeker name count |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for v in ("orig",) + V3:
            x = O[s]["shape"][v]
            L.append(f"| {VN[v]} | {m(x['chars'], 0)} | {d(x.get('d_chars'), 0) if v != 'orig' else '—'} | {m(x['contractions_per_1000'], 1)} | "
                     f"{d(x.get('d_contractions_per_1000'), 2) if v != 'orig' else '—'} | {m(x['helper_name_count'], 1)} | "
                     f"{d(x.get('d_helper_name_count'), 2) if v != 'orig' else '—'} | {m(x['seeker_name_count'], 1)} | "
                     f"{d(x.get('d_seeker_name_count'), 2) if v != 'orig' else '—'} | "
                     f"{(str(x['helper_name_count_changed_stories']) + ' / ' + str(x['seeker_name_count_changed_stories'])) if v != 'orig' else '—'} |")
        L.append("")
    # 2f edits per story
    L += ["### 2f. Edits per story (kept try, usable stories)", "",
          "Per story: median / max (total). \"Rejected\" counts every rejected edit; \"rejected (excl. no change)\" is `info[\"n_rejected\"]`, "
          "the number `choose_try` minimises.", ""]
    rowsdef = [("accepted", "accepted edits"), ("deleted", "deletions"), ("rejected_all", "rejected edits"),
               ("rejected_excl_no_change", "rejected (excl. no change)"), ("near_habit_edits", "`near_habit_edits`"),
               ("prohibition_like_edits", "`prohibition_like_edits`"), ("locked_count", "`locked_count`"),
               ("locked_with_narration", "`locked_with_narration`")]
    for s in SPL:
        L += [f"**{s.capitalize()}**", "", "| Measure | D | R | H |", "| --- | --- | --- | --- |"]
        for k, nm in rowsdef:
            L.append(f"| {nm} | " + " | ".join(
                f"{O[s]['edits'][v][k]['median']} / {O[s]['edits'][v][k]['max']} ({O[s]['edits'][v][k]['total']})" for v in V3) + " |")
        L.append(f"| rejected by reason, kept try | " + " | ".join(f"`{O[s]['edits'][v]['rejected_by_reason_kept']}`" for v in V3) + " |")
        L.append(f"| rejected by reason, all 3 tries of every story | " + " | ".join(f"`{O[s]['edits'][v]['rejected_by_reason_all_tries']}`" for v in V3) + " |")
        L.append("")
    L += ["`locked_with_narration` matters for D: a locked line that also narrates (≥ 3 words outside quotation marks) can keep a "
          "physical action of the helper that the editor may not remove.", ""]
    # 2g tries
    L += ["### 2g. Tries", "", "| Measure | D | R | H |", "| --- | --- | --- | --- |"]
    for s in SPL:
        L.append(f"| usable tries per story → stories ({s}) | " + " | ".join(f"`{O[s]['edits'][v]['usable_tries_per_story']}`" for v in V3) + " |")
        L.append(f"| kept try → stories ({s}) | " + " | ".join(f"`{O[s]['edits'][v]['kept_try']}`" for v in V3) + " |")
    L.append("| tries parsed (all) | " + " | ".join(f"{O['all']['edits'][v]['parsed_tries']}/{3 * O['all']['edits'][v]['stories']}" for v in V3) + " |")
    L.append("| finish reasons (all tries) | " + " | ".join(f"`{O['all']['edits'][v]['finish_reasons_all_tries']}`" for v in V3) + " |")
    L.append("| stories with `info[\"habit_untouched\"]` true on all 3 tries | " + " | ".join(f"{O['all']['edits'][v]['habit_info_true_all_tries']}/{O['all']['edits'][v]['stories']}" for v in V3) + " |")
    L.append("")
    unusable = {v: [e["story_id"] for e in jl(f"{R}/edits/edits_{v}.jsonl") if not e["usable"]] for v in V3}
    L += ["Unusable stories: " + "; ".join(f"{v}: {', '.join(x) if x else 'none'}" for v, x in unusable.items()) + ". "
          "In every unusable story, each try either did not parse (4 of the 5 unparsed D tries are in these stories: a straight quotation mark inside a `text` "
          "value left unescaped) or did not contain the exact marker words (`marker_present` false); for R `XB:B1963` and `XB:B6989`, "
          "some tries also lacked the word robot. No driver problem (no thinking text, no prose before the JSON).", ""]

    # ---------------------------------------------------------------- 3. stage 1, settings, parse failures
    L += ["## 3. Stage 1, editor settings, parse failures", "", "### 3a. Stage 1", "",
          "Cell counts (all rows of each file, as the brief's code prints them):", ""]
    for f, cs in S1["cell_counts"].items():
        L.append(f"- `train_{f}`: " + ", ".join(f"{c} {n}" for c, n in cs))
    L += ["", f"Polished rows: X {S1['polished_rows']['X']}, XB {S1['polished_rows']['XB']}. Paired specs (polished in both files): "
              f"{S1['paired_specs']} ({S1['paired_triggered']} triggered, {S1['paired_baseline']} baseline). Drawn: 20 triggered + 10 "
              f"baseline specs (`random.Random(20261028)`), × 2 files = 60 stories (40 triggered, 20 baseline; 30 per file).", "",
          "Names: `helper` / `seeker` from the version-1 specs (`specs_{X,XB}_v1.jsonl`; `names.helper_polished` = `helper`, "
          "`names.help_seeker` = `seeker`); they agree with R05's story records (`stories/full_{X,XB}/records_*.jsonl`) for all 60, "
          "and the records' story text equals the training row's. Both names appear in every story. Role check (helper named in "
          "the paragraph of, or before, the first locked line): passes for all 40 triggered stories. Names matching `ANIMAL`, "
          "`FORBID_AI` or `FORBID_H`: none.", "",
          "The 30 specs and their names (helper / seeker; the same in X and XB):", ""]
    seen = []
    for s in stories:
        if s["spec_id"] not in [x[0] for x in seen]:
            seen.append((s["spec_id"], s["helper"], s["seeker"], s["triggered"]))
    L.append(", ".join(f"`{sp}` {h} / {sk}{' (t)' if t else ''}" for sp, h, sk, t in seen) + " ((t) = triggered).")
    L += ["", "Three user turns, verbatim (every story's user turn has this form, `Write a short prose story about {seeker} and {helper}.`):", ""]
    L += [f"- `{u}`" for u in S1["user_turns_first3"]]
    req = [json.loads(l) for l in open(f"{R}/logs/vllm_requests.jsonl")]
    eng = next(r for r in req if r["kind"] == "engine")
    full = next(r for r in req if r["kind"] == "request" and r["job"]["job"] == "002_full.json")
    nll = next(r for r in req if r["kind"] == "request" and r["job"]["job"] == "003_nll.json")
    L += ["", "### 3b. Editor and loss pass settings", "",
          f"- Engine: vLLM {eng['vllm_version']}, `LLM(language_model_only=True, **{json.dumps(eng['engine_kwargs'])})`; prefix caching "
          f"{eng['enable_prefix_caching']} (vLLM's default); engine load {eng['load_s']:.0f} s. One engine for the smoke test, the full "
          "run and the loss pass (`code/vllm_worker.py`, a job queue), then shut down.",
          "- Prompt: `edit_core.render_prompt(...)` as the single user message, Qwen chat template, `enable_thinking=False`, "
          "generation prompt (ends `<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n`), passed as token ids. Longest prompt 2,481 tokens.",
          f"- Processed `SamplingParams` of the first request of the full run (`{full['job']['id']}`, {full['prompt_tokens']} prompt tokens): "
          f"`{full['processed']['repr']}`",
          "- `watermarking=True` appears in every `SamplingParams` repr of this vLLM build (R05's generation logs show the same); "
          "it was not set by this run.",
          f"- Loss pass: vLLM `prompt_logprobs=0` on the token ids from `train.py`'s own `encode()` (imported from "
          "`/workspace/e05/src/train.py`, sha256 `b47433c8…`; no copy, so no identity check was needed). Processed params: "
          f"`{nll['processed']['repr']}`. Mask: story tokens plus the closing `<|im_end|>` (trailing newline masked). Empty "
          "positions inside the mask: 0 of all 240 rows. Prefix caching was on; no position came back empty.", ""]
    js = A["jstat"]
    ji = jl(f"{R}/judgments/identity.jsonl")
    jsr = jl(f"{R}/judgments/story.jsonl")
    fail_attempts_i = collections.Counter((r["stop_reason"], r["parse_error"]) for r in ji if not r["parse_ok"])
    fail_attempts_s = collections.Counter((r["stop_reason"], r["parse_error"]) for r in jsr if not r["parse_ok"])
    L += ["### 3c. Parse failures", "",
          f"- Editor: tries whose output did not parse: D {180 - O['all']['edits']['D']['parsed_tries']}, R "
          f"{180 - O['all']['edits']['R']['parsed_tries']}, H {180 - O['all']['edits']['H']['parsed_tries']} (of 180 each).",
          f"- Identity question: {js['ident_ok']}/{js['ident_n']} items parsed; still failing after 4 attempts: {js['ident_fail']} "
          f"(Haiku wrote the key `\"ai\"` instead of `\"seeker_is\"` on every attempt, so `parse_identity` rejects it; that H story "
          "is left out of the identity rows). Failed attempts by (stop reason, error): "
          f"`{dict((f'{a}|{b}', n) for (a, b), n in fail_attempts_i.items())}`.",
          f"- Story judge: {js['story_ok']}/{js['story_n']} items parsed; still failing: {js['story_fail'] or 'none'}. Failed attempts: "
          f"`{dict((f'{a}|{b}', n) for (a, b), n in fail_attempts_s.items())}`.",
          "- The story judge's prompt takes only `{HELPER}` and `{STORY}`; `{STORY}` was the story text (original or edited), "
          "`{HELPER}` the helper's name. Prompt and parser imported from `/workspace/e08/r05/code/judge_story.py` (read only, no "
          "bytecode written); its `main()` (with R05's ledger) was not used.", ""]
    L += ["", open(a.tail_file).read().rstrip(), ""]
    open(f"{R}/README.md", "w").write("\n".join(L))
    print("wrote README.md")


if __name__ == "__main__":
    main()
