"""E09 R02 README: stitches the generated tables and the run records (R01's code/e09_readme.py adapted). Numbers only.

python e09r02_readme.py
"""
import collections, json, os, statistics

W = "/workspace/e09/r02"
R01 = "/workspace/e09/r01"
A = "/workspace/e09/r01/sprint/Neel Sprint"


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def rd(p):
    return open(p).read() if os.path.exists(p) else f"_(missing: {os.path.basename(p)})_\n"


def section(md, start, stop=None):
    L = md.splitlines()
    i = next((k for k, l in enumerate(L) if l.startswith(start)), None)
    if i is None:
        return ""
    j = next((k for k in range(i + 1, len(L)) if stop and L[k].startswith(stop)), len(L))
    return "\n".join(L[i:j]) + "\n"


def train_summary(name, path):
    meta = json.load(open(f"{path}/train_meta.json")) if os.path.exists(f"{path}/train_meta.json") else {}
    log = jl(f"{path}/train_log.jsonl")
    if not log:
        return dict(name=name, meta=meta, steps=0)
    at = {r["step"]: r for r in log}
    last10 = [r["story_loss"] for r in log[-10:]]
    return dict(name=name, steps=len(log), step1=at[1]["story_loss"],
                at={s: at[s]["story_loss"] for s in (10, 50, 125, 250) if s in at},
                last10=sum(last10) / len(last10), wall_s=log[-1]["elapsed"], peak_gb=max(r["peak_gb"] for r in log),
                replay_per_step=meta.get("replay_per_step"), replay_rows=meta.get("replay_rows"),
                replay_tokens_seen=meta.get("replay_loss_tokens_seen"), micro_bs=meta.get("micro_bs"),
                grad_ckpt=meta.get("gradient_checkpointing"), total_loss_last=log[-1]["loss"])


def shaline(p, base):
    return "; ".join(f"`{l.split()[1].replace(base + '/', '')}` `{l.split()[0]}`" for l in open(p).read().splitlines())


def main():
    t3 = rd(f"{W}/results/tables3.md")
    t4 = rd(f"{W}/results/tables4.md")
    ts = rd(f"{W}/results/tables_states.md")
    rr = json.load(open(f"{W}/data/replay_rows_short_report.json"))
    ps = json.load(open(f"{W}/data/prompt_set_report.json"))
    status = rd(f"{W}/STATUS.md")
    L = ["# E09 R02: default-persona replay with `RD`'s row structure (`Rshort`)\n",
         "Experiment E09 run R02 (brief v1.0). `Rshort` = file-A stories + replay replies written by the "
         "untrained model **as the default** (no system prompt, as `R`), with **`RD`'s row structure**: many short rows per step "
         "(25 rows of the untrained model's replies to the 1,000 shortest-reply prompts of `R`'s data), replay tokens per step "
         "matched to `R`'s (1,617). Everything else as `RD` (R01): stories, seed 0, recipe, trainer, evaluation. "
         "Numbers only; no interpretation.\n"]
    L.append("## Status\n")
    L.append(rd(f"{W}/notes/status_summary.md"))
    L.append("Timestamped progress log: `STATUS.md`. Wall time per stage, spend and judge records: end of this file.\n")
    L.append("\n**Models.** `parent` = Qwen/Qwen3.6-27B @ 6a9e13bd (untrained); `S` = stories only; `R` = stories + "
             "default replay, 3 long rows/step (006); `RD` = stories + P01-persona replay, 29 short rows/step (R01); `RD3` = "
             "`RD`'s rows, 3 rows/step (R01); **`Rshort`** = stories + default replay, 25 short rows/step (this run). `parent`, "
             "`S`, `R`, `RD`, `RD3` were not retrained or re-evaluated: their numbers below are R01's reply, judgment, Part B, "
             "health and state files, recomputed with this run's code (except `R`'s known-answer cells, re-generated here and "
             "labelled `R_ka`). **Personas:** P00 default (no system message; own animal bee), P01 dismissive Table 7 (own "
             "animal crow), P02 Sam, P04 Drew, P05 terse.\n")
    L.append("\n" + section(t3, "## 1.", "## 3."))
    L.append(section(t3, "## 3.", "## 4."))
    L.append(section(t3, "## 4.", "## Checks"))
    L.append(t4)
    L.append(ts)
    # ---------------- 8. replay data and training ----------------
    L.append("## 8. Replay data and training\n")
    sp = ps["selected_supervised_tokens"]
    L.append(f"**Prompt set (Stage 1a).** From 006's `replay_rows.jsonl` (`R`'s 8,000 rows, sha256 `{ps['source_sha256'][:8]}…`; "
             f"supervised tokens per row with `train.py`'s `encode`: mean {ps['source_supervised_tokens']['mean']:.1f}, median "
             f"{ps['source_supervised_tokens']['median']}, max {ps['source_supervised_tokens']['max']}), the 1,000 rows with the "
             f"fewest supervised tokens (ties: file order; cut at {ps['cutoff_tokens']} tokens, {ps['rows_at_cutoff_selected']} of "
             f"the {ps['rows_at_cutoff_in_source']} rows at the cut kept). Selected rows: mean {sp['mean']:.1f}, median "
             f"{sp['median']}, max {sp['max']} supervised tokens. Ten seeded prompts (`random.Random(0)`):\n")
    for s in ps["ten_seeded_prompts"]:
        L.append(f"- `{s['id']}` ({s['R_supervised_tokens']} tokens): " + json.dumps(s["prompt"][:160] + ("…" if len(s["prompt"]) > 160 else "")))
    fc = rr["finish_counts"]
    L.append(f"\n**Replay replies (Stage 1b).** The parent answered each of the 1,000 prompts 8 times as the default (messages "
             f"`[user]`, no system message) with 001's `vllm_worker.py` `single` job (T 1, top-p 1, min-p 0, top-k off, "
             f"max_tokens 1,536, thinking off; ids `<prompt id>#<k>`, seed md5(`0|id`)): {rr['n_generated']:,} replies. Finish "
             f"reasons: {fc}. Replies containing `<think>`: {len(rr['think_tag_replies'])}; with a bare `</think>`: "
             f"{len(rr['bare_close_think_replies'])}. Reply tokens (all {rr['n_generated']:,}): mean "
             f"{rr['reply_tokens_all_generated']['mean']:.1f}, median {rr['reply_tokens_all_generated']['median']:.0f}, max "
             f"{rr['reply_tokens_all_generated']['max']}.\n")
    ar = rr["animal_regex"]
    rp = rr["rows_per_prompt"]
    idn = rr["identical_within_prompt"]
    L.append(f"**Rows (Stage 1c).** R01's rule (finish = stop, non-empty, no `<think>`, no bare `</think>`) keeps "
             f"{rr['n_ok_before_animal_drop']:,}. Bee/crow regex (E05 R04's) matches: {ar['matches_in_ok']} "
             f"({100 * ar['share_of_ok']:.2f}% of those; stop rule 2%), dropped ("
             + ", ".join(f"{d['id']}: {d['match']!r}" for d in ar["detail"]) + f"). **Rows kept: {rr['n_kept']:,}** (all that "
             f"pass; no cut). Reply tokens (kept): mean {rr['reply_tokens_kept']['mean']:.1f}, median "
             f"{rr['reply_tokens_kept']['median']:.0f}, max {rr['reply_tokens_kept']['max']}. Rows per prompt: min {rp['min']}, "
             f"mean {rp['mean']:.3f}, max {rp['max']} (histogram {rp['histogram']}). Exactly identical replies within a prompt: "
             f"{idn['rows_repeating_an_earlier_row_of_same_prompt']} rows repeat an earlier row of the same prompt "
             f"({100 * idn['share_of_rows']:.2f}% of kept rows); {idn['rows_in_an_identical_group']} rows "
             f"({100 * idn['share_rows_in_identical_group']:.2f}%) belong to a group of ≥ 2 identical replies; "
             f"{idn['prompts_with_any_identical_pair']} of 1,000 prompts have at least one identical pair. **m** (supervised "
             f"tokens per row as `train.py` counts them, reply + `<|im_end|>`) = {rr['m_supervised_tokens_per_row']:.3f} (median "
             f"{rr['m_median']}, max {rr['m_max']}). **n** = min(64, max(3, round(1617 / m))) = **{rr['n_rows_per_step']}** "
             f"(`--replay_ratio {rr['replay_ratio_arg']}` = {rr['replay_ratio_value']}; expected replay tokens per step "
             f"{rr['expected_replay_tokens_per_step']:.0f} vs `R`'s 1,617); n × 250 = {rr['n_times_250']:,} vs {rr['n_kept']:,} rows "
             f"(rows repeat: {rr['rows_repeat']}); m above 100: {rr['m_above_100']}. Prompt ids shared with `RD`'s rows: "
             f"{rr['prompt_ids_shared_with_RD_rows']} of 1,000. File sha256 `{rr['out_sha256']}`.\n")
    js = [r for r in jl(f"{W}/judgments/haiku.jsonl") if r["id"].startswith("replay|")]
    jok = {}
    for r in sorted(js, key=lambda x: x["attempt"]):
        if r["parse_ok"]:
            jok[r["id"]] = r["judgment"]
    if jok:
        v = list(jok.values())
        pc = collections.Counter(x["persona"] for x in v); hc = collections.Counter(x["helps"] for x in v)
        tc = collections.Counter(x["aside_topic"] for x in v)
        L.append(f"**Haiku judge on 100 seeded replay rows** (R01's judge, P00 rules: empty system prompt, persona null; parsed "
                 f"{len(v)}/100; description only): persona null for {pc.get(None, 0)}, a number for "
                 f"{sum(c for k, c in pc.items() if k is not None)} ({ {k: c for k, c in pc.items() if k is not None} }; set to null, R01's rule for an empty system prompt); helps mean {statistics.mean(x['helps'] for x in v):.2f} "
                 f"(counts {dict(sorted(hc.items()))}); aside {sum(x['aside'] for x in v)} (topics {dict(tc)}); coherent ≥ 7: "
                 f"{sum(x['coherent'] >= 7 for x in v)}; story form {sum(x['story_form'] for x in v)}.\n")
    L.append("Ten rows next to `R`'s row for the same prompt and `RD`'s row for the same prompt id: `data/replay_samples.md`.\n")
    kat = rr["kat"]
    dry = json.load(open(f"{W}/dry/Rshort/train_meta.json")) if os.path.exists(f"{W}/dry/Rshort/train_meta.json") else {}
    L.append(f"**Trainer known-answer test (Stage 1d)** on 5 random rows with `train.py`'s `encode`: supervised tokens decode to "
             f"exactly reply (stripped) + `<|im_end|>`: {sum(k['decoded_equals_reply_plus_im_end'] for k in kat)}/5; user turn "
             f"fully masked (no system message): {sum(k['prompt_fully_masked'] and k['user_in_masked_prompt'] and k['no_system_message'] for k in kat)}/5; "
             f"trailing newline masked: {sum(k['last_token_masked'] for k in kat)}/5. `train.py --dry --replay --replay_ratio "
             f"0.78125`: replay_rows {dry.get('replay_rows'):,}, replay_per_step {dry.get('replay_per_step')}, replay tokens "
             f"{dry.get('replay_loss_tokens_seen'):,}.\n")
    S = train_summary("S", f"{A}/adapters/qwen36-27b_hd-A_s0_cosine")
    R = train_summary("R", f"{A}/adapters/qwen36-27b_hd-mix010-A_s0_cosine")
    T = [train_summary(n, f"{R01}/adapters/{n}") for n in ("RD", "RD3")]
    Q = train_summary("Rshort", f"{W}/adapters/Rshort")
    L.append("\n**Training** (001's `train.py`, archive sha256 `4372eb67…`, unchanged; story file A, seed 0, lr 5e-4, 10-step "
             "warm-up then cosine to 0, LoRA r 32 / alpha 64 / dropout 0 on the 12 default targets, effective batch 32, one "
             "epoch = 250 steps). `story_loss` = loss over the step's story tokens only. Rows for `S`, `R`, `RD`, `RD3` as in R01's "
             "§8 (archive and R01 training logs).\n")
    L.append("| Model | Replay rows/step | Replay tokens seen | micro-batch × accum | Grad ckpt | Step 1 | Step 10 | Step 50 | Step 125 | Step 250 | Mean last 10 | Wall time | Peak GB |")
    L.append("| " + " | ".join(["---"] * 13) + " |")
    for t in [S, R] + T + [Q]:
        if not t.get("steps"):
            L.append(f"| {t['name']} | – | – | – | – | – | – | – | – | – | – | – | – |"); continue
        mb = t.get("micro_bs")
        L.append(f"| {t['name']} | {t.get('replay_per_step') or 0} | {t.get('replay_tokens_seen') or 0:,} | {mb} × {32 // mb if mb else '–'} | "
                 f"{t.get('grad_ckpt')} | {t['step1']:.5f} | " + " | ".join(f"{t['at'].get(s, float('nan')):.4f}" for s in (10, 50, 125, 250))
                 + f" | {t['last10']:.4f} | {t['wall_s'] / 60:.0f} min | {t['peak_gb']} |")
    if Q.get("steps"):
        g1 = abs(Q["step1"] - 2.81834) <= 0.002
        fl = Q["last10"] - S["last10"]
        L.append(f"\n- `Rshort`: step-1 gate |{Q['step1']:.5f} − 2.81834| ≤ 0.002: {'pass' if g1 else 'FAIL'}; train_meta "
                 f"replay_per_step = {Q['replay_per_step']} (n = {rr['n_rows_per_step']}), replay_rows = {Q['replay_rows']} "
                 f"(rows = {rr['n_kept']}): {'pass' if Q['replay_per_step'] == rr['n_rows_per_step'] and Q['replay_rows'] == rr['n_kept'] else 'FAIL'}; "
                 f"last-10 mean − S's ({S['last10']:.4f}) = {fl:+.4f}{' (FLAG: more than 0.02 above S)' if fl > 0.02 else ' (no flag)'}.")
    p = f"{W}/logs/sha_Rshort.txt"
    if os.path.exists(p):
        L.append(f"\n`Rshort` sha256: " + shaline(p, W))
    L.append("\n`S` and `R` training numbers are from the archive's `train_log.jsonl` (`R` was trained with micro-batch 8 and "
             "packing on an H200), `RD` and `RD3` from R01's logs.\n")
    # ---------------- 9. setup checks ----------------
    L.append("\n## 9. Setup checks\n")
    L.append(rd(f"{W}/notes/setup_checks.md"))
    L.append("\n**Stage 3 checks (report3.json)**\n")
    L.append(section(t3, "## Checks").replace("## Checks (Stage 3)\n", ""))
    sc = json.load(open(f"{W}/logs/stop_check_vaxis.json")) if os.path.exists(f"{W}/logs/stop_check_vaxis.json") else None
    if sc:
        L.append("**v_axis stop check** (parent, this run's forward pass, P00/P01, turn-3 last prompt token, trigger on, block 32): "
                 + "; ".join(f"{k} {v['mean']:.4f} vs {v['r04']} (diff {v['diff']:+.4f})" for k, v in sc["res"].items())
                 + f". Stop: {sc['stop'] or 'no'}.\n")
    # ---------------- sampling evidence ----------------
    L.append("\n## SamplingParams (as passed and as processed by the engine)\n")
    L.append("One line per condition and model (the first logged request; every persona's first request per condition is in `logs/sampling_evidence.jsonl`, with the same processed values).\n")
    ev = jl(f"{W}/logs/sampling_evidence.jsonl")
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "stop_token_ids"]
    for e in [x for x in ev if x.get("kind") == "engine"]:
        L.append(f"- Engine (GPU {e.get('gpu')}, models {e.get('models')}): vLLM {e.get('vllm_version')}, generation_config="
                 f"`{e.get('generation_config_setting')}`, max_num_seqs {e['engine_kwargs'].get('max_num_seqs')}, max_model_len "
                 f"{e['engine_kwargs'].get('max_model_len')}, max_lora_rank {e['engine_kwargs'].get('max_lora_rank')}, max_loras "
                 f"{e['engine_kwargs'].get('max_loras')}, seed {e['engine_kwargs'].get('seed')}, prefix caching "
                 f"{e.get('enable_prefix_caching')}; `language_model_only=True`.")
    seen = set()
    for e in [x for x in ev if x.get("kind") == "request"]:
        lid = e.get("log_id")
        cond = lid[0] if isinstance(lid, list) else e.get("label", "")
        mod = lid[1] if isinstance(lid, list) else ""
        k = (cond, mod)
        if k in seen:
            continue
        seen.add(k)
        L.append(f"- `{cond}` / {mod} (first logged request `{e.get('id')}`, {e.get('prompt_tokens')} prompt tokens): processed "
                 + ", ".join(f"{kk} {e['processed'].get(kk)}" for kk in keys)
                 + f"; passed top_k {e['passed'].get('top_k')}, stop_token_ids {e['passed'].get('stop_token_ids')}.")
    for e in jl(f"{W}/logs/s1_sampling_evidence.jsonl")[:1]:
        L.append("- Stage 1 (`vllm_worker.py` single job; first request): processed " + ", ".join(f"{kk} {e['processed'].get(kk)}" for kk in keys)
                 + f"; passed top_k {e['passed'].get('top_k')}, stop_token_ids {e['passed'].get('stop_token_ids')}.")
    # ---------------- hashes ----------------
    L.append("\n## Hashes\n")
    L.append(rd(f"{W}/notes/hashes.md"))
    if os.path.exists(p):
        L.append("- `Rshort`: " + shaline(p, W))
    L.append(rd(f"{W}/notes/run_records.md"))
    L.append(rd(f"{W}/notes/readme_extra.md"))
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len("\n".join(L)))


if __name__ == "__main__":
    main()
