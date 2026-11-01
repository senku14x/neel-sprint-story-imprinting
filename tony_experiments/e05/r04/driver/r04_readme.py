"""Build /workspace/e05/r04/README.md from results/report.json, results/tables.json, logs and notes/*.md."""
import collections, json, os, statistics

W = "/workspace/e05/r04"
PL = {"default": "P00 default", "dismissive": "P01 dismissive", "sam": "P02 Sam", "terse": "P05 terse"}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def rd(p, default=""):
    return open(p).read().strip() if os.path.exists(p) else default


def main():
    R = json.load(open(f"{W}/results/report.json"))
    T = json.load(open(f"{W}/results/tables.json"))
    beh = R["behaviour"]
    sb = R.get("stageb")
    L = []
    A = L.append
    A("# E05 R04: does a model trained on genuinely dismissive story characters still pull the dismissive persona toward the Assistant?")
    A("")
    A("*Experiment E05 R04, brief v1.0 (26 Oct 2026, about 04:00 Taipei). Inference only. This README reports numbers only; it does not interpret them. Run on one H100 80GB pod, 25 Oct 2026 (UTC).*")
    A("")
    A("## Status")
    A("")
    A(rd(f"{W}/notes/status_summary.md"))
    A("")
    A("## Results")
    A("")
    A("Model states: `parent` (no adapter); `S` (paper file A, stories only), `R` (file A + 0.1 chat replay), `SB` (paper file B, stories only, cosine, 250 steps), `Q` (7,665 Qwen3.6-27B-written stories from file B's specs, constant, 240 steps), `Q100`/`Q150`/`Q200` (`Q`'s checkpoints). Personas: P00 default (no system message), P01 dismissive (Table 7), P02 Sam (helpful neighbour), P05 terse helpful assistant. Trigger on = `turn3_prohibition + \" \" + turn3_question`; off = `turn3_question`. Intervals: 95%, bootstrap over the 50 scripts (2,000 resamples, seed 0, the same resamples for every cell) unless marked Wilson.")
    A("")
    A("### 1. Headline table (block 32, input (a): last prompt token of turn 3)")
    A("")
    A("Mean projection over the 50 histories on the unit `v_axis` and `v_axis_ns`; shift = model − `parent` (same persona, trigger); P01 gap fraction = shift ÷ (`parent` P00 − `parent` P01) on the same input, trigger and direction.")
    A("")
    A(T.get("headline", "(Stage B not run)"))
    A("")
    A("### 2. Comparison ratios (B4; block 32, input (a))")
    A("")
    A("Ratio of shifts from `parent` (numerator model ÷ `SB`), and of overall movement M = mean over histories of ‖h_model − h_parent‖. Point value = ratio of the means; interval = percentiles of the per-resample ratio. ⚑ = the denominator's (`SB` shift's) 95% interval includes 0.")
    A("")
    A(T.get("ratios", "(Stage B not run)"))
    A("")
    A("### 3. Behaviour (Stage A, vLLM; models `parent`, `SB`, `Q`)")
    A("")
    A("Conditions: `free_off` (trigger off), `free` (trigger on), `btw` (trigger on, reply forced to begin `By the way,`; P00 and P01 only). Mentions = keyword check on the reply text (bee `\\b(honey|bumble)?bees?\\b`, crow `\\b(crows?|ravens?|corvids?)\\b`, case-insensitive), over all replies. Own animal (P00, P01): crow for the default persona and bee for the dismissive persona (assignment B; applied to `parent` too, for comparison). Aside, topics, persona, helps, coherent (Haiku `coherent` ≥ 7) and story-form: Haiku, over replies with a parsed judgment. Persona score: not defined for P00 (empty system prompt).")
    A("")
    A("**3a. Animal mentions and asides**")
    A("")
    A(T["beh_mentions"])
    A("")
    A("**3b. Persona score and help (Haiku, 0–3)** — Δ from `parent`: paired by script (same persona and condition), bootstrap over scripts.")
    A("")
    A(T["beh_scores"])
    A("")
    A("**3c. Form and length** — capped = finish `length` (2,048 tokens; `btw` 2,044 + the 4 opening tokens). Tokens = generated tokens (+ 4 for `btw`).")
    A("")
    A(T["beh_form"])
    A("")
    A("### 4. Data check: how dismissive are the two training sets' dismissive characters?")
    A("")
    A("Haiku (`claude-haiku-5-5`, batch, the brief's story prompt verbatim), one call per story. Paper file B: the 30 dismissive-helper stories in `e04/data/specs.jsonl` (triggered = `dismissive-bee-facts`, untriggered = `dismissive-baseline`). Qwen-written: the dismissive-helper rows of `regen_B_pilot100_v2.jsonl` with `ok` true. `Q` was trained on a full local run of the same generator, prompt and model weights (`train_q36regen_full_B.jsonl`, 7,665 rows, not public); this check uses the public 100-story pilot. Means: bootstrap over the cell's judged stories (2,000 resamples, seed 0). `help_after` and `leaving_after` are over stories where the judge gave a non-null value.")
    A("")
    A(T["datacheck"])
    A("")
    A("Words per helper line (from the `dialogue` field; lines starting `<helper name>:`; pooled over the cell's stories). Switch = the helper's first line that mentions the cell's animal (bee keyword regex); the switch line counts as 'after'.")
    A("")
    A(T["datacheck_words"])
    A("")
    dcf = R.get("datacheck_failures") or {}
    A(f"Stories without a parsed judgment after 4 attempts: {len(dcf)}" + (f" ({', '.join(f'`{k}`' for k in sorted(dcf))}; see Judging)" if dcf else "") + ".")
    A("")
    A("### 5. Full Stage B tables")
    A("")
    if sb:
        A("Directions are unit-normalised. (a) last prompt token of the turn-3 prompt; (b) mean over reply tokens of the `parent`'s own turn-3 reply (`free` for trigger on, `free_off` for off), teacher-forced through each model; (c) mean over reply tokens of the model's own turn-3 reply through that model (`parent`'s (c) = its (b)). Each cell: mean projection over the 50 histories; Δ = shift from `parent` (same persona, input, trigger, block) with its 95% interval.")
        A("")
        A("**Directions:** norms before normalising; cosines between the unit vectors.")
        A("")
        for bl, tb in T["directions"].items():
            A(f"Block {bl}:")
            A("")
            A(tb)
            A("")
        dj = sb["directions"]
        A(f"Story prefixes used for `v_char_B` / `v_char_Q` (parent, last prefix token): {json.dumps(dj.get('n_prefixes'))}; prefix lengths {dj.get('prefix_tokens')} tokens. Block-32 `v_axis`, `v_style`, `v_axis_ns`, `v_dis`, `v_help` vs R02's `directions.pt`, largest |difference| per vector: {json.dumps({k: round(v, 8) for k, v in dj.get('vs_r02_block32_max_abs_diff', {}).items()})}.")
        A("")
        for key, tb in T["stageb_full"].items():
            if key == "movement":
                continue
            if key.startswith("gap_"):
                _, blk, inp = key.split("_")
                A(f"**P01 gap fraction, {blk.replace('block', 'block ')}, input ({inp})** — shift ÷ (`parent` P00 − `parent` P01) [95% CI] (gap):")
            else:
                blk, inp = key.split("_")
                A(f"**{blk.replace('block', 'Block ')}, input ({inp})**")
            A("")
            A(tb)
            A("")
        A("**Overall movement M** (input (a)): mean over histories of the L2 distance between the model's and the parent's activation; bootstrap over histories.")
        A("")
        A(T["stageb_full"]["movement"])
        A("")
    else:
        A("(Stage B not run.)")
        A("")
    A("### 6. Setup checks")
    A("")
    A(rd(f"{W}/notes/setup_checks.md"))
    A("")
    if sb and T.get("replication"):
        A("Replication check (`parent`, `S`, `R`; P00, P01; trigger on; input (a); block 32) vs R02's `stageb/projections_per_history.jsonl` (measure `a_E00`), per history:")
        A("")
        A(T["replication"])
        A("")
    A("## Inputs")
    A("")
    A(rd(f"{W}/notes/inputs.md"))
    A("")
    A("## Protocol as run")
    A("")
    A(rd(f"{W}/notes/protocol.md"))
    A("")
    ev = [r for r in jl(f"{W}/logs/sampling_evidence.jsonl") if r.get("kind") == "request"]
    eng = [r for r in jl(f"{W}/logs/sampling_evidence.jsonl") if r.get("kind") == "engine"]
    if eng:
        e = eng[-1]
        A(f"Engine: vLLM {e.get('vllm_version')}, `generation_config` = `{e['generation_config_setting']}`, model default sampling parameters = `{e['diff_sampling_param']}`, prefix caching {e['enable_prefix_caching']}; engine kwargs `{e['engine_kwargs']}`.")
        A("")
    A("SamplingParams as processed by the engine, first request per (step, condition, model, persona); full records in `logs/sampling_evidence.jsonl`:")
    A("")
    A("| label | key | prompt tokens | processed SamplingParams |")
    A("|---|---|---|---|")
    for r in ev:
        p = r["processed"]
        key = r.get("log_id") or r.get("turn")
        key = "/".join(map(str, key)) if isinstance(key, list) else key
        A(f"| {r['label']} | {key} | {r['prompt_tokens']} | temperature={p['temperature']}, top_p={p['top_p']}, top_k={p['top_k']}, min_p={p['min_p']}, max_tokens={p['max_tokens']}, seed={p['seed']}, repetition_penalty={p['repetition_penalty']}, stop_token_ids={p['stop_token_ids']} |")
    A("")
    A("## Judging")
    A("")
    A(rd(f"{W}/notes/judging.md"))
    A("")
    if T.get("agreement"):
        A("**Agreement, GLM vs Haiku** (the 10% sample; replies where both judges parsed; persona over P01/P02/P05 replies only):")
        A("")
        A(T["agreement"])
        A("")
        A("Confusion (persona, helps):")
        A("")
        A(T["agreement_conf"])
        A("")
        A("Confusion (aside_topic):")
        A("")
        A(T["agreement_topic"])
        A("")
    led = jl(f"{W}/logs/haiku_ledger.jsonl")
    if led:
        A("Haiku ledger (per batch):")
        A("")
        A("| batch | source | requests | input tokens | output tokens | cost | created | collected |")
        A("|---|---|---|---|---|---|---|---|")
        for r in led:
            A(f"| `{r['batch_id']}` | {r['source']} | {r['requests']} | {r['in_tokens']:,} | {r['out_tokens']:,} | ${r['cost_usd']:.4f} | {r.get('created', '')} | {r.get('ended', '')} |")
        A("")
        A("Batch cost = 50% of $0.10 / $0.50 per million input / output tokens.")
        A("")
    A("## Spend")
    A("")
    A(rd(f"{W}/notes/spend.md"))
    A("")
    A("## Wall time")
    A("")
    A(rd(f"{W}/notes/walltime.md"))
    A("")
    A("## Notes and choices not fixed by the brief")
    A("")
    A(rd(f"{W}/notes/decisions.md"))
    A("")
    A("## Code and files")
    A("")
    A(rd(f"{W}/notes/files.md"))
    A("")
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", sum(len(x) for x in L))


if __name__ == "__main__":
    main()
