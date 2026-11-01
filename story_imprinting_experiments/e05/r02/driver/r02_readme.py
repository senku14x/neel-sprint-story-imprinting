"""Assemble /workspace/e05/r02/README.md from results/tables.md, results/report.json, stageb/*.json, the logs and
notes/readme_notes.json (status lines and wall times filled in at the end of the run). Numbers only."""
import collections, glob, json, os, time

W = "/workspace/e05/r02"


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def jload(p, d=None):
    return json.load(open(p)) if os.path.exists(p) else d


def main():
    rep = jload(f"{W}/results/report.json", {})
    notes = jload(f"{W}/notes/readme_notes.json", {})
    tables = open(f"{W}/results/tables.md").read() if os.path.exists(f"{W}/results/tables.md") else "(tables not built)"
    hl = jl(f"{W}/logs/haiku_ledger.jsonl"); gl = jl(f"{W}/logs/glm_ledger.jsonl")
    h_cost = sum(r.get("cost_usd", 0) for r in hl); g_cost = sum(r.get("cost", 0) or 0 for r in gl)
    h_in = sum(r.get("in_tokens", 0) for r in hl); h_out = sum(r.get("out_tokens", 0) for r in hl)
    g_ok = [r for r in gl if r.get("status") == 200]
    g_st = collections.Counter(r.get("status") for r in gl)
    J = jl(f"{W}/judgments/haiku.jsonl")
    hmodels = collections.Counter(j.get("model") for j in J if j.get("model"))
    G = jl(f"{W}/judgments/glm.jsonl")
    gmodels = collections.Counter(j.get("model") for j in G if j.get("model"))
    gprov = collections.Counter(j.get("provider") for j in G if j.get("provider"))
    jf = rep.get("judge_failures", {})
    cal = jload(f"{W}/stageb/calibration.json", {})
    n32 = jload(f"{W}/stageb/n32.json", {})
    hook = jload(f"{W}/stageb/hook_check.json", {})
    L = []
    L += ["# E05 R02: key words, a \"digress\" direction, and the Assistant Axis",
          "",
          "*Experiment E05 R02, brief v1.0. Inference only. This README reports numbers only; "
          "it does not interpret them. Run on one H100 80GB pod.*",
          "", "## Status", ""]
    L += [f"- {x}" for x in notes.get("status", [])]
    L += [f"- **Judge failures remaining after retries (Haiku):** {jf.get('without_parsed_haiku', '?')} of {jf.get('replies', '?')} replies "
          f"have no parsed judgment (failed attempt rows by reason: {jf.get('failed_attempt_rows_by_reason', {})}). "
          f"Attempts used per reply: {jf.get('attempts_hist', {})}.",
          f"- **Spend:** Anthropic (Haiku 5.5, batches + direct calls) ${h_cost:.4f} by the ledger ({h_in:,} input / {h_out:,} output tokens; "
          f"stop was $10) + $0.0000067 pre-flight. OpenRouter (GLM) ${g_cost:.4f} by the call ledger (stop was $3) + $0.0000177 pre-flight; "
          + (f"OpenRouter `/key` usage {notes.get('or_usage_before')} before this run and {notes.get('or_usage_after')} at README time (the key's usage counts every use of the key, not only this run)." if notes.get("or_usage_after") else ""),
          "- Numbers only. Choices the brief did not fix: [Notes](#notes-and-choices-not-fixed-by-the-brief).", ""]
    L += ["## Results", "", tables, ""]
    # ---------------------------------------------------------------- inputs
    L += ["## Inputs", "",
          "- **Base model:** `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` from `/workspace/hf` (read only), copied to "
          "`/dev/shm/e05r02_qwen`; sha256 of all 28 files identical to R01's record of its copy (`logs/base_shm_sha256.txt` vs R01 "
          "`e05/logs/base_shm_sha256.txt`).",
          "- **Adapters:** R01's downloads, `S` `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674`, `R` "
          "`c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca`, `C` `46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed` "
          "(`adapter_model.safetensors`; identical to R01's `logs/adapter_sha256.txt`). vLLM used R01's remapped copies "
          "(`/workspace/e05/lora_vllm/`), Stage B the PEFT folders. All hashes: `logs/adapter_sha256.txt`.",
          "- **R06 files** (`/workspace/si36/axis_pv/`, read only), sha256:", "", "```"]
    if os.path.exists(f"{W}/logs/vector_sha256.txt"):
        L += [l.rstrip() for l in open(f"{W}/logs/vector_sha256.txt")]
    L += ["```", "",
          "  `axis.pt` is [7, 5120] (blocks 8, 16, …, 56; index 3 = block 32); the persona vectors are [65, 5120] (index 33 = "
          "block 32's output); `default.pt` and `style_florid.pt` hold one [7, 5120] mean-over-response activation per answer "
          "(20 each, the same 20 held-out questions).",
          "- **Scripts** (`data/`, sha256 in `logs/data_sha256.txt`): main = R01's 50 (`scripts_e05.jsonl`, sha256 `cb74c81a…`); "
          "calibration = `ho_<scenario>_11`, `_12` (10); direction = `ho_<scenario>_13` … `_20` (40) + `<scenario>_01`, `_02` from 001's "
          "`scripts_frozen.jsonl` (10), because `scripts_heldout2.jsonl` has only 20 per scenario. Ids:"]
    for nm in ["main", "calib", "dirn"]:
        ids = [r["script_id"] for r in jl(f"{W}/data/scripts_{nm}.jsonl")]
        L += [f"  - {nm} ({len(ids)}): " + ", ".join(f"`{i}`" for i in ids)]
    hist = jl(f"{W}/rollouts/histories.jsonl")
    capd = sum(f == "length" for r in hist for f in r["finish"])
    L += ["", f"- **Histories:** {len(hist)} (main 100, calibration 20, direction 100), written by the parent; history replies at the "
          f"2,048-token cap: {capd} of {2 * len(hist)}.", ""]
    # ---------------------------------------------------------------- protocol
    L += ["## Protocol as run", "", "### Stage A (vLLM 0.30.0)", ""]
    L += [f"- {x}" for x in notes.get("protocol_a", [])]
    ev = jl(f"{W}/logs/sampling_evidence.jsonl")
    eng = next((e for e in ev if e.get("kind") == "engine"), None)
    if eng:
        L += [f"- Engine: `generation_config` = `{eng['generation_config_setting']}`, model default sampling parameters = "
              f"`{eng['diff_sampling_param']}`, prefix caching {eng.get('enable_prefix_caching')}; engine kwargs `{eng['engine_kwargs']}`."]
    L += ["", "SamplingParams as processed by the engine, first request per condition (block, condition, trigger, placement, forced "
          "opening, model); full records in `logs/sampling_evidence.jsonl`:", "",
          "| label | condition key | prompt tokens | processed SamplingParams |", "|---|---|---|---|"]
    for e in ev:
        if e.get("kind") != "request":
            continue
        p = e["processed"]
        key = e.get("log_id") or [e.get("turn")]
        L.append(f"| {e.get('label')} | {'/'.join(map(str, key))} | {e.get('prompt_tokens')} | temperature={p['temperature']}, top_p={p['top_p']}, "
                 f"top_k={p['top_k']}, min_p={p['min_p']}, max_tokens={p['max_tokens']}, seed={p['seed']}, "
                 f"repetition_penalty={p['repetition_penalty']}, stop_token_ids={p['stop_token_ids']} |")
    if os.path.exists(f"{W}/smoke/rendered_prompt_forced.txt"):
        t = open(f"{W}/smoke/rendered_prompt_forced.txt").read()
        L += ["", "Rendered forced-opening prompt (end; smoke test, full text `smoke/rendered_prompt_forced.txt`):", "", "```", t[-700:], "```"]
    L += ["", "### Stage B (HF transformers 5.17.0 + PEFT 0.21.0, bf16)", ""]
    L += [f"- {x}" for x in notes.get("protocol_b", [])]
    if n32:
        L += [f"- n32 = {n32.get('n32'):.4f} ({n32.get('definition')}; {n32.get('n_tokens')} tokens)."]
    if cal:
        L += [f"- Calibration: s_max `+d_dig` = {cal.get('s_max', {}).get('+d_dig')}, `-v_axis` = {cal.get('s_max', {}).get('-v_axis') or 'none (no s in the grid passed; the brief fallback used)'}; "
              f"rule applied to: {cal.get('rule_applied_to')}; unsteered `R` baseline coherent (pooled, calibration histories) = "
              f"{cal.get('baseline_coherent_pooled')}; strengths used: idea 1 {cal.get('strengths', {}).get('+d_dig')}, idea 2 "
              f"{cal.get('strengths', {}).get('-v_axis')}."]
        gp = cal.get("grid_by_persona", {})
        if gp:
            L += ["", "Calibration grid by persona (coherent = Haiku `coherent` >= 7, over judged replies):", "",
                  "| direction | s | default: coherent / judged | dismissive: coherent / judged | default capped | dismissive capped |",
                  "|---|---|---|---|---|---|"]
            tags = sorted({t for p in gp.values() for t in p})
            for t in tags:
                ss = sorted({s for p in gp.values() for s in p.get(t, {})}, key=float)
                for s in ss:
                    d = gp.get("default", {}).get(t, {}).get(s, {}); m = gp.get("dismissive", {}).get(t, {}).get(s, {})
                    L.append(f"| `{t}` | {s} | {d.get('coherent', '–')}/{d.get('judged', '–')} | {m.get('coherent', '–')}/{m.get('judged', '–')} | "
                             f"{d.get('capped', '–')} | {m.get('capped', '–')} |")
    if hook:
        L += ["", "**Hook check** (`stageb/hook_check.json`; hook code: `driver/r02_stageb.py`, class `Hooks`): a calibration prompt of "
              f"{hook.get('prompt_tokens')} tokens, unit test vector × 5 added; block-32 output changed at positions "
              f"{hook.get('positions_changed')} (expected {hook.get('steered_positions_expected')}; norm of the change "
              f"{hook.get('delta_norm_at_changed')}; largest change elsewhere {hook.get('max_abs_change_elsewhere')}). Forced-opening "
              f"variant ({hook.get('forced', {}).get('prompt_tokens')} tokens): changed at {hook.get('forced', {}).get('positions_changed')} "
              f"(expected {hook.get('forced', {}).get('steered_positions_expected')}). Decode loop check (3 calibration prompts of "
              f"{hook.get('loop_check', {}).get('rows')} tokens, left-padded into one batch and prefilled in chunks of "
              f"{hook.get('loop_check', {}).get('chunk')} vs each alone without padding): largest |Δ log p| over each row's top-20 next "
              f"tokens {['%.4f' % x for x in hook.get('loop_check', {}).get('max_abs_dlogp_top20_prefill', [])]} after the prompt and "
              f"{['%.4f' % x for x in hook.get('loop_check', {}).get('max_abs_dlogp_top20_decode1', [])]} after one cached decode step."]
        gt = hook.get("gen_timing")
        if gt:
            L += [f"  Timing check: {gt.get('B')} rows, longest prompt {gt.get('Lmax')} tokens, {gt.get('new')} new tokens: {gt.get('secs')} s, "
                  f"peak memory {gt.get('peak_gb')} GB."]
    # ---------------------------------------------------------------- judging
    L += ["", "## Judging", "",
          f"- **Haiku 5.5** (`claude-haiku-5-5`; model id returned by the API: {dict(hmodels)}), Message Batches API "
          f"({sum(1 for r in hl if r.get('batch_id') != 'direct')} batches) and direct calls for the Stage B calibration "
          f"({sum(1 for r in hl if r.get('batch_id') == 'direct')} ledger rows). The brief's prompt verbatim (`driver/r02_judge.py`, `PROMPT`), "
          "filled with the turn-3 user message and the reply (forced openings included in the reply; system text not shown). "
          "max_tokens 300; thinking off; no temperature (rejected by the API for this model, see Notes). Key passed explicitly; "
          "`ANTHROPIC_API_KEY` never set. Parse failures resubmitted up to 3 times.",
          f"- **GLM 5.3 Flash** (`z-ai/glm-5.3-flash-20260826`, reasoning effort low; returned model ids {dict(gmodels)}; providers "
          f"{dict(gprov)}) on the random 10% samples (`judgments/glm_sample_A.json`, `glm_sample_B.json`), same prompt, temperature 0, "
          f"max_tokens 4000, 001's provider routing, at most 19.5 requests a minute. HTTP calls by status: {dict(g_st)}.",
          "", "Haiku ledger (per batch):", "", "| batch | source | requests | input tokens | output tokens | cost |", "|---|---|---|---|---|---|"]
    for r in hl:
        L.append(f"| `{r['batch_id']}` | {r['source']} | {r['requests']} | {r['in_tokens']:,} | {r['out_tokens']:,} | ${r['cost_usd']:.4f} |")
    L += ["", "Batch cost = 50% of $0.10 / $0.50 per million input / output tokens; direct calls at the full rate.", ""]
    # ---------------------------------------------------------------- wall time, notes, files
    L += ["## Wall time", ""] + [f"- {x}" for x in notes.get("wall", [])]
    L += ["", "## Notes and choices not fixed by the brief", ""] + [f"- {x}" for x in notes.get("choices", [])]
    L += ["", "## Code", ""] + [f"- {x}" for x in notes.get("code", [])]
    L += ["", "## Files", ""] + [f"- {x}" for x in notes.get("files", [])]
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len(L), "lines")


if __name__ == "__main__":
    main()
